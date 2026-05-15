"""
main.py

Demo runner / manual test entry point for Agent 1 — Pakistani Multilingual
Language Parser.

Tests a diverse set of real-world Pakistani service requests spanning multiple
languages, scripts, and dialects.

Usage:
    python main.py
"""

import sys
import logging

# Ensure UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
sys.stdout.reconfigure(encoding="utf-8")

from agents.language_parser import LanguageParserAgent

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# ── Diverse Pakistani multilingual service requests ────────────────────────────
SAMPLE_REQUESTS = [
    # 1. Roman Urdu + English (code-switching) — Emergency
    (
        "Roman Urdu + English  |  Emergency",
        "Bhai HELP karo!! Mere ghar mein pipe phoot gayi aur paani hi paani ho gaya hai. "
        "DHA Phase 5 Karachi mein hoon. Abhi koi plumber bhejo please, koi bhi price chalega!",
    ),

    # 2. Native Urdu script — High urgency
    (
        "Urdu (Nastaliq script)  |  High urgency",
        "مجھے فوری طور پر ایک الیکٹریشن کی ضرورت ہے۔ گھر کی بجلی کل رات سے گئی ہوئی ہے۔ "
        "میں ماڈل ٹاؤن لاہور میں رہتا ہوں۔ بجٹ دس ہزار روپے تک ہے۔",
    ),

    # 3. Punjabi (Roman) — Casual / low urgency
    (
        "Punjabi (Roman)  |  Casual",
        "Yaar koi mistry chahida hai ghar di painting layi. Gulberg Lahore vich haan. "
        "Koi jaldi nahi, next week tak ho jaye. Budget 15 hajar rupay tak theek hai.",
    ),

    # 4. Sindhi — Medium urgency
    (
        "Sindhi  |  Medium urgency",
        "مونکي گهر جي صفائي لاءِ ڪنهن ماڻهوءَ جي ضرورت آهي. "
        "حيدرآباد ۾ رهان ٿو. مهرباني ڪري ڪا پروفيشنل ٽيم موڪليو.",
    ),

    # 5. Pashto — Frustrated tone
    (
        "Pashto  |  Frustrated",
        "زما د کور د چت اوبه اوری، پلمبر راولئ، ډیر ژر. پیښور کې یم، "
        "د یوې ورځې راهیسي اوبه راځي. دا خو ډیر ستونزه ده!",
    ),

    # 6. Heavy Roman Urdu (SMS-style) — code-switching with abbreviations
    (
        "Heavy SMS-style Roman Urdu + English  |  Code-switching",
        "bhai mra ac bilkul kaam nai kr rha subah se, G-10 isb mein hoon, "
        "koi acha tech bhejo asap, genuine parts lgwane hain, budget flexible hai bs kaam thk hona chahiye",
    ),

    # 7. Balochi — Polite / formal
    (
        "Balochi  |  Polite",
        "من را یک نقاش (پینٹر) گپ دیم که خانه رنگ بکنت. "
        "کوئٹه در هستم. بودجه زیاد نیست، معقول قیمت می‌خواهم.",
    ),
]


def print_result(label: str, parsed) -> None:
    """Pretty-print a single parsed result."""
    W = 72
    print(f"\n+{'-' * W}+")
    print(f"|  {label:<{W - 2}}|")
    print(f"+{'=' * W}+")

    # Language analysis block
    print(f"|  {'LANGUAGE ANALYSIS':<{W - 2}}|")
    print(f"+{'-' * W}+")
    analysis = {
        "primary_language":        parsed.primary_language,
        "detected_languages":      parsed.detected_languages,
        "script_type":             parsed.script_type,
        "contains_code_switching": parsed.contains_code_switching,
        "regional_dialect":        parsed.regional_dialect,
        "detected_tone":           parsed.detected_tone,
        "confidence_score":        parsed.confidence_score,
    }
    for k, v in analysis.items():
        line = f"  {k:<26}: {v}"
        print(f"|  {line:<{W - 2}}|")

    print(f"+{'-' * W}+")
    print(f"|  normalized_text{' ' * (W - 18)}|")
    for chunk in _wrap(parsed.normalized_text, W - 4):
        print(f"|    {chunk:<{W - 4}}|")

    print(f"+{'-' * W}+")
    print(f"|  translated_english{' ' * (W - 20)}|")
    for chunk in _wrap(parsed.translated_english, W - 4):
        print(f"|    {chunk:<{W - 4}}|")

    # Service slots block
    print(f"+{'=' * W}+")
    print(f"|  {'SERVICE SLOTS':<{W - 2}}|")
    print(f"+{'-' * W}+")
    slots = {
        "service_type": parsed.service_type,
        "location":     parsed.location,
        "urgency":      parsed.urgency,
        "budget":       parsed.budget,
        "preferences":  parsed.preferences,
    }
    for k, v in slots.items():
        line = f"  {k:<14}: {v}"
        print(f"|  {line:<{W - 2}}|")

    print(f"+{'-' * W}+")


def _wrap(text: str, width: int) -> list[str]:
    """Simple word-wrap for terminal output."""
    if not text:
        return ["(none)"]
    words, lines, current = text.split(), [], ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def main() -> None:
    agent = LanguageParserAgent()

    print(f"\n+{'=' * 72}+")
    print(f"|{'Agent 1 -- Pakistani Multilingual Language Parser Demo':^72}|")
    print(f"+{'=' * 72}+\n")

    for label, text in SAMPLE_REQUESTS:
        print(f"\n  >> Input [{label}]")
        print(f"     {text[:100]}{'...' if len(text) > 100 else ''}")
        try:
            result = agent.run({"text": text})
            print_result(label, result["parsed_request"])
        except Exception as exc:
            print(f"     ERROR: {exc}")

    print("\n[Done] Demo complete.\n")


if __name__ == "__main__":
    main()
