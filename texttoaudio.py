import os
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(text: str, folder: str, voice_id: str) -> str:

    # GENERATE AUDIO
    response = elevenlabs.text_to_speech.convert(

        voice_id=voice_id,

        output_format="mp3_22050_32",

        text=text,

        model_id="eleven_flash_v2_5",

        voice_settings=VoiceSettings(

            stability=0.0,

            similarity_boost=1.0,

            style=0.0,

            use_speaker_boost=True,

            speed=1.0,
        ),
    )

    # SAVE PATH
    save_file_path = os.path.join(
        f"upload_folder/{folder}",
        "audio.mp3"
    )

    # SAVE AUDIO FILE
    with open(save_file_path, "wb") as f:

        for chunk in response:

            if chunk:

                f.write(chunk)

    print(f"{save_file_path}: Audio saved successfully!")

    return save_file_path