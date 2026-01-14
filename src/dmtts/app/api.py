import os
import re
import json
import torch
import librosa
import soundfile
import torchaudio
import numpy as np
import torch.nn as nn
from tqdm import tqdm
import torch

from dmtts.utils import hparam_utils as utils
from dmtts.model import commons
from dmtts.model.synthesizer import SynthesizerTrn
from dmtts.utils.split_utils import split_sentence
from dmtts.utils.download_utils import load_or_download_config, load_or_download_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TTS(nn.Module):
    def __init__(self, 
                language, # lang_list를 받아도 됨
                device='auto',
                use_hf=True,
                config_path=None,
                ckpt_path=None,
                local_repo_path_dict=None,
                skip_snap_seed=True,
                ):
        super().__init__()
        if device == 'auto':
            device = 'cpu'
            if torch.cuda.is_available(): device = 'cuda'
            if torch.backends.mps.is_available(): device = 'mps'
        if 'cuda' in device:
            assert torch.cuda.is_available()

        hps = load_or_download_config(language, use_hf=use_hf, config_path=config_path, local_repo_path_dict=local_repo_path_dict, skip_snap_seed=skip_snap_seed)

        num_languages = hps.num_languages
        num_tones = hps.num_tones
        symbols = hps.symbols
        lang_list = hps.data.lang_list

        model = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            num_tones=num_tones,
            num_languages=num_languages,
            lang_list= lang_list,
            **hps.model,
        ).to(device)

        model.eval()
        self.model = model
        self.symbol_to_id = {s: i for i, s in enumerate(symbols)}
        self.hps = hps
        self.device = device
    
        # load state_dict: parameter
        checkpoint_dict = load_or_download_model(language, device, use_hf=use_hf, ckpt_path=ckpt_path,local_repo_path_dict=local_repo_path_dict,skip_snap_seed=skip_snap_seed)
        self.model.load_state_dict(checkpoint_dict['model'], strict=True)
        
        language = language.split('_')[0] # for multi-lingual: FUTURE WORK
        self.language = language 
        
        
        
        self.lang_list= lang_list
    @staticmethod
    def audio_numpy_concat(segment_data_list, sr, speed=1.):
        audio_segments = []
        for segment_data in segment_data_list:
            audio_segments += segment_data.reshape(-1).tolist()
            audio_segments += [0] * int((sr * 0.05) / speed)
        audio_segments = np.array(audio_segments).astype(np.float32)
        return audio_segments

    @staticmethod
    def split_sentences_into_pieces(text, language, quiet=False):
        # print(f"def split_senteces in to piees: {text}")
        texts = split_sentence(text, language_str=language)
        if not quiet:
            print(" > Text split to sentences.")
            print('\n'.join(texts))
            print(" > ===========================")
        return texts

    ## inference
    def tts_to_file(self, text, speaker_id, output_path=None, sdp_ratio=0.2, noise_scale=0.6, noise_scale_w=0.8, speed=1.0, pbar=None, format=None, position=None, quiet=False,):
        language = self.language
        texts = self.split_sentences_into_pieces(text, language, quiet)
        #print("HIHIHIHIHHIHHIHIH")
        print(f"tts_to_file input text: {texts}")
        audio_list = []
        if pbar:
            tx = pbar(texts)
        else:
            if position:
                tx = tqdm(texts, position=position)
            elif quiet:
                tx = texts
            else:
                tx = tqdm(texts)
        for t in tx:
            if language in ['EN', 'ZH_MIX_EN']:
                t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t)
            ################################################################
            # if language in ['JP']:
            #     t = t.strip()
            #     # ① “hello_jp_tolerance”는 미리 녹음된 wav로 대체
            #     if "hello_jp_tolerance" in t:
            #         hello_path = os.path.join(BASE_DIR, "..", "assets", "hello_jp_tolerance.wav")

            #         #hello_path = os.path.join(BASE_DIR, "hello_jp_tolerance.wav")
            #         hello_audio, sr = soundfile.read(hello_path)
            #         hello_audio = hello_audio.astype(np.float32)
            #         audio_list.append(hello_audio)
            #         # 50ms silence 추가 (자연스러운 연결)
            #         audio_list.append(np.zeros(int(sr * 0.05), dtype=np.float32))
            #         continue
            ################################################################
            device = self.device
            phones, tones, lang_ids = utils.get_text_for_tts_infer(t, language, self.hps, device, self.lang_list)

            with torch.no_grad():
                x_tst = phones.to(device).unsqueeze(0)
                tones = tones.to(device).unsqueeze(0)
                lang_ids = lang_ids.to(device).unsqueeze(0)

                x_tst_lengths = torch.LongTensor([phones.size(0)]).to(device)
                del phones
                speakers = torch.LongTensor([speaker_id]).to(device)
                audio = self.model.infer(
                        x_tst,
                        x_tst_lengths,
                        speakers,
                        tones,
                        lang_ids,
                        sdp_ratio=sdp_ratio,
                        noise_scale=noise_scale,
                        noise_scale_w=noise_scale_w,
                        length_scale=1. / speed,
                    )[0][0, 0].data.cpu().float().numpy()
                del x_tst, tones, lang_ids, x_tst_lengths, speakers


            audio_list.append(audio)
        torch.cuda.empty_cache()
        audio = self.audio_numpy_concat(audio_list, sr=self.hps.data.sampling_rate, speed=speed)

        if output_path is None:
            return audio
        else:
            if format:
                soundfile.write(output_path, audio, self.hps.data.sampling_rate, format=format)
            else:
                soundfile.write(output_path, audio, self.hps.data.sampling_rate)
