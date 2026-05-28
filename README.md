# VIDsnap 🎬

AI Powered Reel Generator using Flask, FFmpeg, and ElevenLabs.

VIDsnap allows users to upload images or videos, add AI generated voice narration, and automatically create cinematic vertical reels optimized for social media platforms like Instagram Reels, TikTok, and YouTube Shorts.

---

# Features 🚀

* Upload multiple images or videos
* AI voice narration using ElevenLabs
* Multiple free AI voice options
* Automatic reel generation
* Smart image duration matching with narration
* Video audio replacement with AI narration
* Vertical 1080x1920 reel generation
* Reel gallery page
* Mobile-friendly UI
* Shareable using ngrok
* Automatic corrupted reel filtering

---

# Tech Stack 🛠️

## Backend

* Flask
* Python

## AI Voice Generation

* ElevenLabs API

## Video Processing

* FFmpeg

## Frontend

* HTML
* CSS
* JavaScript
* Jinja2 Templates

---

# Project Structure 📁

```bash
VIDsnap/
│
├── static/
│   ├── css/
│   └── reels/
│
├── templates/
│   ├── base.html
│   ├── create.html
│   ├── gallery.html
│   └── index.html
│
├── upload_folder/
│
├── main.py
├── generate_process.py
├── texttoaudio.py
├── requirements.txt
├── done.txt
└── README.md
```

---

# Installation ⚙️

## Clone Repository

```bash
git clone https://github.com/rickysaha/VIDsnap.git
cd VIDsnap
```

---

# Create Virtual Environment

## Mac/Linux

```bash
python3 -m venv env
source env/bin/activate
```

## Windows

```bash
python -m venv env
env\Scripts\activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Install FFmpeg

## Mac

```bash
brew install ffmpeg
```

## Ubuntu

```bash
sudo apt install ffmpeg
```

## Windows

Download FFmpeg from:
https://ffmpeg.org/download.html

Add FFmpeg to system PATH.

---

# Setup Environment Variables 🔑

Create a `.env` file:

```env
ELEVENLABS_API_KEY=your_api_key_here
```

Get API key from:
https://elevenlabs.io/

---

# Run the Application ▶️

## Terminal 1

```bash
python main.py
```

## Terminal 2

```bash
python generate_process.py
```

---

# Access Application 🌐

Open:

```bash
http://127.0.0.1:5001
```

---

# Share with Friends using ngrok 🌍

## Install ngrok

https://ngrok.com/

## Start ngrok

```bash
ngrok http 5001
```

Share the generated public URL.

---

# Supported Formats 📦

## Images

* JPG
* JPEG
* PNG

## Videos

* MP4
* MOV
* AVI
* MKV

---

# AI Voices 🎙️

Current free voices:

* Adam
* Bella
* Antoni
* Elli
* Arnold

---

# How It Works ⚡

1. User uploads media
2. User enters narration text
3. ElevenLabs generates AI narration
4. FFmpeg creates vertical reel
5. Reel appears in gallery

---

# Future Improvements 💡

* Auto subtitles
* Background music
* User authentication
* Cloud deployment
* AI script generation
* Reel thumbnails
* TikTok export
* Instagram direct sharing

---

# Screenshots 📸

Add screenshots here later.

---

# Author 👨‍💻

Priyanshu Saha

GitHub:
https://github.com/rickysaha

---

# License 📄

This project is for educational and personal use.
