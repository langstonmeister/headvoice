from setuptools import setup

setup(
    name='headvoice',
    version='0.1.0',
    py_modules=['main', 'config', 'mic_listener', 'wake_word_listener', 'voice_output', 'llm_interface'],
    install_requires=[
        'pvporcupine',
        'pyaudio',
        'sox',
        'sounddevice',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'lxml',
        'openai',
        'platformdirs',
    ],
)
