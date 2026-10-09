"""
Egyptian Arabic (اللهجة المصرية) Insults and Vulgarity Dataset & Patterns.
Includes profanity, family curses, Egyptian slurs, and sexual vulgarities.
"""

import re
from .normalizer import AR_BOUNDARY_LEFT, AR_BOUNDARY_RIGHT

# Egyptian insults (single tokens / core vulgarities)
# NOTE: Arabic characters are normalized before matching (أ/إ -> ا, ة -> ه, etc.)
EGYPTIAN_EXACT_WORDS = {
    # Core slurs & sexual curses
    "كسمك", "كسم", "كسمكم", "كسمه", "كسمها", "كسك", "الكس",
    "شرموطه", "شرموط", "شراميط", "شرمطه",
    "متناك", "متناكه", "متناكين",
    "منيوك", "منيوكه", "منايك",
    "عرص", "معرص", "معرصين", "تعريص",
    "خول", "خولات", "خولنه",
    "احا", "احيه",
    "قحبه", "قحاب", "قحبات",
    "لبوه", "لبوات",
    "طيز", "طيزك", "طياز",
    "زبي", "زبك", "زبوب",
    "منيكه", "تنايك",

    # Character insults
    "وسخ", "وسخه", "اوساخ",
    "واطي", "واطيه",
    "نطع", "نطعنه",
    "جربوع", "جرابيع",
    "معفن", "معفنه",
    "شحات", "شحاتين",
}

# Egyptian phrases & multi-word patterns
EGYPTIAN_PATTERNS = [
    # Family curses with "كس"
    rf"{AR_BOUNDARY_LEFT}كس\s*(?:امك|اختك|اهلك|ميتينك|عيلتك|خالتك|ابوك|ابوكوا|امكو|امكوا|جدك){AR_BOUNDARY_RIGHT}",

    # "ابن الـ..." and "يا ابن الـ..." curses
    rf"{AR_BOUNDARY_LEFT}(?:يا\s*)?(?:ابن|يابن)\s*(?:المتناكه|الشرموطه|العرص|الكلب|الاحبه|الوسخه|القحبه|اللبوه|الهبله|الحرام|الفاجره|المره|الوسخه){AR_BOUNDARY_RIGHT}",

    # "يلعن ..." curses
    rf"{AR_BOUNDARY_LEFT}يلعن\s*(?:ميتينك|ميتين\s*اهلك|كسمك|ديك\s*امك|دين\s*امك|روح\s*امك|ابوك|امك|شكلك|ابو\s*شكلك|سنسفيل|اهلك){AR_BOUNDARY_RIGHT}",

    # Religious/family profanities
    rf"{AR_BOUNDARY_LEFT}(?:دين|يلعن\s*دين)\s*(?:امك|ابوك|اهلك){AR_BOUNDARY_RIGHT}",

    # Sexual acts / threat curses
    rf"{AR_BOUNDARY_LEFT}(?:انيكك|هنيكك|بنيكك|ينيكك|انيك\s*كسمك|هنيك\s*كسمك|انيك\s*طيزك|هنيك\s*طيزك|انيك\s*امك|هنيك\s*امك){AR_BOUNDARY_RIGHT}",
    rf"{AR_BOUNDARY_LEFT}(?:يمص\s*زبي|مص\s*زبي|تمص\s*زبي|لحس\s*طيزي|على\s*طيزي|في\s*طيزك){AR_BOUNDARY_RIGHT}",

    # Direct Egyptian vocative insults
    rf"{AR_BOUNDARY_LEFT}يا\s*(?:عرص|معرص|خول|شرموط|شرموطه|متناك|منيوك|وسخ|واطي|نطع|جربوع|معفن|علق|لبوه|قحبه|حمار|حيوان|كلب|ثور|بهيم){AR_BOUNDARY_RIGHT}",

    # "علق" strictly checked with context to avoid false positives with "تعليق/معلق"
    rf"{AR_BOUNDARY_LEFT}(?:يا\s*علق|علوقيه|انت\s*علق|شخص\s*علق){AR_BOUNDARY_RIGHT}",
]

# Egyptian whitelist to protect innocent words
EGYPTIAN_WHITELIST = {
    "كسكوس", "كسكسي", "انكسار", "اكتساب", "نكسه", "تعليق", "معلق", "يعلق",
    "فرصه", "فرص", "احكام", "احياء", "حاله", "صباحا", "مساء", "شحاته",
}
