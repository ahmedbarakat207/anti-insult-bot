# 🛡️ Telegram Insult Blocker Bot

A high-performance Telegram moderation bot built with **Python 3** and `python-telegram-bot` that automatically detects, deletes, and penalizes insults across **English**, **Modern Standard Arabic (العربية الفصحى)**, and **Egyptian Arabic (اللهجة المصرية + Franco/Arabizi)**.

---

## 🌟 Key Features

- 🚫 **Multi-Dialect Coverage**:
  - **English**: Swear words, profanities, derogatory slurs, and abusive phrases.
  - **Standard Arabic (الفصحى)**: شتائم فصحى، إهانات، قذف، وألفاظ نابية.
  - **Egyptian Arabic (المصري)**: شتائم الأهل والأعراض، السباب الدارج (كسم، عرص، متناك، شرموطة، احا، خول، علق، إلخ).
  - **Egyptian Franco / Arabizi**: الشتائم المكتوبة بحروف وأرقام فرانكو (`kosom`, `3ars`, `a7a`, `metnak`, `sharmouta`, `manyook`, `5ol`, etc.).
- 🛡️ **Anti-Evasion & Bypass Defense**:
  - **Arabic Diacritics & Tatweel**: Strips Harakat (`شَـرْمُـوطَـة` -> `شرموطة`) and Tatweel/Kashida.
  - **Letter Repetition Collapse**: Handles elongated words (`احاااااااا` -> `احا`, `fuuuuuck` -> `fuck`, `عرررررص` -> `عرص`).
  - **Spaced & Dotted Words**: Catches intentionally separated letters (`f u c k`, `f.u.c.k`, `ك س م ك`, `ك.س.م.ك`).
  - **Leetspeak Obfuscation**: Detects `@`, `$`, `!`, `*`, `1`, `0` replacements (`f*ck`, `sh!t`, `b!tch`, `a$$hole`).
- 🎯 **False-Positive Guard**:
  - Built-in whitelisting prevents accidental triggers on safe words (e.g., `كسكسي` / `couscous`, `فرصة`, `تعليق`, `أحياء`, `أحكام`, `classic`, `pass`, `assistant`).
- ⚡ **Strict 2-Tier Enforcement System**:
  - **Instant Deletion**: Offending message or media caption is immediately deleted.
  - **1st Insult (Strike 1/2)**: The user is **muted for 1 day (24 hours)** with a firm warning that the next offense leads to a permanent ban.
  - **2nd Insult (Strike 2/2)**: The user is **permanently banned (`ban_chat_member`)** from the group.
  - **Self-Cleaning Warnings**: Warning and penalty messages auto-delete after a few seconds (default: 10s) to keep group chat history clean.
- 🧪 **Testing Tools**:
  - Command-line interactive tester (`test_cli.py`).
  - Safe in-chat testing via `/check <text>`.
  - Direct message (private chat) testing mode.

---

## 📁 Project Structure

```
├── bot.py                  # Main Telegram bot application & event handlers
├── config.py               # Environment configuration loader
├── tracker.py              # In-memory strike tracking and chat statistics
├── test_cli.py             # Interactive CLI tester for testing sentences
├── requirements.txt        # Python dependencies
├── .env.example            # Sample configuration file
├── .env                    # Active configuration file
├── filter/
│   ├── __init__.py
│   ├── normalizer.py       # Normalization engine (Harakat, Tatweel, repeats, leet, spacing)
│   ├── profanity_detector.py # Unified detection engine
│   ├── words_ar.py         # Standard Arabic insults & patterns
│   ├── words_eg.py         # Egyptian Arabic insults & patterns
│   ├── words_franco.py     # Franco Egyptian insults & patterns
│   └── words_en.py         # English insults & patterns
└── tests/
    └── test_detector.py    # 80+ automated unit tests for accuracy & false-positives
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed:
```bash
python3 --version
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Create Your Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to choose a name and username.
3. Copy the **API Token** provided by BotFather (looks like `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`).

### 4. Configure `.env`
Edit the `.env` file and insert your token:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
```

You can customize additional options in `.env`:
| Setting | Default | Description |
|---|---|---|
| `ACTION_ON_INSULT` | `delete_warn_mute` | Action on violation (`delete_warn_mute`, `delete_only`) |
| `MUTE_DURATION_HOURS` | `24` | 1st offense mute duration in hours (24 hours = 1 day) |
| `BAN_STRIKE_THRESHOLD` | `2` | Number of strikes before permanent ban |
| `AUTO_DELETE_WARNING_SECONDS` | `10` | Seconds before bot deletes its warning (0 = keep permanently) |
| `EXEMPT_ADMINS` | `true` | Whether group admins are exempt from filters |
| `LOG_VIOLATIONS` | `true` | Log violations to the console |

### 5. Run the Bot
```bash
./venv/bin/python bot.py
```

---

## 👥 Adding the Bot to a Group

1. Add your bot to your Telegram Group or Supergroup.
2. Promote the bot to **Administrator (مشرف)**.
3. Grant the following admin permissions:
   - ✅ **Delete Messages (حذف الرسائل)** *(Required)*
   - ✅ **Restrict Users / Ban Users (حظر/كتم المستخدمين)** *(Required for auto-mute)*
   - ✅ **Read All Messages / Disable Privacy Mode** (In `@BotFather`: `/setprivacy` -> Select bot -> `Disable`).

---

## 🧪 Testing the Detection Engine

### Option A: Run Automated Unit Tests (82+ Cases)
```bash
./venv/bin/pytest -o pythonpath=. tests/ -v
```

### Option B: Interactive CLI Tester
Test any text instantly in your terminal:
```bash
# Single sentence test:
./venv/bin/python test_cli.py "kosomak ya 3am"
./venv/bin/python test_cli.py "You are a fucking idiot"
./venv/bin/python test_cli.py "طبق كسكسي مغربي"

# Interactive prompt:
./venv/bin/python test_cli.py
```

### Option C: Private Chat with the Bot
Open a private chat with the bot on Telegram and send any sentence. The bot will analyze it and report whether it would be blocked and what dialect it matches.

---

## 🤖 Available Bot Commands

| Command | Permission | Description |
|---|---|---|
| `/start` | Everyone | Welcome message and setup instructions |
| `/help` | Everyone | Explanation of rules and commands |
| `/check <text>` | Everyone | Test if a specific phrase or sentence is blocked |
| `/mywarnings` | Everyone | Check your current strike count in the group |
| `/stats` | Everyone | View total messages scanned and insults blocked |
| `/settings` | Everyone | View current moderation settings |
| `/clearwarnings` | Admins Only | Reply to a user with `/clearwarnings` to reset strikes |

---

## 🛠️ Production Deployment (PM2 / Systemd)

### Using PM2 (Recommended)
```bash
npm install -g pm2
pm2 start ./venv/bin/python --name "telegram-insult-blocker" -- bot.py
pm2 save
pm2 startup
```

### Using Systemd (Linux Server)
Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Insult Blocker Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/lmao
ExecStart=/path/to/lmao/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```
