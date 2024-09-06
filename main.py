import logging
import os

from flask import Flask, jsonify, render_template, request

from config import Config
from models import Podcast, db
from podcast_generator import generate_podcast

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/interests", methods=["POST"])
def update_interests():
    data = request.json
    interests = data.get("interests", [])
    return jsonify({"status": "success"})


@app.route("/api/generate_podcast", methods=["POST"])
def create_podcast():
    try:
        interests = request.json.get("interests", [])
        podcast = generate_podcast(interests)
        new_podcast = Podcast(
            audio_url=podcast["audio_url"],
            transcript=podcast["transcript"],
        )
        db.session.add(new_podcast)
        db.session.commit()

        return jsonify({"status": "success", "podcast": podcast})
    except Exception as e:
        logging.error(f"Error generating podcast: {str(e)}")
        return jsonify({"error": "Failed to generate podcast"}), 500


@app.route("/api/podcasts", methods=["GET"])
def get_podcasts():
    podcasts = Podcast.query.order_by(Podcast.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": p.id,
                "audio_url": p.audio_url,
                "created_at": p.created_at.isoformat(),
            }
            for p in podcasts
        ]
    )


@app.route("/api/get_sample_descriptions")
def get_sample_descriptions():
    samples = {}
    user_descriptions_dir = "user_descriptions"
    for filename in os.listdir(user_descriptions_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(user_descriptions_dir, filename), "r") as f:
                samples[filename] = f.read().strip()
    return jsonify(samples)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001)
    app.run(host="0.0.0.0", port=5001)
