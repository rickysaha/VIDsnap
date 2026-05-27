import os
import time
from texttoaudio import text_to_speech_file
import subprocess


def text_to_audio(folder):
    print("Text to audio:", folder)
    with open(f"upload_folder/{folder}/desc.txt") as f:
        text = f.read()
    print(text,folder)
    text_to_speech_file(text, folder)


def create_reel(folder):
    output_file = f"static/reels/{folder}.mp4"
    command=command = f'ffmpeg -f concat -safe 0 -i upload_folder/{folder}/input.txt -i upload_folder/{folder}/audio.mp3 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p {output_file}'
    
    subprocess.run(command, shell=True, check=True)
    print("Create reel:", folder)


if __name__ == "__main__":
    while True:
     print("processing...")
     with open("done.txt","r") as f:
        done_folders = f.readlines()
        done_folders = [x.strip() for x in done_folders]
        folders = [
            folder
            for folder in os.listdir("upload_folder")
            if os.path.isdir(os.path.join("upload_folder", folder))
            and os.path.exists(os.path.join("upload_folder", folder, "desc.txt"))
        ]
        print(folders, done_folders)
        for folder in folders:
         if folder not in done_folders:
          text_to_audio(folder)
          create_reel(folder)
          with open("done.txt","a") as f:
             f.write(folder+"\n")
        time.sleep(4)
