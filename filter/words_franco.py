"""
Egyptian Franco / Arabizi (Egyptian Arabic written in Latin alphabet with numbers) Dataset & Patterns.
Covers digits: 3 (ع), 7 (ح), 5 (خ), 2 (ء/ق), 6 (ط).
"""

import re

# Exact Franco words
FRANCO_EXACT_WORDS = {
    # Kosom and variations (كس / كسمين)
    "kosom", "kosomak", "kosomk", "kosomm", "ksmk", "kossom", "kossomk",
    "kosomko", "kesmk", "kesomak", "kossomm", "kosomo", "kosomha",
    "kosmen", "kosmenak", "kesmen", "kosmeen", "kousom", "kousomak",
    "kos", "koss", "kosm",
    "koso5tak", "koso5tek", "kosextak",

    # Metnak
    "metnak", "metnaka", "metnakeen", "matnak", "motnak", "motnaka",
    "metnakiin", "etnakt", "tetnak",

    # Sharmouta
    "sharmouta", "sharmota", "sharmotah", "sharamit", "charmouta", "charmota",
    "shrmota", "sharmoota", "sharmot", "sharmut", "sharmotat",

    # 3ars
    "3ars", "3rs", "3arsan", "m3ars", "mo3ares", "ta3rees", "3aras",
    "3arsa", "m3arsa",

    # Khol / 5ol
    "khol", "5ol", "khwal", "5wal", "khewal", "5ewal", "khawalat",

    # Manyook
    "manyook", "mnyook", "mnyooc", "manayek", "manyouk", "manyoka",

    # A7a
    "a7a", "2a7a", "a7eeh", "a7yh", "a7aaa", "2a7aa", "a7eh",

    # Mateenak / Mayteenak (ميتين) - suffixed only to avoid false positives
    # NOTE: standalone mateen/mayteen can be a name ("Mateen") or "200", so only flag with suffix
    "mateenak", "mayteenak", "myeetenak", "metenak", "meteenak",

    # Genitals / sexual words
    "teez", "tezk", "tyzak", "teezi", "teezak", "teezha", "atyaaz",
    "zebi", "zby", "zebby", "zebk", "zobr", "zobrak",
    "neek", "nayek", "yeenik", "haneekak", "anyek", "neekak", "7aneekak", "aneek",
    "2a7ba", "qa7ba", "qahba", "2ahba", "a7ba",
    "labwa", "labwah", "labwat",
    "3ala2", "3alaq", "3al2",
    "bdan", "badan", "bdank", "bedan",
    "khara", "5ara", "kharak", "kharah",
    "fash5", "fash5ak", "hafsha5ak", "mafsho5", "mafsho5a",
    "shmal", "shemal", "shamala",
    "dayoos", "dayooth", "dayous", "2awad", "qawad",
    "3abeet", "3abita", "ahbal", "habla", "hotal",
    "mot5alef", "ghabi", "ghabeya",
    "7omar", "7omara", "kalb", "kalba", "kelab",
    "7ayawan", "hayawan", "baheem", "gamousa", "ba2ara", "5anzeer",
    "zabala", "zebal", "mo2ref", "7aqeer", "safel",
    "waty", "watey", "wateya", "wes5", "wes5a", "wesekh",
    "nat3", "garbou3", "mo3afen", "7aramy", "nasab",
    "kaddab", "say3", "sa2et", "fager", "baltagy", "mo5anas",
    "yabn", "yebn",
    "gazma",
}

# Franco phrases & multi-word patterns
FRANCO_PATTERNS = [
    # Kos omak phrases (incl. kosmen / dual form كسمين)
    r"\bkos\s*(?:omak|okhtak|2okhtak|omk|omko|omkwa|abook|abuk|ahlak|mayteenak|myeetenak|deenak)\b",
    r"\bkes\s*(?:omak|okhtak|omk|abook)\b",
    r"\bkosmen\s*(?:omak|okhtak|ahlak|abook)\b",
    r"\bkos\s*men\s*(?:omak|okhtak|ahlak|abook)\b",

    # Mateenak phrases (ميتين)
    r"\bmateen\s*(?:omak|abook|ahlak|o5tak|e3eltek)\b",
    r"\bmayteen\s*(?:omak|abook|ahlak)\b",

    # Ebn el ... / Yabn el ... / Bent el ...
    r"\b(?:ya\s*)?(?:ebn|ibn|yabn)\s*el\s*(?:kalb|kalba|sharmouta|sharmota|sharmot|metnaka|metnak|wes5a|wesxa|wesekh|a7ba|2a7ba|qahba|3ars|3rs|labwa|manyook|manyoka|haram|3abeet|3abita|ahbal|habla|zabala|gazma|kaddaba|5ol|khol|7omar|7ayawan|dayoos|2awad|mo5anas)\b",
    r"\bbent\s*el\s*(?:sharmouta|sharmota|metnaka|a7ba|2a7ba|qahba|labwa|wes5a|kalba|sa2ta|shmal)\b",

    # Omak / O5tak attribute curses
    r"\b(?:omak|o5tak|5altek|3amtek)\s*(?:metnaka|sharmouta|sharmota|a7ba|2a7ba|labwa|wes5a|habla|fagra|sa2ta|shmal)\b",

    # Yel3an / curses
    r"\byel3an\s*(?:mayteenak|myeetenak|mateenak|deen\s*omak|deeeen\s*omak|deenak|omak|o5tak|abook|abuk|ahlak|sheklak|sharafak|teezak)\b",
    r"\b(?:deen|den)\s*(?:omak|abook|ahlak)\b",

    # Vocatives
    r"\bya\s*(?:3ars|3rs|5ol|khol|sharmouta|sharmota|metnak|metnaka|manyook|wesekh|wes5a|watey|waty|safel|7omar|kalb|hayawan|7ayawan|labwa|zabala|7aqeer|qazer|negis|mal3oun|dayoos|2awad|3abeet|ahbal|mot5alef|ghabi|7aramy|nasab|kaddab|say3|sa2et|fager|baltagy|shmal|mo5anas|gamousa|ba2ara|5anzeer|gazma|fagra|momis|khara)\b",

    # Khara curses
    r"\bkhara\s*(?:3aleek|3ala\s*sheklak|3ala\s*omak|3ala\s*ahlak)\b",

    # Rooh curses
    r"\broo7\s*(?:omak|etnak|f\s*dahya)\b",

    # Sexual threats
    r"\b(?:haneek|7aneek|aneek|hafsha5)\s*(?:omak|kosomak|teezak|ekhtak|o5tak)\b",
    r"\b(?:moss|mose|e7les)\s*(?:zebi|zby)\b",
]

# Safe Franco words
FRANCO_WHITELIST = {
    "couscous", "kouskous", "salem", "shokran", "tamam", "habibi", "saba7o", "sabah",
}
