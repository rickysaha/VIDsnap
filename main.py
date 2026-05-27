from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os

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

    myid = str(uuid.uuid1())

    if request.method == "POST":

        print(request.files.keys())

        rec_id = request.form.get("uuid")

        desc = request.form.get("text")

        # GET SELECTED VOICE
        voice = request.form.get("voice")

        input_files = []

        upload_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            rec_id
        )

        # CREATE FOLDER
        os.makedirs(upload_path, exist_ok=True)

        # SAVE FILES
        for key, value in request.files.items():

            print(key, value)

            file = request.files[key]

            if file and file.filename != "":

                filename = secure_filename(
                    file.filename
                )

                file.save(
                    os.path.join(
                        upload_path,
                        filename
                    )
                )

                input_files.append(filename)

                print(filename)

        # SAVE DESCRIPTION
        with open(
            os.path.join(upload_path, "desc.txt"),
            "w"
        ) as f:

            f.write(desc)

        # SAVE VOICE
        with open(
            os.path.join(upload_path, "voice.txt"),
            "w"
        ) as f:

            f.write(
                voice or "pNInz6obpgDQGcFmaJgB"
            )

        print("Voice Saved:", voice)

    return render_template(
        "create.html",
        myid=myid
    )


@app.route("/gallery")
def gallery():

    reels_folder = "static/reels"

    reels = []

    for reel in os.listdir(reels_folder):

        path = os.path.join(
            reels_folder,
            reel
        )

        # HIDE CORRUPTED FILES
        if (
            os.path.isfile(path)
            and os.path.getsize(path) > 100000
        ):

            reels.append(reel)

    return render_template(
        "gallery.html",
        reels=reels
    )


if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5001)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )