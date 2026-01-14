import re
import unicodedata


_BETASYMBOL_YOMI = {
    "#": "シャープ",
    "%": "パーセント",
    "&": "アンド",
    "+": "プラス",
    "-": "マイナス",
    ":": "コロン",
    ";": "セミコロン",
    "<": "小なり",
    "=": "イコール",
    ">": "大なり",
    "@": "アット",
    "α": "アルファ",
    "β": "ベータ",
    "γ": "ガンマ",
    "δ": "デルタ",
    "ε": "イプシロン",
    "ζ": "ゼータ",
    "η": "イータ",
    "θ": "シータ",
    "ι": "イオタ",
    "κ": "カッパ",
    "λ": "ラムダ",
    "μ": "ミュー",
    "ν": "ニュー",
    "ξ": "クサイ",
    "ο": "オミクロン",
    "π": "パイ",
    "ρ": "ロー",
    "σ": "シグマ",
    "τ": "タウ",
    "υ": "ウプシロン",
    "φ": "ファイ",
    "χ": "カイ",
    "ψ": "プサイ",
    "ω": "オメガ",
}

_ALPHASYMBOL_YOMI = {
    "a": "エー",
    "b": "ビー",
    "c": "シー",
    "d": "ディー",
    "e": "イー",
    "f": "エフ",
    "g": "ジー",
    "h": "エイチ",
    "i": "アイ",
    "j": "ジェー",
    "k": "ケー",
    "l": "エル",
    "m": "エム",
    "n": "エヌ",
    "o": "オー",
    "p": "ピー",
    "q": "キュー",
    "r": "アール",
    "s": "エス",
    "t": "ティー",
    "u": "ユー",
    "v": "ブイ",
    "w": "ダブリュー",
    "x": "エックス",
    "y": "ワイ",
    "z": "ゼット",
}

# 발음에 기여하지 않는 일본어 괄호/기호
_DROP_CHARS = set([
    "「", "」", "『", "』",
    "（", "）", "(", ")",
    "［", "］", "[", "]",
    "｛", "｝", "{", "}",
    "〈", "〉", "《", "》",
])


# =========================
# MeCab
# =========================
try:
    import MeCab
except ImportError:
    raise ImportError("Please install mecab-python3 and unidic-lite")

TAGGER = MeCab.Tagger()

# =========================
# jphones
# =========================
import jphones as j2p

PHONETIZER = j2p.phonetizer.Phonetizer()

# =========================
# Regex
# =========================
_NUMBER_ONLY_RX = re.compile(r"^[0-9]+$")
_SKIP_TOKEN_RX = re.compile(r"^[、。？！・]$")
_NUM_NONNUM_RX = re.compile(r"(?<=\d)(?=\D)|(?<=\D)(?=\d)")
_ENGLISH_ONLY_RX = re.compile(r"^[A-Za-z]+$")
_ACRONYM_RX = re.compile(r"^[A-Z]{2,4}$")          # (옵션) 2~5글자 대문자 약어
_EN_WORD_RX = re.compile(r"^[A-Za-z]+$")           # 영단어(연속)
_ENGLISH_ONLY_RX = re.compile(r"^[A-Za-z]+$")

# =========================
# MeCab tokenizer
# =========================
def mecab_tokenize(text: str):
    """
    MeCab을 사용해 surface token 리스트 반환
    """
    parsed = TAGGER.parse(text)
    tokens = []

    for line in parsed.split("\n"):
        if line == "EOS":
            break
        surface = line.split("\t")[0]
        tokens.append(surface)

    return tokens

def convert_alpha_symbols_selective(text: str, convert_acronym: bool = True) -> str:
    """
    - 단일 문자(알파벳)는 _ALPHASYMBOL_YOMI로 치환
    - 연속 영단어(starbucks)는 그대로 둠
    - 대문자 약어(CCTV, PCA)는 철자 읽기
    - ⭐ 추가: 영문 1글자가 일본어/한자와 붙어 있으면 그 글자만 치환
    """
    out_tokens = []

    for tok in text.split():
        if not tok:
            continue

        # 1) 단일 문자 토큰
        if len(tok) == 1:
            key = tok.lower()
            out_tokens.append(_ALPHASYMBOL_YOMI.get(key, tok))
            continue

        # 2) 대문자 약어 (CCTV, PCA)
        if convert_acronym and _ACRONYM_RX.fullmatch(tok):
            spelled = []
            for ch in tok:
                spelled.append(_ALPHASYMBOL_YOMI.get(ch.lower(), ch))
            out_tokens.append(" ".join(spelled))
            continue

        # 3) 순수 영단어는 그대로
        if _EN_WORD_RX.fullmatch(tok):
            out_tokens.append(tok)
            continue

        # ⭐ 4) 영문 1글자 + 일본어/한자 혼합 토큰
        new_tok = []
        for ch in tok:
            if ch.isascii() and ch.isalpha():
                new_tok.append(_ALPHASYMBOL_YOMI.get(ch.lower(), ch))
            else:
                new_tok.append(ch)
        out_tokens.append("".join(new_tok))

    return " ".join(out_tokens)


