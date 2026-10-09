"""
Egyptian Franco / Arabizi (Egyptian Arabic written in Latin alphabet with numbers) Dataset & Patterns.
Covers digits: 3 (ع), 7 (ح), 5 (خ), 2 (ء/ق), 6 (ط).
"""

import re

# Exact Franco words
FRANCO_EXACT_WORDS = {
    # Kosom and variations
    "kosom", "kosomak", "kosomk", "kosomm", "ksmk", "kossom", "kossomk",
    "kosomko", "kesmk", "kesomak", "kossomm", "kosomo", "kosomha",

    # Metnak
    "metnak", "metnaka", "metnakeen", "matnak", "motnak", "motnaka",

    # Sharmouta
    "sharmouta", "sharmota", "sharmotah", "sharamit", "charmouta", "charmota",
    "shrmota", "sharmoota", "sharmot", "sharmut",

    # 3ars
    "3ars", "3rs", "3arsan", "m3ars", "mo3ares", "ta3rees", "3aras",

    # Khol / 5ol
    "khol", "5ol", "khwal", "5wal", "khewal", "5ewal",

    # Manyook
    "manyook", "mnyook", "mnyooc", "manayek", "manyouk",

    # A7a
    "a7a", "2a7a", "a7eeh", "a7yh", "a7aaa", "2a7aa",

    # Genitals / sexual words
    "teez", "tezk", "tyzak", "teezi", "teezak",
    "zebi", "zby", "zebby", "zebk",
    "neek", "nayek", "yeenik", "haneekak", "anyek", "neekak", "7aneekak", "aneek",
    "2a7ba", "qa7ba", "qahba", "2ahba", "a7ba",
    "labwa", "labwah",
    "3ala2", "3alaq", "3al2",
}

# Franco phrases & multi-word patterns
FRANCO_PATTERNS = [
    # Kos omak phrases
    r"\bkos\s*(?:omak|okhtak|2okhtak|omk|omko|omkwa|abook|abuk|ahlak|mayteenak|myeetenak)\b",
    r"\bkes\s*(?:omak|okhtak|omk|abook)\b",

    # Ebn el ... / Yabn el ...
    r"\b(?:ya\s*)?(?:ebn|ibn|yabn)\s*el\s*(?:kalb|sharmouta|sharmota|metnaka|wes5a|wesxa|a7ba|2a7ba|3ars|labwa|manyook|haram)\b",

    # Yel3an / curses
    r"\byel3an\s*(?:mayteenak|myeetenak|deen\s*omak|deeeen\s*omak|omak|abook|abuk|sheklak)\b",
    r"\b(?:deen|den)\s*(?:omak|abook|ahlak)\b",

    # Vocatives
    r"\bya\s*(?:3ars|3rs|5ol|khol|sharmouta|sharmota|metnak|manyook|wesekh|wes5a|watey|safel|7omar|kalb|hayawan|labwa)\b",

    # Sexual threats
    r"\b(?:haneek|7aneek|aneek)\s*(?:omak|kosomak|teezak|ekhtak)\b",
    r"\b(?:moss|mose)\s*(?:zebi|zby)\b",
]

# Safe Franco words
FRANCO_WHITELIST = {
    "couscous", "kouskous", "salem", "shokran", "tamam", "habibi", "saba7o", "sabah",
}
