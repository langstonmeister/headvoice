import numpy as np
import sounddevice as sd
from openwakeword.model import Model

CHUNK_SIZE = 1280   # ~80ms of audio at 16kHz
SAMPLE_RATE = 16000
THRESHOLD = 0.5


class WakeWordDetector:
    def __init__(self, model_path: str = None, threshold: float = THRESHOLD):
        """
        model_path: path to a custom openWakeWord .onnx model file, or None to
                    use the built-in 'hey_jarvis' pre-trained model as a stand-in
                    until a custom 'Hey Tavi' model is trained.
        """
        if model_path:
            self.model = Model(wakeword_models=[model_path], inference_framework="onnx")
        else:
            self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        self.threshold = threshold

    def listen(self):
        print("👂 Listening for wake word...")
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                            blocksize=CHUNK_SIZE) as stream:
            while True:
                audio_data, _ = stream.read(CHUNK_SIZE)
                prediction = self.model.predict(audio_data.flatten())
                for score in prediction.values():
                    if score > self.threshold:
                        print("🟢 Wake word detected!")
                        return

    def close(self):
        pass  # InputStream is managed by the context manager inside listen()
