import subprocess

def speak(text: str):
    print(f"🗣️ Tavi says: {text}")
    try:
        subprocess.run(["say", text])
    except Exception as e:
        print("⚠️ TTS error:", e)

if __name__ == "__main__":
    speak("Hello. I'm Tavi.")
