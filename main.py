import os
from flask import Flask, render_template, request, jsonify
from models import db, User, Podcast
from podcast_generator import generate_podcast
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/interests', methods=['POST'])
def update_interests():
    data = request.json
    user_id = data.get('user_id', 1)  # For simplicity, we're using a default user
    interests = data.get('interests', [])

    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, interests=interests)
        db.session.add(user)
    else:
        user.interests = interests
    db.session.commit()

    return jsonify({"status": "success"})

@app.route('/api/generate_podcast', methods=['POST'])
def create_podcast():
    data = request.json
    user_id = data.get('user_id', 1)  # For simplicity, we're using a default user

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    podcast = generate_podcast(user.interests)
    new_podcast = Podcast(user_id=user_id, audio_url=podcast['audio_url'], transcript=podcast['transcript'])
    db.session.add(new_podcast)
    db.session.commit()

    return jsonify({"status": "success", "podcast_id": new_podcast.id})

@app.route('/api/podcasts', methods=['GET'])
def get_podcasts():
    user_id = request.args.get('user_id', 1)  # For simplicity, we're using a default user
    podcasts = Podcast.query.filter_by(user_id=user_id).order_by(Podcast.created_at.desc()).all()
    return jsonify([{"id": p.id, "audio_url": p.audio_url, "created_at": p.created_at} for p in podcasts])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