def convert_alpha_inline(text: str) -> str:
    """
    규칙:
    - 영문 한 글자(a~z, A~Z)가
      앞뒤가 영문이 아닐 경우 → 철자 읽기
    - 연속 영단어(starbucks)는 보호
    """
    res = []
    n = len(text)

    for i, ch in enumerate(text):
        # 알파벳이 아니면 그대로
        if not ch.isalpha() or not ch.isascii():
            res.append(ch)
            continue

        prev_is_alpha = i > 0 and text[i - 1].isalpha() and text[i - 1].isascii()
        next_is_alpha = i < n - 1 and text[i + 1].isalpha() and text[i + 1].isascii()

        # 앞뒤 중 하나라도 영문이면 → 연속 영단어 → 보호
        if prev_is_alpha or next_is_alpha:
            res.append(ch)
        else:
            # 영문 한 글자 단독 → 철자 읽기
            res.append(_ALPHASYMBOL_YOMI.get(ch.lower(), ch))

    return "".join(res)

def drop_unreadable_symbols(text: str) -> str:
    return "".join(ch for ch in text if ch not in _DROP_CHARS)


def convert_beta(text: str) -> str:
    """
    _BETASYMBOL_YOMI 에 해당하는 문자를
    문맥 상관없이 문자 단위로 무조건 변환
    """
    res = []
    for ch in text:
        if ch in _BETASYMBOL_YOMI:
            res.append(_BETASYMBOL_YOMI[ch])
        else:
            res.append(ch)
    return "".join(res)

def nomalize_japanese_puncts(text: str) -> str:
    return text.replace("、", ",").replace("。", ".")

def text_normalize(text):
    text = unicodedata.normalize("NFKC", text)

    text = nomalize_japanese_puncts(text)
    # 숫자 ↔ 비숫자 경계에 공백 삽입 (a1 -> a 1, 1a -> 1 a)
    text = _NUM_NONNUM_RX.sub(" ", text)

    # 괄호/인용부호 제거
    text = drop_unreadable_symbols(text)


    text = convert_beta(text)
    # ⭐ 선택적 알파/기호 변환: 단일 문자만 변환, 영단어는 보존
    text = convert_alpha_symbols_selective(text, convert_acronym=True)  # PCA도 변환 원하면 True
    # text = convert_alpha_inline(text)
    return text



# =========================
# jphones token wrapper
# =========================
def jphones_token2phonemes(token_str: str):
    """
    단일 token → jphones phoneme list
    """
    # 공백 / 문장부호 제거
    if not token_str.strip():
        return []
    if _SKIP_TOKEN_RX.match(token_str):
        return []

    token_type = "number" if _NUMBER_ONLY_RX.match(token_str) else "word"

    token = {
        "token": token_str,
        "type": token_type
    }

    out = PHONETIZER.get_phonemes(token)
    return out["phonemes"]


# =========================
# Full pipeline
# =========================
def split_digits(token_str: str):
    """
    숫자 문자열 → 각 자리 숫자 리스트
    "3050" → ["3", "0", "5", "0"]
    """
    return list(token_str)

def g2p(text: str):
    text = unicodedata.normalize("NFKC", text)
    text = text_normalize(text)

    tokens = mecab_tokenize(text)

    phones = []
    for t in tokens:
        p = jphones_token2phonemes(t)

        if p == ['NUM-TOO-LARGE']:
            # 숫자 fallback
            for d in split_digits(t):
                phones.extend(jphones_token2phonemes(d))
        else:
            phones.extend(p)

    phones = ["_"] + phones + ["_"]
    tones = [0] * len(phones)
    return phones, tones


# =========================
# Test
# =========================
if __name__ == "__main__":
    text = "休日の料金は、メーターの 30 %増しです。"
    text = "30 %増"
    text = "三番目の、そしてもっとも重要な考えは、再入ということである。"
    text = "こんにちは。今日は staarbahks 三番目の、そしてもっとも重要な考えは、再入ということである。"
    text = text_normalize(text)
    phones, tones = g2p(text)

    print("\n[PHONEMES]")
    print(phones, len(phones))
    print(tones, len(tones))
