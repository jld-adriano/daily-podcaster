import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Podcast
from podcast_generator import generate_podcast
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/api/interests', methods=['POST'])
@login_required
def update_interests():
    data = request.json
    interests = data.get('interests', [])

    current_user.interests = interests
    db.session.commit()

    return jsonify({"status": "success"})

@app.route('/api/generate_podcast', methods=['POST'])
@login_required
def create_podcast():
    try:
        podcast = generate_podcast(current_user.interests)
        new_podcast = Podcast(user_id=current_user.id, audio_url=podcast['audio_url'], transcript=podcast['transcript'])
        db.session.add(new_podcast)
        db.session.commit()

        return jsonify({"status": "success", "podcast": podcast})
    except Exception as e:
        logging.error(f"Error generating podcast: {str(e)}")
        return jsonify({"error": "Failed to generate podcast"}), 500

@app.route('/api/podcasts', methods=['GET'])
@login_required
def get_podcasts():
    podcasts = current_user.podcasts.order_by(Podcast.created_at.desc()).all()
    return jsonify([{"id": p.id, "audio_url": p.audio_url, "created_at": p.created_at.isoformat()} for p in podcasts])

@app.route('/api/get_sample_descriptions')
def get_sample_descriptions():
    samples = {}
    user_descriptions_dir = 'user_descriptions'
    for filename in os.listdir(user_descriptions_dir):
        if filename.endswith('.txt'):
            with open(os.path.join(user_descriptions_dir, filename), 'r') as f:
                samples[filename] = f.read().strip()
    return jsonify(samples)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
