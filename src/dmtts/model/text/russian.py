import re
from ruaccent import RUAccent

_accentizer = None


def _load_accentizer(device="auto"):
    global _accentizer
    if _accentizer is None:
        _accentizer = RUAccent()
        _accentizer.load(
            omograph_model_size="turbo3.1",
            use_dictionary=True,
            tiny_mode=False,
            device=device,
        )
    return _accentizer


def post_replace_ph(ph: str) -> str:
    rep_map = {
        # fullwidth / CJK punctuation
        "：": ",",
        "；": ",",
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "\n": ".",
        "·": ",",
        "、": ",",
        "...": "…",
        ";": ",",

        # latin normalize
        # "v": "V",

        # ❗ 러시아어/유럽식 인용부호 제거
        "«": "",
        "»": "",
        "“": "",
        "”": "",
        "„": "",

        # 괄호 제거
        "(": "",
        ")": "",
        "[": "",
        "]": "",
        "{": "",
        "}": "",
    }

    return rep_map.get(ph, ph)


def normalize(text: str, add_stress: bool = True, device: str = "cpu") -> str:
    """
    Russian text normalization.
    - lowercasing
    - optional stress marking via RUAccent

    Args:
        text (str): raw input text
        add_stress (bool): whether to apply stress
        device (str): cpu / cuda

    Returns:
        normalized text (with '+' if add_stress=True)
    """
    text = text.strip().lower()

    if add_stress:
        accentizer = _load_accentizer(device)
        text = accentizer.process_all(text)

    return text

def text_normalize(text):
    print("russian text normalize")
    text = normalize(text)
    print(f"text: {text}")
    return text

def g2p(norm_text: str):
    """
    Russian pseudo-G2P (character-level with stress tones).

    Input:
        norm_text: normalized russian text (may contain '+')
            e.g. "с трев+ожным ч+увством"

    Output:
        phones: ["_", "с", "т", "р", "е", "в", "о", ... , "_"]
        tones : [0, 0, 0, 0, 0, 0, 1, ... , 0]
    """

    phs = []
    tones = []

    pending_stress = False

    for ch in norm_text:
        # stress marker → applies to NEXT phone
        if ch == "+":
            pending_stress = True
            continue

        # skip spaces entirely
        if ch.isspace():
            continue

        # normalize punctuation / symbols
        ch = post_replace_ph(ch)

        phs.append(ch)
        tones.append(1 if pending_stress else 0)
        pending_stress = False

    phones = ["_"] + phs + ["_"]
    tones = [0] + tones + [0]

    return phones, tones




if __name__ == "__main__":
    text = "давайте лучше выпьем и рванём к «максиму». там новое ревю."
    norm = normalize(text, add_stress=True)

    phones, tones = g2p(norm)

    print(norm)
    print(phones)
    print(tones)
    print("----------")
    print(f"text_len    :{len(text)+2-6}")
    print(f"phones_len  :{len(phones)}")
    print(f"tones_len   :{len(tones)}")