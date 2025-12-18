import re

# List of (regular expression, replacement) pairs for abbreviations in english:
abbreviations_en = [
    (re.compile("\\b%s\\." % x[0], re.IGNORECASE), x[1])
    for x in [
        ("mrs", "misess"),
        ("mr", "mister"),
        ("dr", "doctor"),
        ("st", "saint"),
        ("co", "company"),
        ("jr", "junior"),
        ("maj", "major"),
        ("gen", "general"),
        ("drs", "doctors"),
        ("rev", "reverend"),
        ("lt", "lieutenant"),
        ("hon", "honorable"),
        ("sgt", "sergeant"),
        ("capt", "captain"),
        ("esq", "esquire"),
        ("ltd", "limited"),
        ("col", "colonel"),
        ("ft", "fort"),
        ("corp", "corporation"),
        #("tts", "t t s"),
        
    ]
]

initialisms_en = [
    (
        re.compile(r"\b%s\b" % x, re.IGNORECASE),
        lambda m: " ".join(list(m.group(0).upper()))
    )
    for x in [
        # Tech / Computing
        "cpu", "gpu", "ssd", "hdd", "api", "gui", "cli", "ui", "ux", "ip", "dns", "dhcp", "ftp",
        "ssh", "http", "www", "xml", "sql", "db", "usb", 
        "ai", "asr", "tts", "stt", "ml", "dl", "vad", "ivr","llm", "rnn", "lstm", "cnn", "n2gk", "n2gk++", "nmt"

       # File formats
        "pdf", "png", "jpg", "gif", "bmp", "mp3", "aac", "mp4", "mkv",
        "ppt", "pptx", "xls", "xlsx",

        # Networking
        "url", "ip", "tcp", "udp", "tls", "ssl", "vpn", "wan", "wlan",
        "sms", "mms", "rfid", "nfc", "lte", "nr",

        # Organizations
        "un", "eu", "us", "uk", "fbi", "cia", "mit", "ucla", "usc",
        "imo", "itu",

        # Science & Engineering
        "uv", "ir", "xr", "vr", "ar", "mr", "rpm", "dna", "rna", "atm",
        "phd", "md", "bs", "ms", "ba",

        # Business / finance
        "ceo", "cfo", "cto", "coo", "hr", "pr", "kpi", "roi", "rpm", "sla",

        # Corporation & Company
        "LG", "KT", "SK", "CJ", "NH", "GS", "KB", "BM", "KBS", "MBC", "SBS", "JTBC",
        "IBK", "IBM", "AMD", "TSMC", "ARM", "HP",  "BBC", "CNN", "HBO", "ESPN",
         "IMF", "OECD", "DMT", "KSS", "KCC",

        # Others
        "CCTV", "TV"
    ]
]




additional_replacement_en = [
    # 대문자 A만 매칭
    (re.compile(r"\bA\b"), "ae"),
    # (re.compile(r"\bI\b"), "ai"),

    # wifi — 대소문자 모두 허용
    (re.compile(r"\bwifi\b", re.IGNORECASE), "why fhy"),

    # nipa
    (re.compile(r"\bnipa\b", re.IGNORECASE), "nai pa"),

    # 특수문자
    (re.compile(re.escape("-")), " "),


]


special_words_en = [
    (re.compile(re.escape(key)), value)
    for key, value in [
        ("-", " "),
        ("&", "and"),
        ("+", " plus "),
        ("%", " percent"),
        ("°C", " celsius"),
        ("°F", " fahrenheit"),
        ("°K", " kelvin"),
        ("°", " degree"),
        ("µ", " micro"),
        ("π", " pi"),
        ("Ω", " ohm"),
        ("±", " plus or minus"),
        ("×", " times"),
        ("÷", " divided by"),
        ("∞", " infinity"),
        ("→", " to"),
        ("⇄", " reversible"),
        ("ℓ", " liter"),
        ("‰", " per mille"),


    ]
]

def expand_abbreviations(text, lang="en"):
    # print("entering abbreviations")
    # print(f"text is {text}")
    if lang == "en":
        # print("yes lang is en")
        _abbreviations = abbreviations_en
    else:
        raise NotImplementedError()
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text

def expand_initialisms(text):
    for regex, func in initialisms_en:
        text = regex.sub(func, text)
    return text

def additional_replacement(text, lang="en"):
    if lang != "en":
        raise NotImplementedError()
    for regex, replacement in additional_replacement_en:
        text = re.sub(regex, replacement, text)
    return text


