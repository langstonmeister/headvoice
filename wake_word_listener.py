import pvporcupine
import pyaudio
import struct

class WakeWordDetector:
    def __init__(self, keyword_path):
        self.porcupine = pvporcupine.create(keyword_paths=[keyword_path])
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen(self):
        print("👂 Listening for 'Tavi'...")
        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            if self.porcupine.process(pcm) >= 0:
                print("🟢 Wake word 'Tavi' detected!")
                return

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.porcupine.delete()
