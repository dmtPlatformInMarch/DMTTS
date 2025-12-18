""" from https://github.com/keithito/tacotron """

import re
from typing import Dict

import inflect

_inflect = inflect.engine()
_comma_number_re = re.compile(r"([0-9][0-9\,]+[0-9])")
#_decimal_number_re = re.compile(r"([0-9]+\.[0-9]+)")
#_decimal_number_re = re.compile(r"(?:_y|_d)?([0-9]+\.[0-9]+)")

_decimal_number_re = re.compile(r"(?:_y|_d|_e)?([0-9]+)\.(?:_y|_d|_e)?([0-9]+)")
# _decimal_number_re = re.compile(
#     r"(?:_y|_d)?([0-9]+)\.(?:_y|_d)?([0-9]+|911|112|119|110|999)"
# )




#_currency_re = re.compile(r"(£|\$|¥)([0-9\,\.]*[0-9]+)")
_currency_re = re.compile(r"(£|\$|¥)(?:_y|_d|_e)?([0-9][0-9,\.]*)")


#_ordinal_re = re.compile(r"[0-9]+(st|nd|rd|th)")
_ordinal_re = re.compile(r"(?:_y|_d|_e)?([0-9]+)(st|nd|rd|th)")


#_number_re = re.compile(r"-?[0-9]+")
#_number_re = re.compile(r"(?:_y)?(-?[0-9]+)")
_number_re = re.compile(r"(?:_y|_d|_e|_c)?(-?[0-9]+)")


# _might_year_number_re = re.compile(r"\b\d{4}\b")
_might_year_number_re = re.compile(r"\b([12][0-9]{3})\b")
_might_digit_number_re = re.compile(r"\b\d{4,}\b")
_might_emergen_number_re = re.compile(r"\b(911|112|119)\b")
# _might_digit_number_re = re.compile(r"\b(\d{4,}|911|112|119)\b")

# _emergency_number_re = re.compile(r"\b(911|112|119|110|999)\b")

def _remove_commas(m):

    return m.group(1).replace(",", "")


# def _expand_decimal_point(m):
#     return m.group(1).replace(".", " point ")
def is_plural(word: str) -> bool:
    return _inflect.singular_noun(word) is not False

# def _expand_decimal_point(m):
#     integer, fraction = m.group(1).split(".")
#     digits = " ".join(list(fraction))   # "14" -> "1 4"
#     return f"{integer} point {digits}"

def _expand_decimal_point(m):
    # group(1): integer part (prefix 제거된 상태여야 함)
    # group(2): fractional part (prefix 제거된 상태여야 함)

    integer = m.group(1)
    fraction = m.group(2)

    # 혹시 정수부나 소수부 앞에 _y, _d 붙은 경우 제거
    integer = re.sub(r"^_(y|d|e)", "", integer)
    fraction = re.sub(r"^_(y|d|e)", "", fraction)

    # 소수부 한 자리씩 읽기
    digits = " ".join(list(fraction))

    return f"{integer} point {digits}"




def __expand_currency_orig(value: str, inflection: Dict[float, str]) -> str:
    parts = value.replace(",", "").split(".")
    if len(parts) > 2:
        return f"{value} {inflection[2]}"  # Unexpected format
    text = []
    integer = int(parts[0]) if parts[0] else 0
    if integer > 0:
        integer_unit = inflection.get(integer, inflection[2])
        text.append(f"{integer} {integer_unit}")
    fraction = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if fraction > 0:
        fraction_unit = inflection.get(fraction / 100, inflection[0.02])

        # 🔥 수정 포인트: fraction 앞에 AND 추가
        if integer > 0:
            text.append(f"and {fraction} {fraction_unit}")
        else:
            text.append(f"{fraction} {fraction_unit}")



        # text.append(f"{fraction} {fraction_unit}")
    if len(text) == 0:
        return f"zero {inflection[2]}"
    
    return " ".join(text)


def _expand_currency_orig(m: "re.Match") -> str:
    # print(f"_expand_currency")
    currencies = {
        "$": {
            0.01: "cent",
            0.02: "cents",
            1: "dollar",
            2: "dollars",
        },
        "€": {
            0.01: "cent",
            0.02: "cents",
            1: "euro",
            2: "euros",
        },
        "£": {
            0.01: "penny",
            0.02: "pence",
            1: "pound sterling",
            2: "pounds sterling",
        },
        "¥": {
            # TODO rin
            0.02: "sen",
            2: "yen",
        },
    }
    unit = m.group(1)
    currency = currencies[unit]
    value = m.group(2)
    return __expand_currency(value, currency)

