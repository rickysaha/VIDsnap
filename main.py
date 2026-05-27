from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os
from supabase_client import supabase

UPLOAD_FOLDER = 'upload_folder'

ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'mp4',
    'mov',
    'avi',
    'mkv'
}

app = Flask(__name__)

os.makedirs("upload_folder", exist_ok=True)
os.makedirs("static/reels", exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():

    myid = uuid.uuid1()

    if request.method == "POST":

        print(request.files.keys())

        rec_id = request.form.get("uuid")
        desc = request.form.get("text")

        input_files = []

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)

        os.makedirs(folder_path, exist_ok=True)

        for key, value in request.files.items():

            print(key, value)

            file = request.files[key]

            if file:

                filename = secure_filename(file.filename)

                file_path = os.path.join(folder_path, filename)

                # save locally
                file.save(file_path)

                # upload original file to supabase
                with open(file_path, "rb") as f:

                    supabase.storage.from_("uploads").upload(
                        f"{rec_id}/{filename}",
                        f,
                        file_options={"upsert": "true"}
                    )

                input_files.append(filename)

                print(filename)

        # save description locally
        desc_path = os.path.join(folder_path, "desc.txt")

        with open(desc_path, "w") as f:

            f.write(desc)

        # upload description to supabase
        with open(desc_path, "rb") as f:

            supabase.storage.from_("uploads").upload(
                f"{rec_id}/desc.txt",
                f,
                file_options={"upsert": "true"}
            )

        # create input.txt
        input_txt_path = os.path.join(folder_path, "input.txt")

        with open(input_txt_path, "w") as f:

            for fl in input_files:

                ext = fl.split(".")[-1].lower()

                # VIDEO CASE
                if ext in ["mp4", "mov", "avi", "mkv"]:

                    f.write(f"file '{fl}'\n")

                # IMAGE CASE
                else:

                    f.write(f"file '{fl}'\n")
                    f.write("duration 1\n")

            # repeat last image for ffmpeg slideshow
            if input_files:

                last_file = input_files[-1]

                if not last_file.lower().endswith(("mp4", "mov", "avi", "mkv")):

                    f.write(f"file '{last_file}'\n")

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():

    response = supabase.storage.from_("uploads").list()

    reels = []

    for folder in response:

        folder_name = folder["name"]

        files = supabase.storage.from_("uploads").list(folder_name)

        for file in files:

            file_name = file["name"].lower()

            # ONLY SHOW VIDEOS
            if file_name.endswith((".mp4", ".mov", ".avi", ".mkv")):

                public_url = supabase.storage.from_("uploads").get_public_url(
                    f"{folder_name}/{file_name}"
                )

                reels.append(public_url)

    print(reels)

    return render_template("gallery.html", reels=reels)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)