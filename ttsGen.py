"""
tts generator - with kokoro


do this:
    pip install kokoro soundfile numpy

for windows at least, get this:
    https://github.com/espeak-ng/espeak-ng/releases

call it like this, with specific model or whatever:
    run.bat input.txt
    run.bat input.txt --voice am_adam --speed 1 --output ttsOutput.wav

i had to make a run.bat to run python 11 instead of 14 without too much hassle. if you dont:
    python ttsGen.py script.txt
    python ttsGen.py script.txt --voice am_adam --speed 1 --output ttsOutput.wav

voice list
af_heart    — warm, natural female (recommended)
af_nova     — clear, neutral female
af_sarah    — slightly warmer female
am_adam     — natural male
am_michael  — deeper male (default)
bf_emma     — British female
bm_george   — British male

this is intended for premiere pro. for like a youtube video
"""

import argparse
import re
import sys
import numpy as np
import soundfile as sf
from kokoro import KPipeline



def load_script(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: could not find file '{filepath}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def generate_audio(script_text, voice, speed, output_file, sample_rate=24000):
    print(f"\nloading kokoro")
    pipeline = KPipeline(lang_code='a')  # english american

    print(f"voice: {voice} | speed: {speed}")
    print(f"output: {output_file}")
    print(f"generating audio. takes a bit\n")

    all_audio = []

    for i, (_, _, audio) in enumerate(pipeline(script_text, voice=voice, speed=speed)):
        all_audio.append(audio)

    if not all_audio:
        print("no audio was generated. check your input file.")
        sys.exit(1)

    final_audio = np.concatenate(all_audio)
    sf.write(output_file, final_audio, sample_rate)

    duration = len(final_audio) / sample_rate
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    print(f"\ndone")
    print(f"  saved to : {output_file}")
    print(f"  duration : {minutes}m {seconds}s")

def main():
    parser = argparse.ArgumentParser(description="Generate TTS narration from a script file using Kokoro.")
    parser.add_argument("input",                           help="Path to your .txt script file")
    parser.add_argument("--voice",  default="am_michael",  help="Kokoro voice to use (default: am_michael)")
    parser.add_argument("--speed",  default=0.95, type=float, help="Speech speed (default: 0.95)")
    parser.add_argument("--output", default="narration.wav", help="Output WAV file (default: narration.wav)")
    args = parser.parse_args()

    print(f"Reading script from: {args.input}")
    raw_text = load_script(args.input)

    word_count = len(raw_text.split())
    print(f"Word count: {word_count} (~{round(word_count / 140)} min at 140wpm)")

    generate_audio(raw_text, args.voice, args.speed, args.output)


if __name__ == "__main__":
    main()