import re
import unicodedata
from num2words import num2words

# =========================
# MeCab
# =========================
try:
    import MeCab
except ImportError:
    raise ImportError("Please install mecab-python3 and unidic-lite")

TAGGER = MeCab.Tagger()

# =========================
# Alphabets / symbols
# =========================
_ALPHASYMBOL_YOMI = {
    "a": "エー", "b": "ビー", "c": "シー", "d": "ディー", "e": "イー",
    "f": "エフ", "g": "ジー", "h": "エイチ", "i": "アイ", "j": "ジェー",
    "k": "ケー", "l": "エル", "m": "エム", "n": "エヌ", "o": "オー",
    "p": "ピー", "q": "キュー", "r": "アール", "s": "エス", "t": "ティー",
    "u": "ユー", "v": "ブイ", "w": "ダブリュー", "x": "エックス",
    "y": "ワイ", "z": "ゼット",
    "&": "アンド", "%": "パーセント", "+": "プラス", "-": "マイナス",
    "@": "アット", "#": "シャープ"
}

def convert_alpha_symbols(text: str) -> str:
    return "".join(_ALPHASYMBOL_YOMI.get(c.lower(), c) for c in text)

# =========================
# Numbers
# =========================
_NUMBER_WITH_SEPARATOR_RX = re.compile(r"[0-9]{1,3}(,[0-9]{3})+")
_CURRENCY_RX = re.compile(r"([$¥£€])([0-9.]*[0-9])")
_CURRENCY_MAP = {"$": "ドル", "¥": "円", "£": "ポンド", "€": "ユーロ"}
_NUMBER_RX = re.compile(r"[0-9]+(\.[0-9]+)?")

def convert_numbers(text: str) -> str:
    text = _NUMBER_WITH_SEPARATOR_RX.sub(lambda m: m[0].replace(",", ""), text)
    text = _CURRENCY_RX.sub(lambda m: m[2] + _CURRENCY_MAP[m[1]], text)
    text = _NUMBER_RX.sub(lambda m: num2words(m[0], lang="ja"), text)
    return text

# =========================
# Kana conversion
# =========================
_HIRAGANA = "".join(chr(i) for i in range(ord("ぁ"), ord("ん") + 1))
_KATAKANA = "".join(chr(i) for i in range(ord("ァ"), ord("ン") + 1))
_HIRA2KATA = str.maketrans(_HIRAGANA, _KATAKANA)

def hira2kata(text: str) -> str:
    return text.translate(_HIRA2KATA).replace("う゛", "ヴ")

# =========================
# MeCab: text → katakana
# =========================
_SYMBOL_TOKENS = set("、。？！・")
_NO_YOMI_TOKENS = set("「」『』（）［］[]―")

def text2kata(text: str) -> str:
    parsed = TAGGER.parse(text)
    res = []

    for line in parsed.split("\n"):
        if line == "EOS":
            break
        cols = line.split("\t")
        surface = cols[0]
        features = cols[1].split(",")

        yomi = features[6] if len(features) > 6 else "*"

        if yomi != "*" and yomi:
            res.append(yomi)
        else:
            if surface in _SYMBOL_TOKENS:
                res.append(surface)
            elif surface in ("っ", "ッ"):
                res.append("ッ")
            elif surface in _NO_YOMI_TOKENS:
                pass
            else:
                res.append(surface)

    return hira2kata("".join(res))

# =========================
# Katakana → phoneme (Julius)
# =========================
_CONVRULES_1 = {
    "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o",
    "カ": "k a", "キ": "k i", "ク": "k u", "ケ": "k e", "コ": "k o",
    "サ": "s a", "シ": "sh i", "ス": "s u", "セ": "s e", "ソ": "s o",
    "タ": "t a", "チ": "ch i", "ツ": "ts u", "テ": "t e", "ト": "t o",
    "ナ": "n a", "ニ": "n i", "ヌ": "n u", "ネ": "n e", "ノ": "n o",
    "ハ": "h a", "ヒ": "h i", "フ": "f u", "ヘ": "h e", "ホ": "h o",
    "マ": "m a", "ミ": "m i", "ム": "m u", "メ": "m e", "モ": "m o",
    "ラ": "r a", "リ": "r i", "ル": "r u", "レ": "r e", "ロ": "r o",
    "ヤ": "y a", "ユ": "y u", "ヨ": "y o",
    "ワ": "w a",
    "ン": "N",
    "ッ": "q",
    "ー": ":",
}


# =========================
# Katakana → phoneme (Julius, longest-match)
# =========================

_CONVRULES_2 = {
    # 拗音
    "キョ": "k y o",
    "キュ": "k y u",
    "キャ": "k y a",

    "ショ": "sh o",
    "シュ": "sh u",
    "シャ": "sh a",

    "チョ": "ch o",
    "チュ": "ch u",
    "チャ": "ch a",

    "ニョ": "n y o",
    "ニュ": "n y u",
    "ニャ": "n y a",

    "リョ": "r y o",
    "リュ": "r y u",
    "リャ": "r y a",

    "ギョ": "g y o",
    "ギュ": "g y u",
    "ギャ": "g y a",

    "ビョ": "b y o",
    "ビュ": "b y u",
    "ビャ": "b y a",

    "ピョ": "p y o",
    "ピュ": "p y u",
    "ピャ": "p y a",

    # 外来音 (최소)
    "ファ": "f a",
    "フィ": "f i",
    "フェ": "f e",
    "フォ": "f o",

    "ティ": "t i",
    "ディ": "d i",
}


def kata2phoneme(text: str):
    res = []
    i = 0
    L = len(text)

    while i < L:
        # 1) 2글자 우선 매칭
        if i + 1 < L:
            pair = text[i:i+2]
            if pair in _CONVRULES_2:
                res.extend(_CONVRULES_2[pair].split())
                i += 2
                continue

        # 2) 단일 글자
        ch = text[i]
        if ch in _CONVRULES_1:
            res.extend(_CONVRULES_1[ch].split())

        # 3) 그 외는 무시
        i += 1

    return res

def text_normalize(text):
    return text
# =========================
# Full pipeline
# =========================
def g2p(text: str):
    print(f"input text      :{text}")
    text = unicodedata.normalize("NFKC", text)
    print(f"unicodedata     :{text}")
    text = convert_numbers(text)
    print(f"convert_numbers :{text}")
    text = convert_alpha_symbols(text)
    print(f"convert_english :{text}")
    kata = text2kata(text)
    print(f"text2kata       :{kata}")
    phones = kata2phoneme(kata)
    print(f"kata2phoneme    :{phones}")

    phones = ["_"] + phones + ["_"]
    tones = [0] * len(phones)
    return phones, tones

# =========================
# Test
# =========================
if __name__ == "__main__":
    
    text = "こんにちは。 今日はKFCで100円払った。"
    # text = "今日は暑いです。KFCに行きます。"
    text = "今日は"
    phones, tones = g2p(text)
    print("TEXTS        :", text)
    print("PHONES       :", phones)
    print("TONES        :", tones)
