from pathlib import Path

def load_metadata(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fields = line.split("|")
            if len(fields) < 6:
                continue

            audio_path = fields[0]
            phoneme = fields[4]
            data[audio_path] = phoneme
    return data


meta_new = load_metadata("metadata.list")
meta_orig = load_metadata("metadata_orig.list")

common_keys = set(meta_new.keys()) & set(meta_orig.keys())

print(f"공통 audio_path 개수: {len(common_keys)}")

diff = []

for k in sorted(common_keys):
    p_new = meta_new[k]
    p_orig = meta_orig[k]
    if p_new != p_orig:
        diff.append((k, p_orig, p_new))

print(f"phoneme 불일치 개수: {len(diff)}")
