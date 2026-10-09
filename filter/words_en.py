"""
English Insults, Profanity, and Toxic Slurs Dataset & Patterns.
Includes exact words, compounds, phrases, and obfuscation regexes.
"""

import re

# Comprehensive list of English swear words, insults, and derogatory slurs
ENGLISH_EXACT_WORDS = {
    # Core profanities & variations
    "fuck", "fucker", "fucking", "fuckers", "fuckin", "fucked", "fuckface", "fuckhead",
    "motherfucker", "motherfucking", "motherfuckers", "motherfucker", "fuckoff",
    "shit", "shitty", "shitting", "shits", "shithead", "bullshit", "horseshit", "dipshit",
    "bitch", "bitches", "bitching", "bitchy", "bitchass",
    "asshole", "assholes", "asswipe", "asshat", "dumbass", "jackass", "badass", "fatass",
    "bastard", "bastards",
    "cunt", "cunts",
    "dick", "dicks", "dickhead", "dickheads",
    "cock", "cocks", "cocksucker", "cocksuckers",
    "pussy", "pussies",
    "whore", "whores", "whoring",
    "slut", "sluts", "slutty",
    "twat", "twats",
    "wanker", "wankers",
    "prick", "pricks",

    # Derogatory slurs
    "nigger", "niggers", "nigga", "niggas",
    "faggot", "faggots", "fag", "fags",
    "retard", "retarded", "retards",
    "kike", "spic", "chink",

    # Abusive / Toxic expressions
    "stfu", "gtfo", "wtf",
}

# English phrases (multi-word patterns)
ENGLISH_PHRASES = [
    r"\bfuck\s+(?:you|off|up|yourself|u)\b",
    r"\bgo\s+to\s+hell\b",
    r"\beat\s+shit\b",
    r"\bpiece\s+of\s+shit\b",
    r"\bson\s+of\s+a\s+bitch\b",
    r"\bsuck\s+(?:my\s+)?(?:dick|cock|balls|nuts)\b",
    r"\bkiss\s+my\s+ass\b",
    r"\bkill\s+yourself\b",
    r"\bdie\s+in\s+a\s+fire\b",
    r"\bshut\s+the\s+fuck\s+up\b",
    r"\bget\s+the\s+fuck\s+out\b",
    r"\byou(?:'re|\s+are)\s+(?:a\s+)?(?:bitch|cunt|whore|slut|retard|faggot|idiot|piece of shit)\b",
]

# Obfuscated English patterns (e.g. f*ck, sh!t, b*tch, a$$hole)
ENGLISH_OBFUSCATED_PATTERNS = [
    r"\bf[u\*@#!0\-_]{1,3}c?k+(?:ing|er|ers|ed)?\b",
    r"\bs[h\*#!\-_]{1,2}[i!1\*][t\*#!\-_]+\b",
    r"\bb[i!1\*][t\*#\-_]?ch(?:es)?\b",
    r"\ba[\$s]{2}h[o0]le[s]?\b",
    r"\bc[u\*#0]nt[s]?\b",
    r"\bd[i!1\*]ck(?:head)?\b",
    r"\bp[u\*#]ssy\b",
    r"\bm[o0]th[e3]rf[u\*@#!]ck[e3]r\b",
    r"\bn[i!1\*]gg[e3a\*]r?\b",
    r"\bf[a@\*]gg?[o0\*]t\b",
]

# Safe words whitelist to prevent false positives (Scunthorpe problem prevention)
ENGLISH_WHITELIST = {
    "classic", "pass", "passion", "passive", "grass", "glass", "class", "classes",
    "assume", "assumption", "asset", "assets", "assessment", "assist", "assistant",
    "cocktail", "peacock", "shuttlecock", "hancock", "hitchcock",
    "butter", "button", "buttress", "title", "hello", "bass", "mass", "compass",
    "scrap", "scraping", "canal", "banana", "analysis", "analytics", "analyst",
}
