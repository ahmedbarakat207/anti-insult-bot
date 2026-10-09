"""
Strike and Statistics Tracker for Moderation.
Tracks user warning strikes and server-wide statistics in memory.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChatStats:
    total_scanned: int = 0
    total_blocked: int = 0
    by_category: dict[str, int] = field(default_factory=lambda: defaultdict(int))


class ModerationTracker:
    def __init__(self):
        # (chat_id, user_id) -> strike count
        self._strikes: dict[tuple[int, int], int] = defaultdict(int)
        # chat_id -> ChatStats
        self._stats: dict[int, ChatStats] = defaultdict(ChatStats)

    def record_scan(self, chat_id: int):
        self._stats[chat_id].total_scanned += 1

    def record_violation(self, chat_id: int, user_id: int, category: str) -> int:
        """Increments and returns the user's strike count in this chat."""
        self._stats[chat_id].total_blocked += 1
        self._stats[chat_id].by_category[category] += 1
        self._strikes[(chat_id, user_id)] += 1
        return self._strikes[(chat_id, user_id)]

    def get_strikes(self, chat_id: int, user_id: int) -> int:
        return self._strikes.get((chat_id, user_id), 0)

    def reset_strikes(self, chat_id: int, user_id: int):
        if (chat_id, user_id) in self._strikes:
            self._strikes[(chat_id, user_id)] = 0

    def get_stats(self, chat_id: int) -> ChatStats:
        return self._stats[chat_id]


# Global tracker instance
tracker = ModerationTracker()
