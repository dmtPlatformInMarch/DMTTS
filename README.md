# 🗣️ DMTTS: Multi-Language Text-to-Speech System  

DMTTS is a VITS-based multilingual text-to-speech toolkit.
---

## 🌍 Supported Languages
DMTTS supports **English**, **Chinese**, **Korean**, **Japanese**, **Vietnamese**, and **Thai**.  
Each language is currently represented by **a single speaker**.

---

## ⚙️ Environment Setup

### Using Conda
```bash
conda create -n dmtts python=3.11
conda activate dmtts
```

### Simple Installation
```bash
pip install git+https://github.com/dmtPlatformInMarch/DMTTS.git 
```

#### if Ubuntu 22.04 
```bash
pip install git+https://github.com/dmtPlatformInMarch/DMTTS.git@ubuntu.22.04
```

#### if Ubuntu 20.04
```bash
pip install git+https://github.com/dmtPlatformInMarch/DMTTS.git@ubuntu.20.04

```

### for japanese, additionally
```bash
pip install git+https://github.com/JRMeyer/jphones.git
python -m unidic download
```

---

## 🚀 Quick Start

```python
from dmtts.app.api import TTS

# Default text for each language
DEFAULT_TEXT = {
    "EN": "Did you ever hear a folk tale about a giant turtle?",
    "ZH": "领域近年来发展迅速。",
    "KR": "최근, 텍스트 음성 합성 분야가 급속도로 발전하고 있습니다.",
    "VI": "xâm hại tình dục trẻ em là vấn đề của toàn cầu",
    "TH": "ในช่วงหลังมานี้ เทคโนโลยีสังเคราะห์เสียงพูดได้พัฒนาอย่างรวดเร็ว",
    "JP": "テキスト読み上げの分野は最近急速な発展を遂げています。",
}

LANG_TO_LOCAL_REPO_ID = {
    'EN': 'path/to/your/local/path',
    'JP': 'path/to/your/local/path',
    'ZH': 'path/to/your/local/path',
    'KR': 'path/to/your/local/path',
    'TH': 'path/to/your/local/path',
    'VI': 'path/to/your/local/path',
}
# List of languages to synthesize
Languages = list(DEFAULT_TEXT.keys())

# Speaking speed
speed = 1.0

for language in Languages:
    print(f"Generating speech for [{language}]...")

    # Load model
    # if you want to load model from hugging face
    model = TTS(language=language, device="auto", use_hf=True)
    # or if you want to load from your own directory
    # model = TTS(language=language, device="auto", use_hf=False, local_repo_path_dict=LANG_TO_LOCAL_REPO_ID)

    # Get speaker information
    speaker_ids = model.hps.data.spk2id
    speaker = list(speaker_ids.keys())[0]
    speaker_id = speaker_ids[speaker]

    # Select text
    text = DEFAULT_TEXT[language]

    # Define output file path
    output_path = f"{language}.wav"

    # Run synthesis
    model.tts_to_file(
        text=text,
        speaker_id=speaker_id,
        output_path=output_path,
        speed=speed,
        quiet=True
    )

    print(f"Saved: {output_path}")

```

---

## 💾 Clone & Local Installation
```bash
git clone https://github.com/kijoongkwon99/DMTTS.git
cd DMTTS
pip install -e .
python -m unidic download
```

---

---
## 💾 Model & Config Installation


You can easily download pre-trained **DMTTS** models for each supported language from **Hugging Face**.

### 📁 Download Path in Source Code
All model download and configuration logic is implemented in: `dmtts/src/utils/download_utils.py`

### 🌍 Supported Languages
```
# When downloading from Hugging Face Hub
LANG_TO_HF_REPO_ID = {
    'EN': 'kijoongkwon99/DMTTS-English',
    'JP': 'kijoongkwon99/DMTTS-Japanese',
    'ZH': 'kijoongkwon99/DMTTS-Chinese',
    'KR': 'kijoongkwon99/DMTTS-Korean',
    'TH': 'kijoongkwon99/DMTTS-Thai',
    'VI': 'kijoongkwon99/DMTTS-Vietnamese',
}

```
If you want to load models locally instead of from Hugging Face,<br>
make sure that BOTH of the following files exist inside each directory:<br>
  - checkpoint.pth  → the model weights
  - config.json     → the model configuration
<br>

Example:<br>
/to/your/local/path/<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── checkpoint.pth<br>
&nbsp;&nbsp;&nbsp;&nbsp;└── config.json<br>
Otherwise, local loading will fail and you may need to re-download them.

---



---
## 📁 Project Structure

```
DMTTS/
│
├── ckpts/                             # Model checkpoints
│   └── README.md
│
├── data/                              # Dataset folder
│
└── src/dmtts/
    ├── __init__.py
    │
    ├── app/                           # API / Main entrypoints
    │   ├── __init__.py
    │   ├── api.py
    │   ├── app.py
    │   ├── main.py
    │   └── README.md
    │
    ├── eval/                          # Evaluation scripts
    │   ├── __init__.py
    │   ├── ecapa_tdnn.py
    │   ├── eval_infer_batch.py
    │   ├── eval_metric_batch.py
    │   ├── infer_metric_batch.sh
    │   ├── result/
    │   └── README.md
    │
    ├── infer/                         # Inference scripts
    │   ├── __init__.py
    │   ├── infer_cli.py
    │   ├── outputs/
    │   └── README.md
    │
    ├── model/                         # Model architecture
    │   ├── __init__.py
    │   ├── backbones/                 
    │   │   ├── __init__.py
    │   │   ├── discriminators.py
    │   │   ├── duration_predictors.py
    │   │   ├── encoders.py
    │   │   ├── flows.py
    │   │   └── generators.py
    │   │
    │   ├── monotonic_align/           # Alignment functions
    │   │   ├── __init__.py
    │   │   └── core.py
    │   │
    │   ├── text/                      # Text processing modules
    │   │   ├── __init__.py
    │   │   ├── chinese.py
    │   │   ├── cleaner.py
    │   │   ├── english.py
    │   │   ├── japanese.py
    │   │   ├── korean.py
    │   │   ├── kr_normalizer.py
    │   │   ├── symbols.py
    │   │   ├── thai.py
    │   │   ├── tone_sandhi.py
    │   │   ├── vietnamese.py
    │   │   ├── english_utils/         # English text normalization utils
    │   │   │   ├── __init__.py
    │   │   │   ├── abbreviations.py
    │   │   │   ├── number_norm.py
    │   │   │   └── time_norm.py
    │   │   └── README.md
    │   │
    │   ├── attentions.py
    │   ├── commons.py
    │   ├── modules.py
    │   ├── synthesizer.py
    │   └── transforms.py
    │
    ├── train/                         # Training scripts & configs
    │   ├── __init__.py
    │   ├── train.py
    │   ├── losses.py
    │   ├── preprocess_text.py
    │   ├── mel_processing.py
    │   ├── train.sh
    │   └── README.md
    │
    └── utils/                         # Helper modules
        ├── __init__.py
        ├── data_utils.py
        ├── download_utils.py
        ├── hparam_utils.py
        ├── infer_utils.py
        └── eval_utils.py

```

---
