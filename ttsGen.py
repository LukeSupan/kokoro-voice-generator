"""
tts generator - with kokoro
do this:
    pip install kokoro soundfile numpy
for windows at least, get this:
    https://github.com/espeak-ng/espeak-ng/releases
call it like this:
    run.bat script.txt
    run.bat script.txt --voice am_adam --speed 1
    run.bat script*.txt --voice am_michael
if you dont have run.bat:
    python ttsGen.py script.txt
    python ttsGen.py script.txt --voice am_adam --speed 1
output is auto-named from input, e.g. script.txt -> script.wav
voice list:
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
import os
import sys
import numpy as np
import soundfile as sf
from kokoro import KPipeline


def load_script(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"error: could not find file '{filepath}'")
        sys.exit(1)
    except Exception as e:
        print(f"error reading file: {e}")
        sys.exit(1)


def generate_audio(pipeline, script_text, voice, speed, output_file, sample_rate=24000):
    print(f"  voice: {voice} | speed: {speed}")
    print(f"  output: {output_file}")
    print(f"  generating audio. takes a bit...")
    all_audio = []
    for _, _, audio in pipeline(script_text, voice=voice, speed=speed):
        all_audio.append(audio)
    if not all_audio:
        print("  no audio was generated. check your input file.")
        return
    final_audio = np.concatenate(all_audio)
    sf.write(output_file, final_audio, sample_rate)
    duration = len(final_audio) / sample_rate
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    print(f"  done - {minutes}m {seconds}s saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate TTS narration from script files using Kokoro.")
    parser.add_argument("inputs", nargs='+',              help="One or more .txt script files")
    parser.add_argument("--voice", default="am_michael",  help="Kokoro voice (default: am_michael)")
    parser.add_argument("--speed", default=0.95, type=float, help="Speech speed (default: 0.95)")
    args = parser.parse_args()

    print("loading kokoro pipeline...")
    pipeline = KPipeline(lang_code='a')  # american english
    print(f"processing {len(args.inputs)} file(s)\n")

    for i, filepath in enumerate(args.inputs):
        base = os.path.splitext(os.path.basename(filepath))[0]
        output_file = f"{base}.wav"
        print(f"[{i+1}/{len(args.inputs)}] {filepath}")
        raw_text = load_script(filepath)
        word_count = len(raw_text.split())
        print(f"  words: {word_count} (~{round(word_count / 140)} min)")
        generate_audio(pipeline, raw_text, args.voice, args.speed, output_file)
        print()


if __name__ == "__main__":
    main()