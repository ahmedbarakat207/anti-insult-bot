#!/usr/bin/env python3
"""
CLI Insult Detector Tester.
Quickly test phrases or sentences against the detector in real-time.

Usage:
    python test_cli.py "kosomak ya 3am"
    python test_cli.py "shut the fuck up"
    python test_cli.py "طبق كسكسي مغربي"
    python test_cli.py                 # (Interactive prompt mode)
"""

import sys
from filter import InsultDetector

# Terminal colors for slick output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}")
    print("================================================================")
    print("      🛡️  Telegram Insult Blocker - Detection Engine CLI        ")
    print("      Supports: English | Arabic (MSA) | Egyptian | Franco      ")
    print("================================================================")
    print(f"{RESET}")


def evaluate_text(detector: InsultDetector, text: str):
    res = detector.detect(text)
    print(f"\n{BOLD}Input Text:{RESET} \"{text}\"")
    if res.is_insult:
        print(f"{RED}{BOLD}🚨 VIOLATION DETECTED! [BLOCKED]{RESET}")
        print(f"  • {BOLD}Language / Dialect:{RESET} {YELLOW}{res.language}{RESET}")
        print(f"  • {BOLD}Matched Term:{RESET}      {RED}{res.matched_word}{RESET}")
        print(f"  • {BOLD}Detection Layer:{RESET}   {CYAN}{res.variant_type}{RESET}")
        print(f"  • {BOLD}Censored Preview:{RESET}  {detector.censor(text)}")
    else:
        print(f"{GREEN}{BOLD}✅ CLEAN / PERMITTED (No insults detected){RESET}")


def main():
    detector = InsultDetector()

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        evaluate_text(detector, text)
        print()
        return

    print_banner()
    print("Type any text to test (or 'exit' / 'quit' to stop):\n")

    while True:
        try:
            user_input = input(f"{BOLD}Enter phrase > {RESET}").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting. Have a great day!")
                break
            evaluate_text(detector, user_input)
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
