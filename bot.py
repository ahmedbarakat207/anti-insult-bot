"""
Telegram Insult Blocker Bot.
Monitors messages in Telegram groups & supergroups, detects insults across
English, Modern Standard Arabic, Egyptian Arabic, and Franco-Arab,
and automatically deletes offending messages, issues warnings, and mutes repeat offenders.
"""

import asyncio
import html
import logging
from datetime import datetime, timedelta, timezone

import os

from telegram import Update, ChatPermissions
from telegram.constants import ChatType, ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Optional rate limiter import with graceful fallback
try:
    from telegram.ext import AIORateLimiter
except ImportError:
    AIORateLimiter = None

from config import Config, validate_config
from filter import InsultDetector
from tracker import tracker

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("InsultBlockerBot")

# Initialize profanity detection engine
detector = InsultDetector()


async def auto_delete_message(message, delay_seconds: int):
    """Asynchronously deletes a bot warning message after a delay to keep chat clean."""
    if delay_seconds <= 0:
        return
    await asyncio.sleep(delay_seconds)
    try:
        await message.delete()
    except Exception:
        pass


# =========================================================================
# Command Handlers
# =========================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    chat = update.effective_chat

    welcome_text = (
        f"👋 أهلاً بك <b>{html.escape(user.first_name)}</b>!\n\n"
        f"🛡️ <b>بوت حماية المجموعات من الشتائم والألفاظ المسيئة</b>\n\n"
        f"يقوم هذا البوت بحظر وحذف أي رسائل تحتوي على شتائم أو إهانات فورياً:\n"
        f"• 🇬🇧 <b>اللغة الإنجليزية (English)</b>: الشتائم والكلمات البذيئة والحيل الحرفية (f*ck, sh!t, etc.)\n"
        f"• 🇸🇦 <b>العربية الفصحى (Standard Arabic)</b>: الشتائم والسباب والإهانات.\n"
        f"• 🇪🇬 <b>اللهجة المصرية (Egyptian Arabic)</b>: الألفاظ الدارجة وشتائم الأهل والأعراض.\n"
        f"• 📱 <b>الفرانكو (Franco / Arabizi)</b>: الشتائم المكتوبة بأرقام وحروف لاتينية (kosom, 3ars, a7a, etc.)\n\n"
        f"<b>طريقة التفعيل في المجموعات:</b>\n"
        f"1. أضف البوت إلى مجموعتك.\n"
        f"2. رقّي البوت إلى <b>مشرف (Admin)</b> مع صلاحيات:\n"
        f"   - 🗑️ <b>حذف الرسائل (Delete Messages)</b>\n"
        f"   - 🚫 <b>حظر/كتم المستخدمين (Restrict Users)</b>\n\n"
        f"💡 يمكنك تجربة فحص أي جملة هنا في المحادثة الخاصة مباشرة أو عبر أمر <code>/check</code>.\n\n"
        f"<i>Type /help to see all available commands.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = (
        "📚 <b>دليل أوامر البوت | Bot Help Guide</b>\n\n"
        "• <code>/check &lt;نص&gt;</code> - فحص جملة والتأكد مما إذا كانت مسموحة أم محظورة.\n"
        "• <code>/mywarnings</code> - معرفة عدد إنذاراتك في هذه المجموعة.\n"
        "• <code>/stats</code> - إحصائيات الرسائل المفحوصة والمحظورة في المجموعة.\n"
        "• <code>/settings</code> - عرض إعدادات الحظر والإنذارات الحالية.\n"
        "• <code>/clearwarnings @username</code> - (للمشرفين) تصفير إنذارات مستخدم معين.\n\n"
        "🔒 <b>كيف يعمل نظام العقوبات:</b>\n"
        f"• <b>المخالفة الأولى (1/{Config.BAN_STRIKE_THRESHOLD}):</b> حذف الرسالة + كتم العضو لمدة <b>{Config.MUTE_DURATION_HOURS} ساعة (يوم كامل)</b>.\n"
        f"• <b>المخالفة الثانية (2/{Config.BAN_STRIKE_THRESHOLD}):</b> حذف الرسالة + <b>حظر نهائي (Permanent Ban)</b> من المجموعة."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows users to safely test a text string using /check."""
    if not context.args:
        await update.message.reply_text(
            "ℹ️ يرجى كتابة النص المراد فحصه بعد الأمر.\nمثال: <code>/check hello world</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    text_to_check = " ".join(context.args)
    result = detector.detect(text_to_check)

    if result.is_insult:
        response = (
            f"🚨 <b>تم رصد لفظ مسيء [محظور]</b>\n\n"
            f"• <b>التصنيف:</b> {result.language}\n"
            f"• <b>الكلمة المرصودة:</b> <code>{html.escape(result.matched_word or '')}</code>\n"
            f"• <b>النسخة المشفرة:</b> <code>{html.escape(detector.censor(text_to_check))}</code>"
        )
    else:
        response = "✅ <b>نص سليم ونظيف</b> (لم يتم رصد أي ألفاظ مسيئة أو شتائم)."

    await update.message.reply_text(response, parse_mode=ParseMode.HTML)


async def mywarnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the sender's current strike count."""
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text("ℹ️ الإنذارات تُحسب فقط داخل المجموعات.")
        return

    strikes = tracker.get_strikes(chat.id, user.id)
    await update.message.reply_text(
        f"⚠️ عدد إنذاراتك الحالية في هذه المجموعة: <b>{strikes}/{Config.BAN_STRIKE_THRESHOLD}</b>",
        parse_mode=ParseMode.HTML,
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows statistics of scanned/blocked messages."""
    chat = update.effective_chat
    stats = tracker.get_stats(chat.id)

    breakdown_text = ""
    if stats.by_category:
        breakdown_text = "\n<b>تفاصيل الشتائم المحظورة:</b>\n" + "\n".join(
            f"• {cat}: {count}" for cat, count in stats.by_category.items()
        )

    text = (
        f"📊 <b>إحصائيات الحماية | Group Stats</b>\n\n"
        f"• 📨 إجمالي الرسائل المفحوصة: <b>{stats.total_scanned}</b>\n"
        f"• 🛡️ إجمالي الرسائل المحظورة: <b>{stats.total_blocked}</b>"
        f"{breakdown_text}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays current moderation settings."""
    text = (
        f"⚙️ <b>إعدادات الحماية الحالية:</b>\n\n"
        f"• <b>المخالفة الأولى:</b> كتم لمدة {Config.MUTE_DURATION_HOURS} ساعة (1 يوم كامل)\n"
        f"• <b>المخالفة الثانية:</b> حظر نهائي من المجموعة (Permanent Ban)\n"
        f"• <b>حذف رسالة التنبيه تلقائياً:</b> {Config.AUTO_DELETE_WARNING_SECONDS} ثانية\n"
        f"• <b>استثناء المشرفين:</b> {'مفعّل' if Config.EXEMPT_ADMINS else 'معطّل'}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def clearwarnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows admins to clear warnings for a user."""
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text("ℹ️ هذا الأمر مخصص للمجموعات فقط.")
        return

    # Check if caller is admin
    try:
        member = await chat.get_member(user.id)
        if member.status not in ("administrator", "creator") and user.id not in Config.SUPER_ADMINS:
            await update.message.reply_text("⛔ هذا الأمر متاح لمشرفي المجموعة فقط.")
            return
    except TelegramError:
        pass

    target_user_id = None
    target_name = "المستخدم"

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_name = target_user.first_name
    elif context.args:
        # Check if user passed user id
        arg = context.args[0].replace("@", "")
        if arg.isdigit():
            target_user_id = int(arg)

    if not target_user_id:
        await update.message.reply_text(
            "ℹ️ يرجى الرد على رسالة المستخدم أو تمرير الآيدي لتصفير إنذاراته.\n"
            "مثال: الرد على رسالته بـ <code>/clearwarnings</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    tracker.reset_strikes(chat.id, target_user_id)
    await update.message.reply_text(
        f"✅ تم تصفير إنذارات <b>{html.escape(target_name)}</b> بنجاح.",
        parse_mode=ParseMode.HTML,
    )


# =========================================================================
# Main Message Inspection & Enforcement Handler
# =========================================================================

async def message_filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inspects all incoming messages and photo/video captions for insults."""
    message = update.effective_message
    if not message:
        return

    user = update.effective_user
    chat = update.effective_chat

    # Ignore messages sent by the bot itself
    if user and user.is_bot and user.id == context.bot.id:
        return

    # Extract text from standard text or media caption
    text = message.text or message.caption or ""
    if not text:
        return

    # Track message count in chat stats
    tracker.record_scan(chat.id)

    # ----------------------------------------------------
    # Private Chat: Interactive Testing Mode
    # ----------------------------------------------------
    if chat.type == ChatType.PRIVATE:
        result = detector.detect(text)
        if result.is_insult:
            reply = (
                f"🚨 <b>تم رصد إهانة / لفظ مسيء! [محظور]</b>\n\n"
                f"• <b>اللغة / اللهجة:</b> {result.language}\n"
                f"• <b>اللفظ المرصود:</b> <code>{html.escape(result.matched_word or '')}</code>\n"
                f"• <b>تقنية الكشف:</b> <code>{result.variant_type}</code>\n\n"
                f"🛡️ لو كانت هذه الرسالة داخل مجموعة، لتم حذفها فوراً وإنذار العضو."
            )
        else:
            reply = "✅ <b>رسالة نظيفة</b> — لا تحتوي على أي شتائم أو ألفاظ مسيئة."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)
        return

    # ----------------------------------------------------
    # Group / Supergroup Mode: Strict Moderation
    # ----------------------------------------------------
    # Check admin exemption
    if Config.EXEMPT_ADMINS and user:
        try:
            member = await chat.get_member(user.id)
            if member.status in ("administrator", "creator"):
                return
        except TelegramError:
            pass

    # Run the multi-dialect detection engine
    result = detector.detect(text)
    if not result.is_insult:
        return

    # Log violation to console
    if Config.LOG_VIOLATIONS:
        logger.info(
            f"[VIOLATION] Chat: {chat.title} ({chat.id}) | "
            f"User: {user.username or user.first_name} ({user.id}) | "
            f"Dialect: {result.language} | Term: {result.matched_word}"
        )

    # 1. Attempt to delete the offensive message immediately
    delete_failed = False
    try:
        await message.delete()
    except TelegramError as e:
        delete_failed = True
        logger.warning(
            f"Could not delete message in chat {chat.id}: {e}. "
            "Ensure the bot is promoted to Admin with 'Delete Messages' permission."
        )

    # If action is delete_only, stop here
    if Config.ACTION_ON_INSULT == "delete_only":
        return

    # 2. Record strike
    user_id = user.id if user else 0
    strikes = tracker.record_violation(chat.id, user_id, result.category or "unknown")
    user_mention = user.mention_html() if user else "المستخدم"

    admin_hint = ""
    if delete_failed:
        admin_hint = "\n\n⚠️ <i>(تنبيه: لم يتمكن البوت من حذف الرسالة. يرجى التأكد من ترقية البوت لمشرف ومنحه صلاحية 'حذف الرسائل')</i>"

    # =====================================================================
    # STAGE 2: Second Offense -> PERMANENT BAN (الحظر النهائي من المجموعة)
    # =====================================================================
    if strikes >= Config.BAN_STRIKE_THRESHOLD:
        ban_successful = False
        try:
            await context.bot.ban_chat_member(
                chat_id=chat.id,
                user_id=user_id,
            )
            ban_successful = True
        except TelegramError as e:
            logger.warning(f"Could not ban user {user_id} in {chat.id}: {e}")

        if ban_successful:
            ban_text = (
                f"عييب"
            )
        else:
            ban_text = (
                f"عييب"
            )

        sent_ban_msg = await context.bot.send_message(
            chat_id=chat.id,
            text=ban_text,
            parse_mode=ParseMode.HTML,
        )

        if Config.AUTO_DELETE_WARNING_SECONDS > 0:
            asyncio.create_task(auto_delete_message(sent_ban_msg, Config.AUTO_DELETE_WARNING_SECONDS * 2))
        return

    # =====================================================================
    # STAGE 1: First Offense -> 1-DAY MUTE (كتم لمدة 24 ساعة)
    # =====================================================================
    until_date = datetime.now(timezone.utc) + timedelta(hours=Config.MUTE_DURATION_HOURS)
    mute_successful = False
    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
        mute_successful = True
    except TelegramError as e:
        logger.warning(f"Could not mute user {user_id} in {chat.id}: {e}")

    if mute_successful:
        warn_text = (
            f"عييب"
        )
    else:
        warn_text = (
            f"عييب"
        )

    try:
        sent_warning = await context.bot.send_message(
            chat_id=chat.id,
            text=warn_text,
            parse_mode=ParseMode.HTML,
        )

        if Config.AUTO_DELETE_WARNING_SECONDS > 0:
            asyncio.create_task(auto_delete_message(sent_warning, Config.AUTO_DELETE_WARNING_SECONDS))
    except TelegramError as e:
        logger.warning(f"Could not send warning message in {chat.id}: {e}")


async def start_health_server():
    """Starts a minimal HTTP server to satisfy Render/cloud port binding health checks."""
    port_str = os.getenv("PORT")
    if not port_str:
        return
    try:
        port = int(port_str)
        async def handle_request(reader, writer):
            await reader.read(256)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: 15\r\n"
                b"Connection: close\r\n\r\n"
                b"Bot is healthy!"
            )
            writer.write(response)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        await asyncio.start_server(handle_request, "0.0.0.0", port)
        logger.info(f"Health check HTTP server started on port {port}")
    except Exception as e:
        logger.warning(f"Could not start health check server on port {port_str}: {e}")


async def post_init(application: Application):
    """Called after application initializes, starts cloud health server if needed."""
    await start_health_server()


def main():
    """Starts the Telegram bot polling service."""
    if not validate_config():
        print("\n" + "=" * 65)
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is missing or not configured!")
        print("=" * 65)
        print("Please configure your bot token in the .env file:")
        print("  1. Open or copy .env.example to .env")
        print("  2. Get a bot token from Telegram's @BotFather")
        print("  3. Set TELEGRAM_BOT_TOKEN=your_token_here in .env")
        print("=" * 65 + "\n")
        return

    print("🤖 Starting Telegram Insult Blocker Bot...")
    
    # Safe rate limiter initialization (fallback gracefully if aiolimiter is missing)
    rate_limiter = None
    if AIORateLimiter is not None:
        try:
            rate_limiter = AIORateLimiter()
        except (ImportError, RuntimeError) as e:
            logger.info(f"AIORateLimiter disabled: {e}")

    builder = (
        ApplicationBuilder()
        .token(Config.BOT_TOKEN)
        .concurrent_updates(True)      # Process high-volume updates concurrently
        .connection_pool_size(16)      # Expand connection pool for speed
        .get_updates_read_timeout(60.0)# Prevent timeout disconnects during long polling
        .post_init(post_init)          # Binds to $PORT for Render/cloud deployment
    )
    if rate_limiter:
        builder.rate_limiter(rate_limiter)

    application = builder.build()

    # Register commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CommandHandler("mywarnings", mywarnings_command))
    application.add_handler(CommandHandler("clearwarnings", clearwarnings_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Register main message filter (listens to all text and media captions)
    application.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            message_filter_handler,
        )
    )

    print("🚀 Bot is running and actively monitoring messages (Press Ctrl+C to stop)...")
    # Long polling configuration:
    # timeout=45 ensures idle requests stay well under 2,000/day (fits easily in 3,000/day limit)
    # Telegram delivers new messages instantly with 0ms delay over the open socket
    application.run_polling(
        timeout=45,
        poll_interval=0.0,
        drop_pending_updates=True,
        allowed_updates=["message"],
    )


if __name__ == "__main__":
    main()
