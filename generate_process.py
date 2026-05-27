import os
import time
import subprocess
from mutagen.mp3 import MP3
from texttoaudio import text_to_speech_file

def text_to_audio(folder):

    print("Text to audio:", folder)

    # READ TEXT
    with open(f"upload_folder/{folder}/desc.txt") as f:

        text = f.read()

    # READ SELECTED VOICE
    with open(f"upload_folder/{folder}/voice.txt") as f:

        voice_id = f.read().strip()

    print(text, folder, voice_id)

    # GENERATE AUDIO
    text_to_speech_file(

        text,

        folder,

        voice_id

    )
def create_reel(folder):

    folder_path = f"upload_folder/{folder}"

    files = os.listdir(folder_path)

    video_extensions = (".mp4", ".mov", ".avi", ".mkv")

    video_file = None

    # ====================================
    # CHECK VIDEO FILE
    # ====================================
    for file in files:

        if file.lower().endswith(video_extensions):

            video_file = file

            break

    output_file = f"static/reels/{folder}.mp4"

    # ====================================
    # VIDEO CASE
    # ====================================
    if video_file:

        command = f'''
        ffmpeg -y \
        -i "{folder_path}/{video_file}" \
        -i "{folder_path}/audio.mp3" \
        -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
        -map 0:v:0 \
        -map 1:a:0 \
        -c:v libx264 \
        -c:a aac \
        -shortest \
        -r 30 \
        -pix_fmt yuv420p \
        "{output_file}"
        '''

    # ====================================
    # IMAGE CASE
    # ====================================
    else:

        # GET IMAGE FILES
        image_files = []

        for file in files:

            if file.lower().endswith((".jpg", ".jpeg", ".png")):

                image_files.append(file)

        # NO IMAGES
        if len(image_files) == 0:

            print("No images found")

            return

        # AUDIO PATH
        audio_path = os.path.join(folder_path, "audio.mp3")

        # GET AUDIO DURATION
        audio = MP3(audio_path)

        audio_duration = audio.info.length

        print("Audio Duration:", audio_duration)

        # CALCULATE DURATION PER IMAGE
        duration_per_image = audio_duration / len(image_files)

        print("Duration Per Image:", duration_per_image)

        # CREATE INPUT.TXT
        input_txt_path = os.path.join(folder_path, "input.txt")

        with open(input_txt_path, "w") as f:

            for img in image_files:

                full_path = os.path.abspath(
                    os.path.join(folder_path, img)
                )

                f.write(f"file '{full_path}'\n")
                f.write(f"duration {duration_per_image}\n")

            # REPEAT LAST IMAGE
            last_image = os.path.abspath(
                os.path.join(folder_path, image_files[-1])
            )

            f.write(f"file '{last_image}'\n")

        # CREATE VIDEO
        command = f'''
        ffmpeg -y \
        -f concat -safe 0 \
        -i "{input_txt_path}" \
        -i "{audio_path}" \
        -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
        -c:v libx264 \
        -c:a aac \
        -shortest \
        -r 30 \
        -pix_fmt yuv420p \
        "{output_file}"
        '''

    # ====================================
    # RUN FFMPEG
    # ====================================
    subprocess.run(command, shell=True, check=True)

    # ====================================
    # DELETE CORRUPTED VIDEOS
    # ====================================
    if os.path.exists(output_file):

        if os.path.getsize(output_file) < 100000:

            print("Corrupted reel deleted")

            os.remove(output_file)

            return

    print("Create reel:", folder)


if __name__ == "__main__":

    while True:

        print("processing...")

        # CREATE done.txt IF NOT EXISTS
        if not os.path.exists("done.txt"):

            with open("done.txt", "w") as f:
                pass

        # READ DONE FOLDERS
        with open("done.txt", "r") as f:

            done_folders = f.readlines()

        done_folders = [x.strip() for x in done_folders]

        # GET VALID FOLDERS
        folders = [
            folder
            for folder in os.listdir("upload_folder")
            if os.path.isdir(os.path.join("upload_folder", folder))
            and os.path.exists(
                os.path.join("upload_folder", folder, "desc.txt")
            )
        ]

        print(folders, done_folders)

        for folder in folders:

            if folder not in done_folders:

                try:

                    # GENERATE AUDIO
                    text_to_audio(folder)

                    # CREATE REEL
                    create_reel(folder)

                    # MARK AS DONE
                    with open("done.txt", "a") as f:

                        f.write(folder + "\n")

                except Exception as e:

                    print("ERROR:", e)

        time.sleep(4)