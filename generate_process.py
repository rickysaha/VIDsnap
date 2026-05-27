import shutil
import subprocess
import time
from pathlib import Path

from supabase_client import supabase
from texttoaudio import text_to_speech_file


UPLOAD_DIR = Path("upload_folder")
REELS_DIR = Path("static/reels")
DONE_FILE = Path("done.txt")
BUCKET_NAME = "uploads"

VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)


def log(message):
    print(message, flush=True)


def ensure_done_file():
    if not DONE_FILE.exists():
        DONE_FILE.write_text("")
        log("Created missing done.txt")


def read_done_folders():
    ensure_done_file()
    with DONE_FILE.open("r") as f:
        return {line.strip() for line in f if line.strip()}


def mark_done(folder):
    with DONE_FILE.open("a") as f:
        f.write(f"{folder}\n")


def run_ffmpeg(command):
    log("Running FFmpeg command:")
    log(" ".join(f'"{part}"' if " " in part else part for part in command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    log(f"FFmpeg return code: {result.returncode}")
    log("FFmpeg STDOUT:")
    log(result.stdout or "<empty>")
    log("FFmpeg STDERR:")
    log(result.stderr or "<empty>")

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed with return code "
            f"{result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )

    return result


def require_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg was not found on PATH. On Railway, install ffmpeg in the runtime "
            "image with railpack.json deploy.aptPackages or with the "
            "RAILPACK_DEPLOY_APT_PACKAGES=ffmpeg service variable, then redeploy."
        )


def safe_folder_name(folder):
    return Path(folder).name == folder and folder not in ("", ".", "..")


def list_supabase_folders():
    try:
        response = supabase.storage.from_(BUCKET_NAME).list()
    except Exception as exc:
        log(f"Could not list Supabase bucket '{BUCKET_NAME}': {exc}")
        return []

    folders = []
    for item in response or []:
        name = item.get("name")
        if name and safe_folder_name(name):
            folders.append(name)
    return folders


def sync_folder_from_supabase(folder):
    if not safe_folder_name(folder):
        log(f"Skipping unsafe Supabase folder name: {folder}")
        return

    folder_path = UPLOAD_DIR / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    try:
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
    except Exception as exc:
        log(f"Could not list Supabase folder '{folder}': {exc}")
        return

    for item in files or []:
        file_name = item.get("name")
        if not file_name or "/" in file_name or file_name in (".", ".."):
            continue

        local_path = folder_path / file_name
        if local_path.exists() and local_path.stat().st_size > 0:
            continue

        try:
            log(f"Downloading {folder}/{file_name} from Supabase")
            data = supabase.storage.from_(BUCKET_NAME).download(f"{folder}/{file_name}")
            local_path.write_bytes(data)
        except Exception as exc:
            log(f"Could not download {folder}/{file_name}: {exc}")


def sync_pending_supabase_folders(done_folders):
    for folder in list_supabase_folders():
        if folder not in done_folders:
            sync_folder_from_supabase(folder)


def get_processable_folders():
    folders = []

    if not UPLOAD_DIR.exists():
        return folders

    for folder_path in sorted(UPLOAD_DIR.iterdir()):
        if not folder_path.is_dir():
            continue

        desc_path = folder_path / "desc.txt"
        if desc_path.exists() and desc_path.stat().st_size > 0:
            folders.append(folder_path.name)
        else:
            log(f"Skipping {folder_path.name}: missing or empty desc.txt")

    return folders


def get_media_files(folder_path):
    files = sorted(
        path
        for path in folder_path.iterdir()
        if path.is_file()
        and path.name not in ("desc.txt", "audio.mp3", "input.txt")
        and path.suffix.lower() in VIDEO_EXTENSIONS + IMAGE_EXTENSIONS
    )

    video_files = [path for path in files if path.suffix.lower() in VIDEO_EXTENSIONS]
    image_files = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]

    return video_files, image_files


