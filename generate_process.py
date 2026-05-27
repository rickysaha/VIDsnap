import os
import time
from texttoaudio import text_to_speech_file
import subprocess
os.makedirs("upload_folder", exist_ok=True)
os.makedirs("static/reels", exist_ok=True)


def text_to_audio(folder):

    print("Text to audio:", folder)

    with open(f"upload_folder/{folder}/desc.txt") as f:
        text = f.read()

    print(text, folder)

    text_to_speech_file(text, folder)


def create_reel(folder):

    folder_path = f"upload_folder/{folder}"

    files = os.listdir(folder_path)

    video_extensions = (".mp4", ".mov", ".avi", ".mkv")

    video_file = None

    for file in files:
        if file.lower().endswith(video_extensions):
            video_file = file
            break

    output_file = f"static/reels/{folder}.mp4"

    # VIDEO CASE
    if video_file:

        command = f'''
        ffmpeg -i "{folder_path}/{video_file}" \
        -i "{folder_path}/audio.mp3" \
        -c:v libx264 \
        -c:a aac \
        -shortest \
        "{output_file}"
        '''

    # IMAGE CASE
    else:

        command = f'''
        ffmpeg -f concat -safe 0 \
        -i "{folder_path}/input.txt" \
        -i "{folder_path}/audio.mp3" \
        -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
        -c:v libx264 \
        -c:a aac \
        -shortest \
        -r 30 \
        -pix_fmt yuv420p \
        "{output_file}"
        '''

    subprocess.run(command, shell=True, check=True)

    print("Create reel:", folder)


if __name__ == "__main__":

    while True:

        print("processing...")

        with open("done.txt", "r") as f:

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

                try:

                    text_to_audio(folder)

                    create_reel(folder)

                    with open("done.txt", "a") as f:
                        f.write(folder + "\n")

                except Exception as e:

                    print("ERROR:", e)

        time.sleep(4)