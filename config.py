"""
Configuration module for Telegram Insult Blocker Bot.
Loads environment variables from .env file with safe defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the current directory or parent
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    # Telegram Bot Token (from @BotFather)
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    # Action to take when an insult is detected:
    # "delete_and_warn": Delete message + post warning
    # "delete_warn_mute": Delete message + warning + mute after max strikes
    # "delete_only": Silent deletion without warning
    ACTION_ON_INSULT: str = os.getenv("ACTION_ON_INSULT", "delete_warn_mute").strip().lower()

    # Auto-delete bot's warning message after X seconds to keep chat clean (0 to keep warning)
    AUTO_DELETE_WARNING_SECONDS: int = int(os.getenv("AUTO_DELETE_WARNING_SECONDS", "10"))

    # Penalty durations & thresholds:
    # 1st insult = Mute for 1 day (24 hours)
    # 2nd insult = Permanent ban from the group
    MUTE_DURATION_HOURS: int = int(os.getenv("MUTE_DURATION_HOURS", "24"))
    BAN_STRIKE_THRESHOLD: int = int(os.getenv("BAN_STRIKE_THRESHOLD", "2"))

    # Whether group administrators can be exempted from filters (default false)
    EXEMPT_ADMINS: bool = os.getenv("EXEMPT_ADMINS", "false").strip().lower() in ("true", "1", "yes")

    # Comma-separated list of Telegram User IDs who have super-admin privileges
    SUPER_ADMINS: list[int] = [
        int(uid.strip())
        for uid in os.getenv("SUPER_ADMINS", "").split(",")
        if uid.strip().isdigit()
    ]

    # Console logging for detected insults
    LOG_VIOLATIONS: bool = os.getenv("LOG_VIOLATIONS", "true").strip().lower() in ("true", "1", "yes")


def validate_config() -> bool:
    """Validates that essential configurations are present."""
    if not Config.BOT_TOKEN or Config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        return False
    return True
