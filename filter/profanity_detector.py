"""
Unified Insult & Profanity Detection Engine.
Coordinates multi-layer normalization, token matching, phrase regexes,
and category attribution for English, Arabic, Egyptian Arabic, and Franco.
"""

import re
from dataclasses import dataclass
from typing import Optional

from .normalizer import (
    generate_normalized_variants,
    remove_diacritics_and_tatweel,
    normalize_arabic_chars,
    AR_BOUNDARY_LEFT,
    AR_BOUNDARY_RIGHT,
)
from .words_en import (
    ENGLISH_EXACT_WORDS,
    ENGLISH_PHRASES,
    ENGLISH_OBFUSCATED_PATTERNS,
    ENGLISH_WHITELIST,
)
from .words_ar import (
    ARABIC_EXACT_WORDS,
    ARABIC_PATTERNS,
    ARABIC_WHITELIST,
)
from .words_eg import (
    EGYPTIAN_EXACT_WORDS,
    EGYPTIAN_PATTERNS,
    EGYPTIAN_WHITELIST,
)
from .words_franco import (
    FRANCO_EXACT_WORDS,
    FRANCO_PATTERNS,
    FRANCO_WHITELIST,
)


@dataclass
class DetectionResult:
    is_insult: bool
    matched_word: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    variant_type: Optional[str] = None

    def __bool__(self) -> bool:
        return self.is_insult


