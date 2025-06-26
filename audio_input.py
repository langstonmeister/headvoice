import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import whisper

SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5  # seconds
FILENAME = "recording.wav"

def record_audio(duration=DURATION, samplerate=SAMPLE_RATE, filename=FILENAME):
    print(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=CHANNELS, dtype="int16")
    sd.wait()
    scipy.io.wavfile.write(filename, samplerate, audio)
    print(f"✅ Audio saved to {filename}")
    return filename

def transcribe_audio(filename=FILENAME):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    print(f"🧠 Whisper heard: {result['text']}")
    return result["text"]

if __name__ == "__main__":
    audio_file = record_audio()
    transcribe_audio(audio_file)
