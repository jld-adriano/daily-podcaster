import os

import requests

from config import Config


def text_to_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": Config.ELEVENLABS_API_KEY,
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        filename = f"podcast_{hash(text)}.mp3"
        with open(os.path.join("static", "audio", filename), "wb") as f:
            f.write(response.content)
        return f"/static/audio/{filename}"
    else:
        raise Exception(f"Error in text-to-speech conversion: {response.text}")


def check_api_key():
    if not Config.ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY is not set in the configuration")
