#!/usr/bin/env python3
"""Make numbers in narration speakable for TTS (English, Egyptian Arabic, MSA).

Narration is spoken text: "$1,000" -> "one thousand dollars", "18%" -> "eighteen percent",
"2026-03-01" -> "March first, twenty twenty-six"; Arabic "25%" -> "خمسة وعشرين في المية" (ar-EG).
On-screen props keep digits; only narration goes through this.

Usage: speakable.py --lang en-US "Claims over $25 within 30 days"   |   echo text | speakable.py --lang ar-EG -
Python: from speakable import speakable; speakable(text, "en-US")
"""
from __future__ import annotations

import re
import sys

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen " \
       "seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth",
       "twelve": "twelfth"}
MONTHS = "January February March April May June July August September October November December".split()


def en_words(n: int) -> str:
    if n < 0:
        return "minus " + en_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return ONES[n // 100] + " hundred" + (" " + en_words(n % 100) if n % 100 else "")
    for div, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= div:
            return en_words(n // div) + " " + name + (" " + en_words(n % div) if n % div else "")
    return str(n)


def en_ordinal(n: int) -> str:
    w = en_words(n)
    last = re.split(r"[ -]", w)[-1]
    if last in ORD:
        rep = ORD[last]
    elif last.endswith("y"):
        rep = last[:-1] + "ieth"
    else:
        rep = last + "th"
    return w[: len(w) - len(last)] + rep


def en_year(y: int) -> str:
    if 2000 <= y < 2010:
        return en_words(y)
    hi, lo = divmod(y, 100)
    return en_words(hi) + " " + ("hundred" if lo == 0 else ("oh " + en_words(lo) if lo < 10 else en_words(lo)))


def en_number(s: str) -> str:
    s = s.replace(",", "")
    if "." in s:
        a, b = s.split(".", 1)
        return en_words(int(a or 0)) + " point " + " ".join(ONES[int(d)] for d in b)
    return en_words(int(s))


# ---------------------------------------------------------------- Arabic
EG = {0: "صفر", 1: "واحد", 2: "اتنين", 3: "تلاتة", 4: "أربعة", 5: "خمسة", 6: "ستة", 7: "سبعة", 8: "تمانية", 9: "تسعة",
      10: "عشرة", 11: "حداشر", 12: "اتناشر", 13: "تلاتاشر", 14: "أربعتاشر", 15: "خمستاشر", 16: "ستاشر",
      17: "سبعتاشر", 18: "تمنتاشر", 19: "تسعتاشر"}
EG_T = {2: "عشرين", 3: "تلاتين", 4: "أربعين", 5: "خمسين", 6: "ستين", 7: "سبعين", 8: "تمانين", 9: "تسعين"}
EG_H = {1: "مية", 2: "ميتين", 3: "تلتمية", 4: "ربعمية", 5: "خمسمية", 6: "ستمية", 7: "سبعمية", 8: "تمنمية", 9: "تسعمية"}
MSA = {0: "صفر", 1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة", 5: "خمسة", 6: "ستة", 7: "سبعة", 8: "ثمانية", 9: "تسعة",
       10: "عشرة", 11: "أحد عشر", 12: "اثنا عشر", 13: "ثلاثة عشر", 14: "أربعة عشر", 15: "خمسة عشر", 16: "ستة عشر",
       17: "سبعة عشر", 18: "ثمانية عشر", 19: "تسعة عشر"}
MSA_T = {2: "عشرون", 3: "ثلاثون", 4: "أربعون", 5: "خمسون", 6: "ستون", 7: "سبعون", 8: "ثمانون", 9: "تسعون"}
MSA_H = {1: "مائة", 2: "مائتان", 3: "ثلاثمائة", 4: "أربعمائة", 5: "خمسمائة", 6: "ستمائة", 7: "سبعمائة", 8: "ثمانمائة",
         9: "تسعمائة"}


def ar_words(n: int, eg: bool = True) -> str:
    units, tens, hund = (EG, EG_T, EG_H) if eg else (MSA, MSA_T, MSA_H)
    if n < 20:
        return units[n]
    if n < 100:
        return (units[n % 10] + " و" if n % 10 else "") + tens[n // 10]
    if n < 1000:
        return hund[n // 100] + (" و" + ar_words(n % 100, eg) if n % 100 else "")
    for div, one, two, few, many in ((10 ** 6, "مليون", "مليونين" if eg else "مليونان", "ملايين", "مليون"),
                                     (1000, "ألف", "ألفين" if eg else "ألفان", "آلاف" if not eg else "تلاف", "ألف")):
        if n >= div:
            q, r = divmod(n, div)
            if q == 1:
                head = one
            elif q == 2:
                head = two
            elif q <= 10:
                head = (ar_words(q, eg).replace("ة", "") if eg else ar_words(q, eg)) + " " + few
            else:
                head = ar_words(q, eg) + " " + many
            return head + (" و" + ar_words(r, eg) if r else "")
    return str(n)


def ar_number(s: str, eg: bool) -> str:
    s = s.replace(",", "").replace("٬", "")
    if "." in s:
        a, b = s.split(".", 1)
        return ar_words(int(a or 0), eg) + (" ونص" if b == "5" and eg else " فاصلة " + " ".join(ar_words(int(d), eg) for d in b))
    return ar_words(int(s), eg)


CUR_EN = {"$": "dollars", "€": "euros", "£": "pounds", "EGP": "Egyptian pounds", "USD": "US dollars", "SAR": "riyals",
          "AED": "dirhams"}
CUR_AR = {"$": "دولار", "€": "يورو", "£": "جنيه إسترليني", "EGP": "جنيه", "USD": "دولار", "SAR": "ريال", "AED": "درهم",
          "ج.م": "جنيه"}
AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"


def speakable(text: str, lang: str = "en-US") -> str:
    ar = lang.startswith("ar")
    eg = lang == "ar-EG"
    t = text.translate(AR_DIGITS)

    def num(s: str) -> str:
        return ar_number(s, eg) if ar else en_number(s)

    # ISO dates
    def date(m):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if ar:
            return f"{ar_words(d, eg)} {['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'][mo-1]} {ar_words(y, eg)}"
        return f"{MONTHS[mo - 1]} {en_ordinal(d)}, {en_year(y)}"
    t = re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", date, t)
    # currency prefix/suffix
    def cur_pre(m):
        sym, n = m.group(1), m.group(2)
        unit = (CUR_AR if ar else CUR_EN)[sym]
        if not ar and n.replace(",", "") in ("1", "1.0"):
            unit = unit.rstrip("s")
        return f"{num(n)} {unit}"
    t = re.sub(rf"(\$|€|£|EGP|USD|SAR|AED)\s?({NUM})", cur_pre, t)
    t = re.sub(rf"({NUM})\s?(EGP|USD|SAR|AED|ج\.م)", lambda m: f"{num(m.group(1))} {(CUR_AR if ar else CUR_EN)[m.group(2)]}", t)
    # percent
    pct = " في المية" if eg else (" بالمائة" if ar else " percent")
    t = re.sub(rf"({NUM})\s?%", lambda m: num(m.group(1)) + pct, t)
    # ordinals 1st 2nd
    if not ar:
        t = re.sub(r"\b(\d+)(st|nd|rd|th)\b", lambda m: en_ordinal(int(m.group(1))), t)
        # years in "in 2025" / "since 1999" style contexts
        t = re.sub(r"\b(in|since|by|from|until|of|year)\s(19\d{2}|20\d{2})\b",
                   lambda m: f"{m.group(1)} {en_year(int(m.group(2)))}", t, flags=re.I)
        t = re.sub(r"\b(\d+)-(day|hour|week|month|year|minute|step|page)\b", lambda m: f"{num(m.group(1))}-{m.group(2)}", t)
    t = re.sub(rf"(?<![A-Za-z0-9_.])(?:{NUM})(?![A-Za-z0-9_])", lambda m: num(m.group(0)), t)
    return t


def has_digits(text: str) -> bool:
    return bool(re.search(r"[0-9٠-٩]", text))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en-US", choices=["en-US", "en-GB", "ar-EG", "ar-MSA"])
    ap.add_argument("text")
    a = ap.parse_args()
    print(speakable(sys.stdin.read() if a.text == "-" else a.text, a.lang))
