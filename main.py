from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os
from supabase_client import supabase

UPLOAD_FOLDER = 'upload_folder'
ALLOWED_EXTENSIONS = {  'png',
    'jpg',
    'jpeg',
    'mp4',
    'mov',
    'avi',
    'mkv'}

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
        for key, value in request.files.items():
            print(key, value)
            # Upload the file
            file = request.files[key]
            if file:
                filename = secure_filename(file.filename)
                if(not(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], rec_id)))):
                    os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], rec_id))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,  filename))
                 
                input_files.append(file.filename)
                print(file.filename)
            # Capture the description and save it to a file
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id, "desc.txt"), "w") as f:
                f.write(desc)
        for fl in input_files:
            with open(os.path.join(app.config['UPLOAD_FOLDER'], rec_id,  "input.txt"), "a") as f:
                f.write(f"file '{fl}'\nduration 1\n")


    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels = os.listdir("static/reels")
    print(reels)
    return render_template("gallery.html", reels=reels)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)