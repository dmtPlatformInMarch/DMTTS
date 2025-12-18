import torch
import os
from dmtts.utils import hparam_utils as utils
from cached_path import cached_path
from huggingface_hub import hf_hub_download

LANG_TO_HF_REPO_ID = {
    'EN': 'kijoongkwon99/DMTTSv2-English',
    'JP': 'kijoongkwon99/DMTTS-Japanese',
    'ZH': 'kijoongkwon99/DMTTS-Chinese',
    'KR': 'kijoongkwon99/DMTTSv2-Korean',
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

def load_or_download_config_orig(locale, use_hf=True, config_path=None, local_repo_path_dict=None, skip_seed=True):
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
        assert local_repo_path_dict is not None, \
            "local_repo_path_dict must be provided when use_hf=False"

        assert language in local_repo_path_dict, \
            f"{language} not found in local_repo_path_dict"

        config_path = os.path.join(local_repo_path_dict[language], "config.json")

    return utils.get_hparams_from_file(config_path)

def load_or_download_config(
    locale,
    use_hf=True,
    config_path=None,
    local_repo_path_dict=None,
    skip_snap_seed=True
):
    print("LOAD_OR_DOWNLOAD_CONFIG")
    language = locale.split('-')[0].upper()

    # ① 직접 config 경로가 주어진 경우
    if config_path is not None:
        return utils.get_hparams_from_file(config_path)

    # ② Hugging Face에서 받아오는 경우
    if use_hf:
        try:
            assert language in LANG_TO_HF_REPO_ID
            config_path = hf_hub_download(
                repo_id=LANG_TO_HF_REPO_ID[language],
                filename="config.json"
            )
        except Exception as e:
            print(f"[WARN] Hugging Face download failed: {e}")
            use_hf = False  # fallback

    # ③ 로컬에서 불러오는 경우
    if not use_hf:
        assert local_repo_path_dict is not None, \
            "local_repo_path_dict must be provided when use_hf=False"
        assert language in local_repo_path_dict, \
            f"{language} not found in local_repo_path_dict"

        base_path = local_repo_path_dict[language]

        # ✅ skip_snap_seed=True → snapshots/<hash> 자동 탐색
        if skip_snap_seed:
            snapshots_dir = os.path.join(base_path, "snapshots")
            if not os.path.isdir(snapshots_dir):
                raise FileNotFoundError(f"'snapshots' directory not found in {base_path}")

            subdirs = [
                d for d in os.listdir(snapshots_dir)
                if os.path.isdir(os.path.join(snapshots_dir, d))
            ]
            if not subdirs:
                raise FileNotFoundError(f"No snapshot subdirectories found in {snapshots_dir}")

            # 첫 번째 해시 폴더 선택
            base_path = os.path.join(snapshots_dir, subdirs[0])
            print(f"[INFO] Auto-selected snapshot dir: {base_path}")

        # config.json 확인
        config_file = os.path.join(base_path, "config.json")
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"config.json not found in {base_path}")

        config_path = config_file

    # ④ 로드
    return utils.get_hparams_from_file(config_path)



def load_or_download_model_orig(locale, device, use_hf=True, ckpt_path=None, local_repo_path_dict=None):
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
        assert local_repo_path_dict is not None, \
            "local_repo_path_dict must be provided when use_hf=False"

        assert language in local_repo_path_dict, \
            f"{language} not found in local_repo_path_dict"

        ckpt_path = os.path.join(local_repo_path_dict[language], "checkpoint.pth")

    return torch.load(ckpt_path, map_location=device)


def load_or_download_model(
    locale,
    device,
    use_hf=True,
    ckpt_path=None,
    local_repo_path_dict=None,
    skip_snap_seed=True
):
    print("LOAD_OR_DOWNLOAD_MODEL")
    language = locale.split('-')[0].upper()

    # ① 명시적으로 ckpt_path가 주어진 경우
    if ckpt_path is not None:
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}")
        return torch.load(ckpt_path, map_location=device)

    # ② Hugging Face에서 받는 경우
    if use_hf:
        try:
            assert language in LANG_TO_HF_REPO_ID
            ckpt_path = hf_hub_download(
                repo_id=LANG_TO_HF_REPO_ID[language],
                filename="checkpoint.pth"
            )
        except Exception as e:
            print(f"[WARN] Hugging Face download failed: {e}")
            use_hf = False  # fallback

    # ③ 로컬에서 불러오는 경우
    if not use_hf:
        assert local_repo_path_dict is not None, \
            "local_repo_path_dict must be provided when use_hf=False"
        assert language in local_repo_path_dict, \
            f"{language} not found in local_repo_path_dict"

        base_path = local_repo_path_dict[language]

        # ✅ skip_snap_seed=True일 경우: snapshots/<hash> 자동 탐색
        if skip_snap_seed:
            snapshots_dir = os.path.join(base_path, "snapshots")
            if not os.path.isdir(snapshots_dir):
                raise FileNotFoundError(f"'snapshots' directory not found in {base_path}")

            subdirs = [
                d for d in os.listdir(snapshots_dir)
                if os.path.isdir(os.path.join(snapshots_dir, d))
            ]
            if not subdirs:
                raise FileNotFoundError(f"No snapshot subdirectories found in {snapshots_dir}")

            # 첫 번째 hash 폴더 선택
            base_path = os.path.join(snapshots_dir, subdirs[0])
            print(f"[INFO] Auto-selected snapshot dir: {base_path}")

        # checkpoint.pth 확인
        ckpt_path = os.path.join(base_path, "checkpoint.pth")
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"checkpoint.pth not found in {base_path}")

    # ④ 모델 로드
    print(f"[INFO] Loading model from: {ckpt_path}")
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

PRETRAINED_MODELS = {
    'G.pth': 'https://myshell-public-repo-host.s3.amazonaws.com/openvoice/basespeakers/pretrained/G.pth',
    'D.pth': 'https://myshell-public-repo-host.s3.amazonaws.com/openvoice/basespeakers/pretrained/D.pth',
    'DUR.pth': 'https://myshell-public-repo-host.s3.amazonaws.com/openvoice/basespeakers/pretrained/DUR.pth',
}