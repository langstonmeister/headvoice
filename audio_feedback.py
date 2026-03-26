import os
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time

def apply_fade(data, fade_duration=0.5, samplerate=16000):
    total_samples = len(data)
    fade_samples = int(fade_duration * samplerate)

    if fade_samples * 2 > total_samples:
        fade_samples = total_samples // 2

    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    data[:fade_samples] *= fade_in[:, np.newaxis] if data.ndim > 1 else fade_in
    data[-fade_samples:] *= fade_out[:, np.newaxis] if data.ndim > 1 else fade_out

    return data

def play_processing_sound(filename="ffharp.wav", fade_duration=0.5, overlap=0.5):
    def _play():
        if not os.path.exists(filename):
            return
        data, samplerate = sf.read(filename, dtype='float32')
        data = apply_fade(data, fade_duration, samplerate)
        sd.play(data, samplerate)
        time.sleep(overlap)  # allow partial overlap before continuing

    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
