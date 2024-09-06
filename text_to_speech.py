import os
import requests
import logging
import time
from config import Config

def text_to_speech(text: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{Config.ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": Config.ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        # Save the audio file
        filename = f"podcast_{int(time.time())}.mp3"
        filepath = os.path.join("static", "audio", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(response.content)

        return f"/static/audio/{filename}"
    except requests.RequestException as e:
        logging.error(f"Error generating audio: {str(e)}")
        return ""
