import torch
import os
from dmtts.utils import hparam_utils as utils
from cached_path import cached_path
from huggingface_hub import hf_hub_download

LANG_TO_HF_REPO_ID = {
    'EN': 'kijoongkwon99/DMTTS-English',
    'JP': 'kijoongkwon99/DMTTS-Japanese',
    'ZH': 'kijoongkwon99/DMTTS-Chinese',
    'KR': 'kijoongkwon99/DMTTS-Korean',
    'TH': 'kijoongkwon99/DMTTS-Thai',
    'VI': 'kijoongkwon99/DMTTS-Vietnamese',
}


LANG_TO_LOCAL_REPO_ID = {
    'EN': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-English',
    'JP': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-Japanese',
    'ZH': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-Chinese',
    'KR': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-Korean',
    'TH': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-Thai',
    'VI': '/home/dev_admin/KKJ/TTS-model/DMTTS/local/DMTTS-Vietnamese',
}

def load_or_download_config(locale, use_hf=True, config_path=None):
    print("LOAD_OR_DOWNLOAD_CONFIG")
    language = locale.split('-')[0].upper()

    if config_path is not None:
        return utils.get_hparams_from_file(config_path)

    if use_hf:
        try:
            assert language in LANG_TO_HF_REPO_ID
            config_path = hf_hub_download(
                repo_id=LANG_TO_HF_REPO_ID[language],
                filename="config.json"
            )
        except Exception as e:

            use_hf = False  # fallback to local

    if not use_hf:
        assert language in LANG_TO_LOCAL_REPO_ID
        config_path = os.path.join(
            LANG_TO_LOCAL_REPO_ID[language],
            "config.json"
        )

    return utils.get_hparams_from_file(config_path)




def load_or_download_model(locale, device, use_hf=True, ckpt_path=None):
    print("LOAD_OR_DOWNLOAD_MODEL")
    language = locale.split('-')[0].upper()


    if ckpt_path is not None:
        return torch.load(ckpt_path, map_location=device)

    if use_hf:
        try:
            assert language in LANG_TO_HF_REPO_ID
            ckpt_path = hf_hub_download(
                repo_id=LANG_TO_HF_REPO_ID[language],
                filename="checkpoint.pth"
            )
        except Exception as e:
            use_hf = False  # fallback to local


    if not use_hf:
        assert language in LANG_TO_LOCAL_REPO_ID
        ckpt_path = os.path.join(
            LANG_TO_LOCAL_REPO_ID[language],
            "checkpoint.pth"
        )

    return torch.load(ckpt_path, map_location=device)




def load_pretrain_model():
    return (
        cached_path(PRETRAINED_MODELS["G.pth"]), # EN checkpoint
        cached_path(PRETRAINED_MODELS["D.pth"]),
        cached_path(PRETRAINED_MODELS["DUR.pth"]),
    )


def load_pretrained_language_model(locale):
    language = locale.split('-')[0].upper()
    return (
        cached_path(DOWNLOAD_CKPT_URLS[language]),
        cached_path(PRETRAINED_MODELS["D.pth"]),
        cached_path(PRETRAINED_MODELS["DUR.pth"]),
    )       

