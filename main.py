import json
import logging
import os

from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
from llama_index import Document, GPTSimpleVectorIndex
from llama_index.readers import SimpleWebPageReader

from config import Config
from models import Podcast, db
from text_to_speech import text_to_speech

app = Flask(__name__)
CORS(app)
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
        podcast = generate_podcast(interests, "fake_user_id")
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


@app.route("/api/generate_podcast_stream", methods=["POST"])
def generate_podcast_stream():
    def generate():
        try:
            user_description = request.json.get("user_description", "")

            # Step 1: Generate query
            query = generate_query(user_description)
            yield json.dumps({"step": "query", "data": query}) + "\n"

            # Step 2: Get query results
            results = get_query_results(query)
            yield json.dumps({"step": "results", "data": results}) + "\n"

            # Step 3: Generate summary
            summary = generate_summary(results, user_description)
            yield json.dumps({"step": "summary", "data": summary}) + "\n"

            # Step 4: Generate audio
            audio_url = text_to_speech(summary)
            yield json.dumps({"step": "audio", "data": audio_url}) + "\n"

            # Save podcast to database
            new_podcast = Podcast(
                audio_url=audio_url,
                transcript=summary,
            )
            db.session.add(new_podcast)
            db.session.commit()

        except Exception as e:
            logging.error(f"Error generating podcast: {str(e)}")
            yield json.dumps({"error": "Failed to generate podcast"}) + "\n"

    return Response(generate(), mimetype="text/event-stream")


# Add these new functions
def generate_query(user_description):
    index = GPTSimpleVectorIndex([Document(user_description)])
    query = index.query("Generate a search query based on this user description")
    return query.response


def get_query_results(query):
    reader = SimpleWebPageReader(html_to_text=True)
    documents = reader.load_data(
        [f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"]
    )
    return [doc.text for doc in documents]


def generate_summary(results, user_description):
    documents = [Document(text) for text in results]
    index = GPTSimpleVectorIndex(documents)
    summary = index.query(
        f"Summarize these articles into a short podcast script, focusing on the interests described by the user: {user_description}"
    )
    return summary.response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    from text_to_speech import check_api_key

    check_api_key()
    app.run(host="0.0.0.0", port=5001)
