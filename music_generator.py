# music_generator.py
import os
import numpy as np
import torch
import soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from config import Config

try:
    from pydub import AudioSegment
    PydubAvailable = True
except ImportError:
    PydubAvailable = False


class MusicGenerator:
    def __init__(self, device="cpu"):
        # Force CPU
        self.device = "cpu"
        self.model_name = Config.MUSICGEN_MODEL
        self.sr = Config.MUSICGEN_SAMPLING_RATE
        self.model = None
        self.processor = None
        self._load_model()

    def _load_model(self):
        """Load Hugging Face processor and model into memory (CPU only)."""
        if self.model is None:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                self.model_name
            ).to(self.device)
            self.model.eval()

    def _postprocess(self, audio_tensor):
        """
        Convert model output tensor to float32 numpy array in [-1,1].
        Handles shapes (batch, channels, samples) or (channels, samples).
        """
        arr = audio_tensor.detach().cpu().numpy()

        if arr.ndim == 3:  # (batch, channels, samples)
            arr = arr[0]
        if arr.ndim == 2:  # (channels, samples)
            arr = np.mean(arr, axis=0)  # convert to mono

        # Normalize
        maxv = np.max(np.abs(arr)) or 1e-8
        return (arr / maxv * 0.95).astype(np.float32)

    def generate_music(self, prompt: str, duration: int = Config.MUSICGEN_DURATION,
                       temperature: float = Config.TEMPERATURE, seed: int = None):
        """
        Generate music from a text prompt.

        Args:
            prompt: description of music
            duration: target length in seconds
            temperature: sampling temperature
            seed: RNG seed for reproducibility

        Returns:
            audio_arr: float32 numpy array at sampling rate self.sr
        """
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)

        inputs = self.processor(text=[prompt], return_tensors="pt").to(self.device)

        # Compute tokens based on duration
        tokens_per_second = getattr(Config, "TOKENS_PER_SECOND", 50)
        max_new_tokens = int(tokens_per_second * duration)

        with torch.no_grad():
            audio_out = self.model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                max_new_tokens=max_new_tokens
            )

        audio_tensor = audio_out[0]  # first batch
        audio_arr = self._postprocess(audio_tensor)
        return audio_arr

    def save_audio(self, audio_array: np.ndarray, out_path: str):
        """
        Save audio to WAV and optionally MP3.
        Returns (wav_path, mp3_path or None).
        """
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        wav_path = out_path if out_path.endswith(".wav") else out_path + ".wav"

        # Save WAV
        sf.write(wav_path, audio_array, self.sr, format="WAV", subtype="PCM_16")

        # Save MP3 (if pydub + ffmpeg available)
        mp3_path = wav_path.replace(".wav", ".mp3")
        if PydubAvailable:
            try:
                AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3", bitrate=Config.AUDIO_BITRATE)
            except Exception:
                mp3_path = None
        else:
            mp3_path = None

        return wav_path, mp3_path
