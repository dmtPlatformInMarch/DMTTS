# Convert Vietnamese text to phonemes
# Utilizing Viphoneme (IEEE): https://github.com/v-nhandt21/Viphoneme.git
"""
CITATION
@inproceedings{tri2020vietnamese,
  title={Vietnamese Speech Synthesis with End-to-End Model and Text Normalization},
  author={Tri, Nguyen Minh and Nam, Cao Xuan and others},
  booktitle={2020 7th NAFOSTED Conference on Information and Computer Science (NICS)},
  pages={179--184},
  year={2020},
  organization={IEEE}
}
"""
from typing import List, Tuple
import re
import unicodedata
import os
import sys

sys.stderr = open(os.devnull, 'w')  # 모든 stderr 출력 버리기



#from dmtts.model.text.phonemizer.vi.viphoneme import vi2IPA, vi2IPA_split 
from viphoneme import vi2IPA, vi2IPA_split

# /.../ 토큰 추출용
_SLASH_TOKEN = re.compile(r"/([^/]+)/")
# 0~6 톤 숫자
TONE_RE = re.compile(r"^[0-6]$")
# 구두점 집합 (원하면 'sp' 처리로 바꿀 수 있음)
PUNCT = {",", ".", "!", "?", ";", ":"}

def tone_shift(t: int) -> int:
    # 필요 없으면 그대로  t 반환해도 됨
    return t - 1 if t > 0 else 0

def text_normalize(text: str) -> str:
    if not text:
        return text
    t = unicodedata.normalize("NFC", text)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def print_procedure(out_phones,out_tones):
    print(f"out_phones  :{out_phones}")
    print(f"out_tones   :{out_tones}")
    print(f"len_phons   :{len(out_phones)}")
    print(f"len_tones   :{len(out_tones)}")
    print("-----------------------------------------")        

def g2p(norm_text: str, add_space=False) -> Tuple[List[str], List[int]]:

    viet_ipa_split = vi2IPA_split(norm_text, delimit="/")
    #print(f"fist    :{viet_ipa_split}")
    # TODO: temporal exception for ! or ? since it is not contained on training set
    viet_ipa_split = viet_ipa_split.replace("/../ /./", "/./")
    # TODO: temporal exception for . since it is not contained on training set
    viet_ipa_split = viet_ipa_split.replace("/./ /./  /./", "/./")
    viet_ipa_split = viet_ipa_split.replace("/./ /./", "/./")
    #print(f"second  :{viet_ipa_split}")
    tokens = viet_ipa_split.split("/")   # 슬래시 기준 분리

    #print(f"tokens: {tokens}")
    out_phones: List[str] = []
    out_tones:  List[int] = []

    run_count = 0  # 마지막 '톤 숫자' 이후부터 지금까지 모은 음소 개수

    first_done = False # wheter the first token is not vietnamese
    #print(f"tokens  :{tokens}")
    for tok in tokens:
        #print(f"run :{run_count}")
        #print(f"tok :{tok}")
        if not tok or tok == "_" or tok == " ":
            #print("if not tok or tok == '_' or tok == ' ':")
            if add_space:
                out_phones.append("SP")
                out_tones.append(0)
            #print_procedure(out_phones, out_tones)   

            continue
        if not first_done:
            #print("if not first_done:")
            if not compare_diff(norm_text):
                tone = 0
                non_vi_phs, num = split_non_vi(tok)
                out_phones.extend(non_vi_phs)
                out_tones.extend([tone]*num)
            first_done=True
            #print_procedure(out_phones, out_tones)      

            continue
        if tok in PUNCT:
            #print("if tok in PUNCT:")
            #print(f"PUNT : {tok}")
            tone = 0
            out_tones.extend([tone])
            out_phones.append(tok)
            #print_procedure(out_phones, out_tones)     
            continue

        if is_non_vi(tok):
            #print("if is_non_vi(tok):")
            tone = 0
            #print(f"non_vi_tok: {tok}")
            non_vi_phs, num = split_non_vi(tok)
            out_phones.extend(non_vi_phs)
            out_tones.extend([tone] * num)
            #print_procedure(out_phones, out_tones)       

            continue

        if TONE_RE.match(tok):
            #print("if TONE_RE.match(tok):")
            tone = tone_shift(int(tok))
            if run_count > 0:
                out_tones.extend([tone] * run_count)
                #out_tones.extend([0])
                run_count = 0
            # run_count==0이면(연속 숫자 등) 그냥 스킵
            #print_procedure(out_phones, out_tones)        

            continue

        # 그 외는 '음소'로 취급하여 out_phones에 추가
        #print("ELSE")
        out_phones.append(tok)
        run_count += 1
        #print_procedure(out_phones, out_tones)    

    # 끝났는데 마지막 묶음에 톤 숫자가 없었다면 0톤으로 채움
    if run_count > 0:
        out_tones.extend([0] * run_count)
    phones = ["_"] + out_phones + ["_"]
    tones  = [0]   + out_tones  + [0]
    return phones, tones