def text_to_audio(folder):
    folder_path = UPLOAD_DIR / folder
    desc_path = folder_path / "desc.txt"
    audio_path = folder_path / "audio.mp3"

    if not desc_path.exists() or desc_path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty description file: {desc_path}")

    if audio_path.exists() and audio_path.stat().st_size > 0:
        log(f"Audio already exists for {folder}: {audio_path}")
        return audio_path

    text = desc_path.read_text().strip()
    if not text:
        raise ValueError(f"Description is empty: {desc_path}")

    log(f"Generating audio for folder: {folder}")
    generated_path = Path(text_to_speech_file(text, folder))

    if not generated_path.exists() or generated_path.stat().st_size == 0:
        raise FileNotFoundError(f"Audio generation did not create a valid file: {generated_path}")

    return generated_path


def create_image_concat_file(folder_path, image_files):
    input_path = folder_path / "input.txt"

    if not image_files:
        raise FileNotFoundError(f"No images found and no video found in {folder_path}")

    if input_path.exists() and input_path.stat().st_size > 0:
        log(f"Regenerating image concat input with absolute paths: {input_path}")

    log(f"Creating image concat input: {input_path}")
    lines = []

    for image_path in image_files:
        lines.append(f"file '{image_path.resolve().as_posix()}'")
        lines.append("duration 2")

    lines.append(f"file '{image_files[-1].resolve().as_posix()}'")
    input_path.write_text("\n".join(lines) + "\n")

    if not input_path.exists() or input_path.stat().st_size == 0:
        raise FileNotFoundError(f"Failed to create concat input: {input_path}")

    return input_path


def verify_common_inputs(folder_path, audio_path):
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    if not any(folder_path.iterdir()):
        raise FileNotFoundError(f"Folder is empty: {folder_path}")

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty audio.mp3: {audio_path}")


def create_reel(folder):
    require_ffmpeg()

    folder_path = UPLOAD_DIR / folder
    output_file = REELS_DIR / f"{folder}.mp4"
    audio_path = folder_path / "audio.mp3"

    verify_common_inputs(folder_path, audio_path)

    video_files, image_files = get_media_files(folder_path)

    if not video_files and not image_files:
        raise FileNotFoundError(f"No uploaded video or image files found in {folder_path}")

    if video_files:
        input_video = video_files[0]
        log(f"Creating reel from video: {input_video}")

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",  # suppress swscaler and other warnings
            "-i",
            str(input_video),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            "setsar=1",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            str(output_file),
        ]
    else:
        input_txt = create_image_concat_file(folder_path, image_files)

        if not input_txt.exists() or input_txt.stat().st_size == 0:
            raise FileNotFoundError(f"Missing or empty input.txt: {input_txt}")

        log(f"Creating reel from image slideshow: {input_txt}")

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",  # suppress swscaler and other warnings
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(input_txt),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            "setsar=1,fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_file),
        ]

    run_ffmpeg(command)

    if not output_file.exists() or output_file.stat().st_size == 0:
        raise FileNotFoundError(f"FFmpeg completed but output file is missing or empty: {output_file}")

    log(f"Created reel: {output_file}")
    upload_reel(folder, output_file)

    return output_file


def upload_reel(folder, output_file):
    storage_path = f"{folder}/{folder}.mp4"
    log(f"Uploading generated reel to Supabase: {BUCKET_NAME}/{storage_path}")

    with output_file.open("rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            storage_path,
            f,
            file_options={
                "content-type": "video/mp4",
                "upsert": "true",
            },
        )

    log(f"Uploaded generated reel: {storage_path}")


def process_folder(folder):
    log(f"Processing folder: {folder}")
    text_to_audio(folder)
    create_reel(folder)
    mark_done(folder)
    log(f"Finished folder: {folder}")


def main():
    ensure_done_file()

    while True:
        log("Worker tick: checking for pending folders")

        try:
            require_ffmpeg()
        except Exception as exc:
            log(f"Dependency error: {exc}")
            time.sleep(4)
            continue

        done_folders = read_done_folders()
        sync_pending_supabase_folders(done_folders)

        folders = get_processable_folders()
        pending_folders = [folder for folder in folders if folder not in done_folders]

        log(f"Found folders: {folders}")
        log(f"Done folders: {sorted(done_folders)}")
        log(f"Pending folders: {pending_folders}")

        for folder in pending_folders:
            try:
                process_folder(folder)
            except Exception as exc:
                log(f"ERROR while processing {folder}: {exc}")

        time.sleep(4)


if __name__ == "__main__":
    main()
