"""
Text Normalization Engine for English, Arabic, Egyptian Arabic, and Franco.
Handles diacritics, tatweel, character repetitions, leetspeak, and spaced bypasses.
"""

import re
import unicodedata

# Tashkeel, Harakat, Quranic marks, Tatweel
ARABIC_DIACRITICS_REGEX = re.compile(
    r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u08D4-\u08E1\u08E3-\u08FF]'
)
TATWEEL_REGEX = re.compile(r'[\u0640]')

# Invisible, formatting, zero-width characters often used to evade filters
ZERO_WIDTH_REGEX = re.compile(r'[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]')

# Leetspeak map for English obfuscation
LEET_MAP = {
    '@': 'a',
    '4': 'a',
    '$': 's',
    '5': 's',
    '!': 'i',
    '1': 'i',
    '0': 'o',
    '3': 'e',
    '7': 't',
    '+': 't',
    '8': 'b',
}

# Regex word boundaries tailored for Arabic & Latin text
AR_BOUNDARY_LEFT = r'(?<![\w\u0600-\u06FF])'
AR_BOUNDARY_RIGHT = r'(?![\w\u0600-\u06FF])'


def remove_diacritics_and_tatweel(text: str) -> str:
    """Removes Arabic harakat, diacritics, and tatweel (kashida)."""
    text = ARABIC_DIACRITICS_REGEX.sub('', text)
    text = TATWEEL_REGEX.sub('', text)
    text = ZERO_WIDTH_REGEX.sub('', text)
    return text


def normalize_arabic_chars(text: str) -> str:
    """
    Normalizes common Arabic character variations:
    - Alef variations (أ, إ, آ, ٱ) -> ا
    - Taa marbuta (ة) -> ه
    - Yaa (ى) -> ي
    - Hamza variations (ؤ, ئ) -> ء
    """
    text = re.sub(r'[إأآاٱ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'ؤ', 'و', text)
    text = re.sub(r'ئ', 'ي', text)
    return text


def collapse_repeated_characters(text: str) -> str:
    """
    Collapses 2 or more identical consecutive characters into 1.
    e.g. 'احاااااا' -> 'احا', 'fuuuuck' -> 'fuck', 'koooossoom' -> 'kosom'
    """
    return re.sub(r'(.)\1+', r'\1', text)


def collapse_spaced_single_letters(text: str) -> str:
    """
    Detects and merges intentionally spaced or dotted single-letter words used to bypass filters.
    e.g. 'f u c k' -> 'fuck', 'ك س م ك' -> 'كسمك', 'f.u.c.k' -> 'fuck', 'ك.س.م' -> 'كسم'
    """
    # 1. Punctuation-separated single letters (e.g., 'f.u.c.k', 'f-u-c-k', 'ك.س.م.ك')
    def punct_repl(m: re.Match) -> str:
        chars = re.findall(r'[\w\u0600-\u06FF]', m.group(0))
        return ''.join(chars)

    # Match tokens like a.b.c or a-b-c
    text = re.sub(r'\b(?:[\w\u0600-\u06FF][\.\-_*~]){2,}[\w\u0600-\u06FF]\b', punct_repl, text)

    # 2. Space-separated single letters
    tokens = text.split()
    new_tokens = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and (tokens[i].isalpha() or ('\u0600' <= tokens[i] <= '\u06FF')):
            j = i
            while j < len(tokens) and len(tokens[j]) == 1 and (tokens[j].isalpha() or ('\u0600' <= tokens[j] <= '\u06FF')):
                j += 1
            if j - i >= 3:
                new_tokens.append(''.join(tokens[i:j]))
                i = j
                continue
        new_tokens.append(tokens[i])
        i += 1

    return ' '.join(new_tokens)


def apply_leetspeak_translation(text: str) -> str:
    """Converts common leetspeak characters to their alphabetical equivalents."""
    chars = []
    for ch in text:
        chars.append(LEET_MAP.get(ch, ch))
    return ''.join(chars)


def generate_normalized_variants(text: str) -> list[tuple[str, str]]:
    """
    Generates multiple normalized variants of the input text for comprehensive scanning.
    Returns a list of (variant_label, normalized_text).
    """
    variants = []

    # 1. Base clean: lowercased, no diacritics/tatweel/invisible chars, normalized arabic chars
    base = remove_diacritics_and_tatweel(text).strip()
    base_ar_norm = normalize_arabic_chars(base)
    variants.append(("base", base_ar_norm))

    # 2. Spaced single-letters collapsed
    spaced_collapsed = collapse_spaced_single_letters(base_ar_norm)
    if spaced_collapsed != base_ar_norm:
        variants.append(("spaced_collapsed", spaced_collapsed))

    # 3. Repeated characters collapsed
    repeat_collapsed = collapse_repeated_characters(base_ar_norm)
    if repeat_collapsed != base_ar_norm:
        variants.append(("repeat_collapsed", repeat_collapsed))

    # 4. Spaced collapsed + repeat collapsed
    combined = collapse_repeated_characters(spaced_collapsed)
    if combined not in (base_ar_norm, repeat_collapsed, spaced_collapsed):
        variants.append(("combined", combined))

    # 5. Leetspeak translated
    leet_converted = apply_leetspeak_translation(base_ar_norm.lower())
    if leet_converted != base_ar_norm.lower():
        variants.append(("leetspeak", leet_converted))
        leet_repeat = collapse_repeated_characters(leet_converted)
        if leet_repeat != leet_converted:
            variants.append(("leetspeak_repeat", leet_repeat))

    return variants