#def add_zero_tone(ipa_text):
    

def is_non_vi(tok):
    if tok[0] == " ":
        ipa_raw = vi2IPA(tok).replace(".", "")
        ipa_split = vi2IPA_split(tok, delimit="/").replace("/","").replace(".", "")

        return ipa_raw != ipa_split
    else:
        return False

def split_non_vi(tok):
    ipa_raw = vi2IPA(tok)
    s = ipa_raw.replace("ˈ", "").replace(".","").strip()
    phones: List[str] = list(s) if s else [tok]

    #print(f"phones: {phones}")
    return phones, len(phones)

def extract_non_vi(ipa_text: str) -> str:
    if not ipa_text:
        return ipa_text
    s = re.sub(r'(?:^|\s)(?:\S*\d\S*|[.,!?;:])(?=\s|$)', ' ', ipa_text)
    return re.sub(r'\s+', ' ', s).strip()

def get_first_split(norm_text: str) -> str:
    """
    Return the first word from normalized Vietnamese text.
    Words are split by whitespace after NFC normalization.
    """
    if not norm_text:
        return ""
    # 이미 text_normalize에서 NFC와 strip 처리했으니 여기서는 split만
    words = norm_text.split(" ")
    return words[0] if words else ""



def compare_diff(norm_text):
    norm_text = get_first_split(norm_text)
    ipa_raw = vi2IPA(norm_text)
    ipa_split = vi2IPA_split(norm_text, delimit="/")
    ipa_split = ipa_split.replace("/", "")

    non_vi_from_raw= extract_non_vi(ipa_raw)
    non_vi_from_split= extract_non_vi(ipa_split)

    #print(f"non_vi_from_raw:    {non_vi_from_raw}")
    #print(f"non_vi_from_split:  {non_vi_from_split}")
    return non_vi_from_raw == non_vi_from_split

#def is_non_vi(ipa_te)


if __name__ == "__main__":
    vi_text = "xâm hại tình dục trẻ em là vấn đề của toàn cầu."
    phoneme = vi2IPA(vi_text)
    print(f"vi_text     :{vi_text}\n")
    print(f"vi2IPA      :{phoneme}\n")
    
    #phoneme_split = vi2IPA_split(vi_text, delimit="/")
    #print(f"vi2IPA_split:{phoneme_split}")


    import subprocess, json, textwrap, os

    def silent_vi2IPA_split(text, delimit="/"):
        code = textwrap.dedent(f"""
        from viphoneme import vi2IPA_split
        import json
        print(json.dumps(vi2IPA_split({text!r}, delimit={delimit!r})))
        """)

        # 🚫 stderr를 완전히 /dev/null로 연결 (C write까지 차단)
        with open(os.devnull, 'w') as devnull:
            result = subprocess.run(
                ["python3", "-c", code],
                stdout=subprocess.PIPE,
                stderr=devnull,   # 핵심: stderr 완전 차단
                text=True,
            )

        if not result.stdout.strip():
            print("[silent_vi2IPA_split] Warning: empty stdout")
            return None

        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print("[silent_vi2IPA_split] JSON decode error, raw output:", result.stdout)
            return None



    phoneme_split = vi2IPA_split(vi_text, delimit="/")
    print(f"\n vi2IPA_split result:\n{phoneme_split}")
    
    print("running vi2IPA_split silently...")
    phoneme_split = silent_vi2IPA_split(vi_text, delimit="/")
    print(f"\n✅ vi2IPA_split result:\n{phoneme_split}")

    """
    norm = text_normalize(vi_text)
    print(f"applying vietnam g2p")
    ph, tn = g2p(norm)
    print("phones:", ph)
    print("tones :", tn)
    print("len   :", len(ph), len(tn))
    """

