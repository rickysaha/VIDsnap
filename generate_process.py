import os
from texttoaudio import text_to_speech_file
import subprocess


def text_to_audio(folder):

    print("Text to audio:", folder)

    with open(f"upload_folder/{folder}/desc.txt") as f:
        text = f.read()

    print(text, folder)

    text_to_speech_file(text, folder)


def create_reel(folder):

    output_file = f"static/reels/{folder}.mp4"

    command = f'ffmpeg -f concat -safe 0 -i upload_folder/{folder}/input.txt -i upload_folder/{folder}/audio.mp3 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p {output_file}'

    subprocess.run(command, shell=True, check=True)

    print("Create reel:", folder)