def expand_special_tokens(text: str, lang="en") -> str:
    """
    Replace special characters (&, -, +, / ...) into spoken English forms.
    """
    if lang != "en":
        raise NotImplementedError()

    for regex, replacement in special_words_en:
        text = regex.sub(replacement, text)

    return text


# --------------------------
# 1) Base unit mapping
# --------------------------
unit_map = {
    # Length
    "cm": "centimeter",
    "mm": "millimeter",
    "m":  "meter",
    "km": "kilometer",
    "um": "micrometer",
    "nm": "nanometer",
    "Å": "angstrom",
    "ly": "light year",
    "au": "astronomical unit",
    "pc": "parsec",

    # Time
    "s": "second",
    "ms": "millisecond",
    "us": "microsecond",
    "ns": "nanosecond",
    "min": "minute",
    "h": "hour",
    "hr": "hour",
    "day": "day",

    # Mass
    "g": "gram",
    "kg": "kilogram",
    "mg": "milligram",
    "ug": "microgram",
    "lb": "pound",
    "oz": "ounce",
    "ton": "ton",

    # Electricity / Energy
    "a": "ampere",
    "v": "volt",
    "w": "watt",
    "kw": "kilowatt",
    "j": "joule",
    "wh": "watt hour",
    "kwh": "kilowatt hour",
    "f": "farad",
    # "h": "henry",
    "ohm": "ohm",

    # Pressure
    "pa": "pascal",
    "kpa": "kilopascal",
    "mpa": "megapascal",

    # Force + Energy
    "n": "newton",
    "kn": "kilonewton",
    "kj": "kilojoule",
    "cal": "calorie",
    "kcal": "kilocalorie",

    # Volume
    "l": "liter",
    "ml": "milliliter",
    "ul": "microliter",

    # Digital Storage
    "b": "byte",
    "kb": "kilobyte",
    "mb": "megabyte",
    "gb": "gigabyte",
    "tb": "terabyte",
    "pb": "petabyte",
    "eb": "exabyte",
    "zb": "zettabyte",
    "yb": "yottabyte",

    # Special tokens
    "percent": "percent",
    "fahrenheit": "fahrenheit",
    "kelvin": "kelvin",
    "degree": "degree"
}

# --------------------------
# 2) Superscript mapping
# --------------------------
superscript_map = {
    "²": "squared",
    "³": "cubed"
}

prefix_map = {
    "²": "square",
    "³": "cubic"
}

# --------------------------
# 3) Unit expression parser
# --------------------------
def parse_unit_expression(expr: str, is_denominator=False) -> str:
    expr = expr.strip()

    # "/" — division (per)
    if "/" in expr:
        numerator, denominator = expr.split("/", 1)
        return (
            parse_unit_expression(numerator, is_denominator=False)
            + " per "
            + parse_unit_expression(denominator, is_denominator=True)
        )

    # multiplication: "·", "*"
    for sep in ["·", "*"]:
        if sep in expr:
            parts = expr.split(sep)
            return " ".join(parse_unit_expression(p, is_denominator) for p in parts)

    # superscript
    if len(expr) > 1 and expr[-1] in superscript_map:
        base = expr[:-1].lower()
        sup = expr[-1]

        # denominator: "second squared"
        if is_denominator:
            if base in unit_map:
                return f"{unit_map[base]} {superscript_map[sup]}"
            return f"{base} {superscript_map[sup]}"

        # numerator: "square meter"
        if base in unit_map:
            return f"{prefix_map[sup]} {unit_map[base]}"
        return f"{prefix_map[sup]} {base}"

    # direct lookup
    lowercase_expr = expr.lower()
    if lowercase_expr in unit_map:
        return unit_map[lowercase_expr]

    return expr


# --------------------------
# 4) Main expand function
# --------------------------
def expand_units(text: str, lang="en") -> str:
    if lang != "en":
        raise NotImplementedError()

    # e.g. "10km/h", "3 m²", "20kg·m/s²"
    unit_keys = sorted(unit_map.keys(), key=len, reverse=True)
    unit_pattern = "|".join(re.escape(k) for k in unit_keys)
    pattern = re.compile(rf"\b(\d+(?:\.\d+)?)[ ]*({unit_pattern}(?:[²³])?)\b")

    # pattern = re.compile(r"\b(\d+(?:\.\d+)?)[ ]*([a-zµ°\/\*\·²³]+)\b")

    def repl(m):
        num = m.group(1)
        unit_expr = m.group(2)
        expanded = parse_unit_expression(unit_expr)
        return f"_c{num} {expanded}"

    return pattern.sub(repl, text)

 