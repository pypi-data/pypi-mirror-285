from setuptools import setup, find_packages

setup(
    name='vocalverse',
    version='1.1.0',
    author='Vamshi Krishna Madhavan',
    author_email='vamshi-madhavan@outlook.com',
    description='A package for Text Translation, Speech Synthesis, and Audio Transcription Toolkit"',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Vamshi0104/vocalverse',
    packages=find_packages(),
    install_requires=[
        'pygame',
        'googletrans-py',
        'gtts',
        'pyaudio',
        'pydub',
        'openai-whisper'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