def __expand_currency(raw_value: str, inflection: Dict[float, str]) -> str:
    # prefix 제거
    raw_value = re.sub(r"^_(y|d|e)", "", raw_value)

    # 숫자에서 콤마 제거
    value = raw_value.replace(",", "")

    # 정수/소수 분리
    parts = value.split(".")

    if len(parts) > 2:
        # 예외 처리 → 그냥 dollars 등으로 읽기
        return f"{raw_value} {inflection[2]}"

    text = []

    # 정수부
    integer = int(parts[0]) if parts[0] else 0
    if integer > 0:
        integer_unit = inflection.get(integer, inflection[2])
        text.append(f"{integer} {integer_unit}")

    # 소수부
    fraction = 0
    if len(parts) == 2:
        frac_str = parts[1]
        # 소수부를 실제 숫자로 환산
        if frac_str.isdigit():
            # 예: "50" → 50
            fraction = int(frac_str)
        else:
            fraction = 0

    if fraction > 0:
        # 센트/펜스 판단
        fraction_unit = inflection.get(fraction / 100, inflection[0.02])

        if integer > 0:
            text.append(f"and {fraction} {fraction_unit}")
        else:
            text.append(f"{fraction} {fraction_unit}")

    # 전체가 0일 경우
    if not text:
        return f"zero {inflection[2]}"

    return " ".join(text)


def _expand_currency(m: "re.Match") -> str:
    currency_symbol = m.group(1)
    value = m.group(2)

    currencies = {
        "$": {0.01: "cent", 0.02: "cents", 1: "dollar", 2: "dollars"},
        "€": {0.01: "cent", 0.02: "cents", 1: "euro", 2: "euros"},
        "£": {0.01: "penny", 0.02: "pence", 1: "pound sterling", 2: "pounds sterling"},
        "¥": {0.02: "sen", 2: "yen"},
    }

    inflection = currencies[currency_symbol]
    return __expand_currency(value, inflection)









def _expand_ordinal_orig(m):
    return _inflect.number_to_words(m.group(0))


def _expand_ordinal(m):
    num = m.group(1)

    # prefix 제거
    num = re.sub(r"^_(y|d)", "", num)

    ordinal_full = num + m.group(2)
    return _inflect.number_to_words(ordinal_full)


def _expand_number(m):

    raw = m.group(0)

    if raw.startswith("_y"):
        print("starts with _y")
        num = int(m.group(1))

        if 1000 < num < 3000:
            if num == 2000:
                return "two thousand"
            if 2000 < num < 2010:
                return "two thousand " + _inflect.number_to_words(num % 100)
            if num % 100 == 0:
                return _inflect.number_to_words(num // 100) + " hundred"
            return _inflect.number_to_words(num, andword="", zero="oh", group=2).replace(", ", " ")
    
    elif raw.startswith("_d"):
        # print("starts with _d")

        num_int = str(m.group(1))
        # print(f"num_int: {num_int}")
        num = " ".join(list(num_int))
        return _inflect.number_to_words(num, andword="", zero="oh", group=1).replace(", ", " ")
    elif raw.startswith("_e"):
        num_int = str(m.group(1))

        num = " ".join(list(num_int))
        return _inflect.number_to_words(num, andword="", zero="oh", group=1).replace(", ", " ")

    elif raw.startswith("_c"):
        num = int(m.group(1))
    else:
        # print("else")
        num = int(m.group(0))
    return _inflect.number_to_words(num, andword="")

def _prefix_year(m: "re.Match") -> str:
    year = m.group(0)
    return f"_y{year}"

def _prefix_digit(m: "re.Match") -> str:
    num = m.group(0)
    return f"_d{num}"

def _prefix_emergency(m):
    num = m.group(0)
    return f"_e{num}"

def normalize_numbers(text):


    text = re.sub(_might_emergen_number_re, _prefix_emergency, text)
    # print(f"_might_emergen_number_re:  {text}")
    # print(" > =========================== <\n")

    text = re.sub(_might_year_number_re, _prefix_year, text)
    # print(f"_might_year_number_re:  {text}")
    # print(" > =========================== <\n")
    text = re.sub(_might_digit_number_re, _prefix_digit, text)

    # print(f"_might_digit_number_re: {text}")
    # print(" > =========================== <\n")

    text = re.sub(_comma_number_re, _remove_commas, text)
    # print(f"_comma_number_re:       {text}")
    # print(" > =========================== <\n")

    text = re.sub(_currency_re, _expand_currency, text)
    # print(f"_currency_re:           {text}")
    # print(" > =========================== <\n")

    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    # print(f"_decimal_number_re:     {text}")
    # print(" > =========================== <\n")

    text = re.sub(_ordinal_re, _expand_ordinal, text)
    # print(f"_ordinal_re:            {text}")
    # print(" > =========================== <\n")

    # text = re.sub(_emergency_number_re, _expand_emergency, text)

    text = re.sub(_number_re, _expand_number, text)
    # print(f"_number_re:             {text}")
    # print(" > =========================== <\n")

    return text