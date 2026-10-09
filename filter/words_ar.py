"""
Modern Standard Arabic (الفصحى) Insults and Derogatory Expressions.
"""

import re
from .normalizer import AR_BOUNDARY_LEFT, AR_BOUNDARY_RIGHT

# Exact words (must be matched on word boundaries to avoid substrings in innocent words)
ARABIC_EXACT_WORDS = {
    # Sexual / Honor insults
    "عاهره", "عاهرات", "مومس", "بغي", "زانيه", "زاني", "فاسق", "فاسقه",
    "لوطي", "شاذ", "ديوث", "قواد", "قوادين", "ابن الزنا", "ابن الحرام", "لقيط",

    # Moral & Character insults
    "سافل", "سافله", "سفله",
    "حقير", "حقيره", "حقراء",
    "قذر", "قذره", "اقذار",
    "نجس", "نجسه", "انجاس",
    "لعين", "ملعون", "ملاعين",
    "خسيس", "نذل", "انذال",
    "منحط", "منحطه", "اوغاد", "وغد",
}

# Arabic phrases / Patterns
ARABIC_PATTERNS = [
    # Vocative animal insults (e.g., يا كلب, يا حمار, يا خنزير)
    rf"{AR_BOUNDARY_LEFT}يا\s*(?:كلب|حمار|خنزير|ثور|بهيم|جحش|تيس|سافل|حقير|قذر|واطي|نجس|لعين|ديوث){AR_BOUNDARY_RIGHT}",

    # Compound curses
    rf"{AR_BOUNDARY_LEFT}(?:لعنك\s*الله|الله\s*يلعنك|لعنة\s*الله\s*عليك|تبا\s*لك|سحقا\s*لك){AR_BOUNDARY_RIGHT}",
    rf"{AR_BOUNDARY_LEFT}(?:ابن\s*الزنا|ابن\s*الحرام|ابن\s*اللعينه|ابن\s*العاهره){AR_BOUNDARY_RIGHT}",
    rf"{AR_BOUNDARY_LEFT}(?:عديم\s*الشرف|فاقد\s*الشرف|بلا\s*شرف|عديم\s*الاخلاق){AR_BOUNDARY_RIGHT}",
]

# Safe Arabic words to guard against accidental match
ARABIC_WHITELIST = {
    "كلبشات", "حمارة", "خنزيرة", "تحكيم", "احكام", "حكمة", "حاكم", "محكمة",
    "سفينة", "قاد", "قيادة", "قائد", "انجاز", "نجاح",
}