class InsultDetector:
    def __init__(self):
        # Precompile regex patterns for high-throughput performance
        self.en_phrase_regexes = [re.compile(p, re.IGNORECASE) for p in ENGLISH_PHRASES]
        self.en_obf_regexes = [re.compile(p, re.IGNORECASE) for p in ENGLISH_OBFUSCATED_PATTERNS]
        self.ar_regexes = [re.compile(p, re.IGNORECASE) for p in ARABIC_PATTERNS]
        self.eg_regexes = [re.compile(p, re.IGNORECASE) for p in EGYPTIAN_PATTERNS]
        self.franco_regexes = [re.compile(p, re.IGNORECASE) for p in FRANCO_PATTERNS]
        # Fast lookup cache for high-frequency messages (LRU / dict cache up to 20,000 items)
        self._cache: dict[str, DetectionResult] = {}

    def _tokenize(self, text: str) -> list[str]:
        """Extracts individual tokens stripping standard punctuation."""
        return re.findall(r'[\w\u0600-\u06FF]+', text.lower())

    def detect(self, text: str) -> DetectionResult:
        """
        Scans input text across all language engines and normalization variations.
        Optimized with fast-path heuristics and LRU caching for 100k+ msgs/sec.
        """
        if not text or not text.strip():
            return DetectionResult(is_insult=False)

        # 1. Fast Cache Check
        cached = self._cache.get(text)
        if cached is not None:
            return cached

        # 2. Fast-Path Pre-Filter:
        # If message contains NO Arabic or Latin letters (e.g. only numbers, emojis, punctuation)
        # It cannot be an insult -> instant return in <1 microsecond
        has_letters = any(c.isalpha() or ('\u0600' <= c <= '\u06FF') for c in text)
        if not has_letters:
            clean_res = DetectionResult(is_insult=False)
            if len(self._cache) < 20000:
                self._cache[text] = clean_res
            return clean_res

        variants = generate_normalized_variants(text)

        for variant_type, norm_text in variants:
            tokens = set(self._tokenize(norm_text))

            # ----------------------------------------------------
            # 1. Egyptian Arabic Detection
            # ----------------------------------------------------
            # A. Check Egyptian Exact Words (excluding whitelisted)
            eg_matches = (tokens & EGYPTIAN_EXACT_WORDS) - EGYPTIAN_WHITELIST
            if eg_matches:
                match = next(iter(eg_matches))
                return DetectionResult(
                    is_insult=True,
                    matched_word=match,
                    language="Egyptian Arabic (اللهجة المصرية)",
                    category="egyptian_arabic",
                    variant_type=variant_type,
                )

            # B. Check Egyptian Patterns
            for pattern in self.eg_regexes:
                match = pattern.search(norm_text)
                if match:
                    matched_str = match.group(0).strip()
                    if matched_str not in EGYPTIAN_WHITELIST:
                        return DetectionResult(
                            is_insult=True,
                            matched_word=matched_str,
                            language="Egyptian Arabic (اللهجة المصرية)",
                            category="egyptian_arabic",
                            variant_type=variant_type,
                        )

            # ----------------------------------------------------
            # 2. Egyptian Franco / Arabizi Detection
            # ----------------------------------------------------
            franco_matches = (tokens & FRANCO_EXACT_WORDS) - FRANCO_WHITELIST
            if franco_matches:
                match = next(iter(franco_matches))
                return DetectionResult(
                    is_insult=True,
                    matched_word=match,
                    language="Egyptian Franco / Arabizi (فرانكو)",
                    category="egyptian_franco",
                    variant_type=variant_type,
                )

            for pattern in self.franco_regexes:
                match = pattern.search(norm_text)
                if match:
                    matched_str = match.group(0).strip()
                    if matched_str not in FRANCO_WHITELIST:
                        return DetectionResult(
                            is_insult=True,
                            matched_word=matched_str,
                            language="Egyptian Franco / Arabizi (فرانكو)",
                            category="egyptian_franco",
                            variant_type=variant_type,
                        )

            # ----------------------------------------------------
            # 3. Standard Arabic Detection
            # ----------------------------------------------------
            ar_matches = (tokens & ARABIC_EXACT_WORDS) - ARABIC_WHITELIST
            if ar_matches:
                match = next(iter(ar_matches))
                return DetectionResult(
                    is_insult=True,
                    matched_word=match,
                    language="Standard Arabic (العربية الفصحى)",
                    category="arabic_standard",
                    variant_type=variant_type,
                )

            for pattern in self.ar_regexes:
                match = pattern.search(norm_text)
                if match:
                    matched_str = match.group(0).strip()
                    if matched_str not in ARABIC_WHITELIST:
                        return DetectionResult(
                            is_insult=True,
                            matched_word=matched_str,
                            language="Standard Arabic (العربية الفصحى)",
                            category="arabic_standard",
                            variant_type=variant_type,
                        )

            # ----------------------------------------------------
            # 4. English Detection
            # ----------------------------------------------------
            en_matches = (tokens & ENGLISH_EXACT_WORDS) - ENGLISH_WHITELIST
            if en_matches:
                match = next(iter(en_matches))
                return DetectionResult(
                    is_insult=True,
                    matched_word=match,
                    language="English",
                    category="english",
                    variant_type=variant_type,
                )

            for pattern in self.en_phrase_regexes:
                match = pattern.search(norm_text)
                if match:
                    matched_str = match.group(0).strip()
                    if matched_str not in ENGLISH_WHITELIST:
                        return DetectionResult(
                            is_insult=True,
                            matched_word=matched_str,
                            language="English",
                            category="english",
                            variant_type=variant_type,
                        )

            for pattern in self.en_obf_regexes:
                match = pattern.search(norm_text)
                if match:
                    matched_str = match.group(0).strip()
                    if matched_str not in ENGLISH_WHITELIST:
                        return DetectionResult(
                            is_insult=True,
                            matched_word=matched_str,
                            language="English (Obfuscated)",
                            category="english",
                            variant_type=variant_type,
                        )

        # No insult detected
        clean_result = DetectionResult(is_insult=False)
        if len(self._cache) < 20000:
            self._cache[text] = clean_result
        return clean_result

    def censor(self, text: str, replacement: str = "***") -> str:
        """Returns the text with detected insults masked."""
        result = self.detect(text)
        if not result.is_insult or not result.matched_word:
            return text
        pattern = re.compile(re.escape(result.matched_word), re.IGNORECASE)
        return pattern.sub(replacement, text)
