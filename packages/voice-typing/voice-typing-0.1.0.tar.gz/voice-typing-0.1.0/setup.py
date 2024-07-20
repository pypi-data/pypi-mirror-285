from setuptools import setup, find_packages

setup(
    name='voice-typing',
    version='0.1.0',
    description='A voice typing application using tkinter and speech recognition',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Er. Harsh Raj',
    author_email='your-email@example.com',
    url='https://github.com/yourusername/voice-typing',
    packages=find_packages(),
    install_requires=[
        'pyautogui',
        'SpeechRecognition',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'voice-typing=voice_typing.main:main',
        ],
    },
)
