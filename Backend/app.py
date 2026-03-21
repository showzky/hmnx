# -------------------------
# Import Libraries and Modules
# -------------------------
#import eventlet
#eventlet.monkey_patch()

from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone, timedelta
import socketio as py_socketio
from flask_socketio import SocketIO, Namespace
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from flask import send_file
import mimetypes
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from enum import Enum
import defusedxml.ElementTree as ET
import json
from pathlib import Path
from soundcloud_routes import soundcloud_bp

# In-memory store for playlist data
playlist_data = []

# Import Cloudinary libraries for image upload
import cloudinary
import cloudinary.uploader
# Removed unused import: cloudinary.api

# -------------------------
# Game Achievements 
# -------------------------
GAME_ACHIEVEMENTS_PATH = Path(__file__).parent / 'clicker_achievements.json'
with open(GAME_ACHIEVEMENTS_PATH, 'r', encoding='utf-8') as f:
    GAME_ACHIEVEMENTS = json.load(f)

# -------------------------
# Load Backend Environment Variables
# -------------------------
# Adjust the path based on your folder structure.
# Determine which env file to load based on FLASK_ENV.
if os.getenv("FLASK_ENV") == "production":
    env_file = os.path.join(os.path.dirname(__file__), '.env.backend.production')
else:
    env_file = os.path.join(os.path.dirname(__file__), '.env.backend.development')

load_dotenv(env_file)
print("Loaded MAILERSEND_USERNAME:", os.getenv("MAILERSEND_USERNAME"))

# -------------------------
# Initialize Flask App
# -------------------------
app = Flask(__name__, static_folder="/var/www/Backend/static", static_url_path="/static") 
app.secret_key = os.urandom(24)

# Set maximum file upload size to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# -------------------------
# Cloudinary Configuration
# -------------------------
cloudinary.config(
    cloud_name='di8fs1bcm',       # Cloud name
    api_key='572143913137685',    # API key
    api_secret='x5NtUOZVTPnDUZmRvUyP_ZhMJBQ'   # API secret
)

# -------------------------
# Available Roles Configuration
# -------------------------
AVAILABLE_ROLES = ['producer', 'developer', 'Admin']

# -------------------------
# JWT Configuration: Set token expiration times
# -------------------------
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# -------------------------
# Application Configuration for Database and JWT
# -------------------------
database_uri = os.getenv('DATABASE_URI')
if not database_uri:
    raise RuntimeError(
        "DATABASE_URI is not configured. Set it in Backend/.env.backend.development for local "
        "development or in your production environment variables."
    )

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

# -------------------------
# Configure Upload Folder (for local storage if needed)
# -------------------------
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Flask-Mail Configuration
# -------------------------

# MailerSend config
mailer_send_config = {
    'MAIL_SERVER': os.getenv('MAILERSEND_SERVER', 'smtp.mailersend.net'),
    'MAIL_PORT': int(os.getenv('MAILERSEND_PORT', '2525')),
    'MAIL_USE_TLS': os.getenv('MAILERSEND_USE_TLS', 'true').lower() == 'true',
    'MAIL_USERNAME': os.getenv('MAILERSEND_USERNAME'),
    'MAIL_PASSWORD': os.getenv('MAILERSEND_PASSWORD'),
    'MAIL_DEFAULT_SENDER': os.getenv('MAILERSEND_DEFAULT_SENDER', 'MS_TS4k3S@hmnmentalpasienter.no'),
    'MAIL_DEBUG': True
}

# Support email config
support_config = {
    'MAIL_SERVER': os.getenv('SUPPORT_SERVER', 'mail.hmnmentalpasienter.no'),
    'MAIL_PORT': int(os.getenv('SUPPORT_PORT', '587')),
    'MAIL_USE_TLS': os.getenv('SUPPORT_USE_TLS', 'true').lower() == 'true',
    'MAIL_USERNAME': os.getenv('SUPPORT_USERNAME'),
    'MAIL_PASSWORD': os.getenv('SUPPORT_PASSWORD'),
    'MAIL_DEFAULT_SENDER': os.getenv('SUPPORT_DEFAULT_SENDER', 'support@hmnmentalpasienter.no'),
    'MAIL_DEBUG': True
}

# Initialize Flask-Mail with the main app config (default could be MailerSend or Support)
app.config.update(mailer_send_config)  # Set MailerSend or Support as default
mail = Mail(app)

# -------------------------
# Functions to Switch Configs Dynamically
# -------------------------

def switch_mail_config(config):
    """Helper to switch mail config dynamically"""
    app.config.update(config)
    mail.init_app(app)  # Reinitialize Mail with the new config

import logging
import os

logger = logging.getLogger("test_email")

def get_dynamic_log_path():
    # 1. Use ENV if explicitly set
    log_path_env = os.getenv('APP_LOG_PATH')
    if log_path_env:
        return log_path_env

    # 2. Otherwise, dynamic based on FLASK_ENV
    if os.getenv("FLASK_ENV") == "production":
        return "/var/www/Backend/test_email.log"
    else:
        # Use the project directory in development!
        return os.path.join(os.path.dirname(__file__), "test_email.log")

log_path = get_dynamic_log_path()
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Ensure the directory exists
os.makedirs(os.path.dirname(log_path), exist_ok=True)

handler = logging.FileHandler(log_path)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

import threading

def send_email_async_thread(msg):
    try:
        # Ensure the application context is active in this thread.
        with app.app_context():
            mail.send(msg)
        logger.info("Email sent successfully in background thread!")
    except Exception:
        logger.exception("Exception in background thread email sending:")


@app.route('/api/test-email')
def test_email():
    msg = Message(
        subject="🧠 HMN Email Test",
        recipients=["andre.tonning@gmail.com"],
        body="Hey Andre! This is your Flask app sending you an email from your VPS 🎉🚀"
    )
    # Start a background thread to send the email
    threading.Thread(target=send_email_async_thread, args=(msg,)).start()
    return "✅ Email is being sent asynchronously!"


def sanitize_svg(svg_data):
    try:
        # Parse the SVG data
        tree = ET.fromstring(svg_data)
        # Optionally, check for forbidden tags/attributes here
        # For example, block <script> tags
        for elem in tree.iter():
            if elem.tag.endswith('script'):
                raise ValueError("SVG contains forbidden <script> tag")
        # If it parses and passes checks, return the original data
        return svg_data
    except Exception as e:
        raise ValueError(f"Invalid or unsafe SVG: {e}")




# -------------------------
# Initialize Extensions
# -------------------------
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.register_blueprint(soundcloud_bp)


import os
import logging

if os.getenv("FLASK_ENV") == "production":
    log_file_path = '/var/www/Backend/app_debug.log'
else:
    # For local development on Windows, use a relative path in the current directory.
    log_file_path = os.path.join(os.getcwd(), 'app_debug.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)



# -------------------------
# Models
# -------------------------
# -------------------------
# Association Table: Many-to-Many relationship between User and Role
# -------------------------
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

################################################################################################################################################


# models.py (or in app.py, above your routes)
class Friend(db.Model):
    __tablename__ = 'friend'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)

    # (Optional) convenience backrefs:
    user       = db.relationship('User', foreign_keys=[user_id],   backref=db.backref('friends',  lazy='dynamic'))
    friend_obj = db.relationship('User', foreign_keys=[friend_id], backref=db.backref('followers', lazy='dynamic'))
# Configure OAuth with Authlib
oauth = OAuth(app)

# Register Discord as an OAuth provider with the necessary endpoints and scopes
discord = oauth.register(
    name='discord',  
    client_id='1356200673636515922',  
    client_secret='IscsTQvtavYEtCA30VGQMscq1EVJ3J4B',  
    access_token_url='https://discord.com/api/oauth2/token', 
    authorize_url='https://discord.com/api/oauth2/authorize',  
    api_base_url='https://discord.com/api/', 
    client_kwargs={  
        'scope': 'identify email'
    }
)

socketio = SocketIO(app, cors_allowed_origins="*")  # add any other configs you need

# Comment Model with nested (self-referential) relationship for replies
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    # Endre parent_id til ondelete='CASCADE'
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('comment.id', ondelete='CASCADE'),
        nullable=True
    )
    
    # Samme for thread_id
    thread_id = db.Column(
        db.Integer,
        db.ForeignKey('thread.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    replies = db.relationship(
        'Comment',
        # Her kan du bruke cascade='all, delete-orphan', men pass på cyclical references
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    # NEW: Relationship to the User model
    user = db.relationship('User', lazy=True, foreign_keys=[user_id])

    def __repr__(self):
        return f'<Comment {self.id}>'

# Thread Model representing a forum thread
class Thread(db.Model):
    __tablename__ = 'thread'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Updated with ForeignKey
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # This sets up the relationship to the User model.
    user = db.relationship('User', lazy=True, foreign_keys=[user_id])
    
    # Relationship to the Comment model – each thread can have many comments.
    comments = db.relationship(
        'Comment',
        backref='thread',
        lazy=True,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<Thread {self.id} - {self.title}>'

# Setting model for storing key-value app settings like maintenance_mode
class Setting(db.Model):
    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'

# User Model representing a registered user
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Profile information
    username = db.Column(db.String(80), unique=True, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    banner = db.Column(db.String(200), nullable=True)
     # NEW: Rank field for user roles (default is 'regular')
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy=True))
    krenke_level = db.Column(db.Float, default=0)
    fitte_points = db.Column(db.Integer, default=0)
    last_daily_reward_claim = db.Column(db.DateTime, nullable=True)
    daily_claim_count = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, nullable=True)
    login_streak = db.Column(db.Integer, default=0)



    def __repr__(self):
        return f'<User {self.email}>'

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    def has_role(self, role_names):
        """Check if a user has any of the specified roles"""
        return any(role.name in role_names for role in self.roles)
    # Define which ranks are allowed to manage songs
allowed_ranks_for_song_management = ['developer', 'producer']

def check_user_rank(user, allowed_ranks):
    # Convert both the allowed list and role names to lowercase for case-insensitive comparison.
    return any(role.name.lower() in [r.lower() for r in allowed_ranks] for role in user.roles)

def get_setting(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default

def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
    db.session.commit()


def can_manage_music(user):
    if not user:
        return False
    return any(role.name.lower() in ['admin', 'developer', 'producer'] for role in user.roles)


def serialize_music_song(song):
    track_url = song.url or song.soundcloudUrl or ''
    author_name = song.author_name or song.artist or ''
    thumbnail_url = song.thumbnail_url or song.cover or ''

    return {
        'id': song.id,
        'title': song.title,
        'url': track_url,
        'author_name': author_name,
        'thumbnail_url': thumbnail_url,
        'duration': song.duration or '',
        'featured': bool(song.featured),
        'position': song.position or 0,
        # Compatibility keys during migration
        'artist': author_name,
        'cover': thumbnail_url,
        'soundcloudUrl': track_url,
    }


def serialize_playlist_song(song):
    payload = serialize_music_song(song)
    return {
        'id': payload['id'],
        'title': payload['title'],
        'artist': payload['artist'],
        'cover': payload['cover'],
        'soundcloudUrl': payload['soundcloudUrl'],
        'position': payload['position'],
        'featured': payload['featured'],
        'duration': payload['duration'],
        'author_name': payload['author_name'],
        'thumbnail_url': payload['thumbnail_url'],
        'url': payload['url'],
    }


def get_ordered_songs():
    return Song.query.order_by(Song.position.asc(), Song.id.asc()).all()


def normalize_music_payload(data):
    return {
        'title': (data.get('title') or '').strip(),
        'url': (data.get('url') or data.get('soundcloudUrl') or '').strip(),
        'author_name': (data.get('author_name') or data.get('artist') or '').strip(),
        'thumbnail_url': (data.get('thumbnail_url') or data.get('cover') or '').strip(),
        'duration': (data.get('duration') or '').strip(),
        'featured': bool(data.get('featured', False)),
    }


def get_driftsmelding_history():
    history = []
    for index in range(1, 4):
        prefix = f'notice_maintenance_history_{index}'
        title = get_setting(f'{prefix}_title', '')
        message = get_setting(f'{prefix}_message', '')
        updated_at = get_setting(f'{prefix}_updated_at', '')
        ref = get_setting(f'{prefix}_ref', '')
        if title or message:
            history.append({
                'title': title,
                'message': message,
                'updated_at': updated_at,
                'ref': ref,
            })
    return history


def set_driftsmelding_history(history_items):
    for index in range(1, 4):
        item = history_items[index - 1] if index - 1 < len(history_items) else None
        prefix = f'notice_maintenance_history_{index}'
        set_setting(f'{prefix}_title', item.get('title', '') if item else '')
        set_setting(f'{prefix}_message', item.get('message', '') if item else '')
        set_setting(f'{prefix}_updated_at', item.get('updated_at', '') if item else '')
        set_setting(f'{prefix}_ref', item.get('ref', '') if item else '')


def build_driftsmelding_feed():
    current_message = get_setting('notice_maintenance_message', '')
    current_title = get_setting('notice_maintenance_title', '')
    current_updated_at = get_setting('notice_maintenance_updated_at', '')
    current_ref = get_setting('notice_maintenance_ref', '')

    items = []
    if current_message:
        items.append({
            'title': current_title or 'Ny driftsmelding',
            'body': current_message,
            'message': current_message,
            'date': current_updated_at,
            'updated_at': current_updated_at,
            'ref': current_ref or 'HMN-MSG-001',
            'meta': 'nyeste driftsmelding',
            'is_featured': True,
        })

    for item in get_driftsmelding_history():
        items.append({
            'title': item.get('title') or 'Tidligere driftsmelding',
            'body': item.get('message', ''),
            'message': item.get('message', ''),
            'date': item.get('updated_at', ''),
            'updated_at': item.get('updated_at', ''),
            'ref': item.get('ref', ''),
            'meta': 'tidligere melding',
            'is_featured': False,
        })

    return items



#Socket
class DashboardNamespace(Namespace):
    def on_connect(self):
        print("✅ Client connected to /dashboard namespace")

    def on_disconnect(self):
        print("❌ Client disconnected from /dashboard")

    def on_custom_event(self, data):
        print("📩 Received custom_event on /dashboard:", data)

socketio.emit('event_name', {'some': 'data'}, namespace='/dashboard')
socketio.on_namespace(DashboardNamespace('/dashboard'))


@app.route('/debug-session')
def debug_session():
    return jsonify(dict(session))




app.config.update(
    SESSION_COOKIE_DOMAIN='.www.hmnmentalpasienter.no',
    SESSION_COOKIE_SAMESITE='None',  # or 'None' if you want cross-site
    SESSION_COOKIE_SECURE=True       # if using HTTPS
)
import base64
import hashlib
import hmac
import urllib.parse

from flask import request, redirect, session  # Added session for session-based authentication

# SSO Configuration
SSO_SECRET = 'ca7d1c78cef959144eae8eee30249309b97829ef7c7a4a5e768e48cdee6646cf'
DISCOURSE_SSO_CALLBACK = 'https://forum.hmnmentalpasienter.no/session/sso_login'

# SSO endpoint: No JWT protection, relies on session-based authentication
@app.route('/api/sso', methods=['GET'])
def sso():
    # Retrieve SSO parameters from the query
    sso_payload = request.args.get('sso')
    sig = request.args.get('sig')
    if not sso_payload or not sig:
        return "Missing parameters", 400

    # Verify the provided signature against our computed signature
    computed_sig = hmac.new(
        SSO_SECRET.encode('utf-8'),
        sso_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    if computed_sig != sig:
        return "Invalid signature", 403

    # Decode the SSO payload
    try:
        decoded = base64.b64decode(sso_payload).decode('utf-8')
    except Exception as e:
        return f"Error decoding payload: {e}", 400

    # Parse the decoded query string to extract the nonce
    qs = urllib.parse.parse_qs(decoded)
    nonce = qs.get('nonce', [None])[0]
    if not nonce:
        return "Missing nonce", 400

    # Retrieve the current user's ID from the session
    current_user_id = session.get('user_id')
    if not current_user_id:
        return "User not authenticated", 403

    # Ensure the user ID is in integer form
    try:
        current_user_id = int(current_user_id)
    except Exception as e:
        return f"Invalid user id format: {e}", 400

    # Query the user from the database
    user = User.query.get(current_user_id)
    if not user:
        return "User not found", 404

    # Extract user roles and create a role string (default to 'member' if none)
    roles = [role.name for role in user.roles]
    # Removed unused variable: role_str
    ','.join(roles) if roles else 'member'


    groups_str = ','.join([role.name for role in user.roles])
    # Build the payload for Discourse SSO
    payload_dict = {
        'nonce': nonce,
        'email': user.email,
        'external_id': str(user.id),
        'username': user.username,
        "groups": groups_str
    }
    payload_str = urllib.parse.urlencode(payload_dict)
    payload_base64 = base64.b64encode(payload_str.encode('utf-8')).decode('utf-8')

    # Compute a new signature for our payload
    new_sig = hmac.new(
        SSO_SECRET.encode('utf-8'),
        payload_base64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Construct the redirect URL to Discourse with the payload and signature
    redirect_url = (
        f"{DISCOURSE_SSO_CALLBACK}?sso={urllib.parse.quote(payload_base64)}"
        f"&sig={new_sig}"
    )
    return redirect(redirect_url)

# -------------------------








# NEW: Song Model for Music Player
class Song(db.Model):
    __tablename__ = 'song'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=True)
    cover = db.Column(db.String(255), nullable=True)          # New column for cover image URL
    soundcloudUrl = db.Column(db.String(255), nullable=True)   # New column for SoundCloud URL
    url = db.Column(db.String(255), nullable=True)
    author_name = db.Column(db.String(255), nullable=True)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.String(32), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    upload_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    position = db.Column(db.Integer, default=0)


    def __repr__(self):
        return f'<Song {self.id} - {self.title}>'

#221
#Activity Model to track user actions
class Activity(db.Model):
    __tablename__ = 'activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # e.g., 'dashboard_visit'
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    duration_seconds = db.Column(db.Integer, default=0)

    # Relationship to the User model
    user = db.relationship('User', lazy=True, foreign_keys=[user_id])

    def __repr__(self):
        return f'<Activity {self.id} - User {self.user_id} - Type {self.activity_type}>'

from datetime import datetime, timezone

# -------------------------
# Role Model to store available roles (badges/job titles)
# -------------------------
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    badge_icon = db.Column(db.String(20), nullable=True)   # e.g., "👑", "💻"
    badge_color = db.Column(db.String(20), nullable=True)    # e.g., "#f5a623", "#e35050"
class TeamMember(db.Model):
    __tablename__ = 'team_member'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)  # For controlling display order
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'bio': self.bio,
            'avatar': self.avatar,
            'order': self.order
        }
# Notification Model
class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False) # e.g., 'system_update', 'collaboration_request'
    message = db.Column(db.Text, nullable=False) # The main content of the notification
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)
    related_object_id = db.Column(db.Integer, nullable=True) # Optional: Link to a related object (e.g., experiment ID, collaboration ID)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True)) # Relationship to User

    from datetime import datetime, timezone

class FriendRequest(db.Model):
    __tablename__ = 'friend_request'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'
    )  # 'pending', 'accepted', 'declined'
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    sender = db.relationship(
        'User',
        foreign_keys=[sender_id],
        backref=db.backref('sent_requests', lazy=True)
    )
    receiver = db.relationship(
        'User',
        foreign_keys=[receiver_id],
        backref=db.backref('received_requests', lazy=True)
    )

    def __repr__(self):
        return f'<FriendRequest {self.id}: {self.sender_id} -> {self.receiver_id} ({self.status})>'


# NEW: Event Model for Upcoming Events
class Event(db.Model):
    __tablename__ = 'event'  # Defines the table name in the database as 'event'

    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each event, automatically incrementing
    event_name = db.Column(db.String(255), nullable=False)  # Name of the event (e.g., "Movie Night"), cannot be empty
    event_date = db.Column(db.Date, nullable=False)     # Date of the event, cannot be empty
    event_time = db.Column(db.Time, nullable=False)     # Time of the event, cannot be empty
    event_description = db.Column(db.Text, nullable=True)   # Optional description for the event
    event_image_path = db.Column(db.String(255))  # Store Cloudinary URL of the image
    template_name = db.Column(db.String(100), default='template1') # Store template name, default to 'template1'

    def __repr__(self):
        return f'<Event {self.id} - {self.event_name}>'

class ShopItem(db.Model):
    __tablename__ = 'shop_items'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price       = db.Column(db.Integer, nullable=False, default=0)
    icon = db.Column(db.Text, nullable=True)
    rarity = db.Column(db.String(50), nullable=True)
    glow_color = db.Column(db.String(50), nullable=True)
    type        = db.Column(db.Enum('badge', 'theme', name='shop_item_type'),
                            nullable=False, default='badge')
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ShopItem {self.id} – {self.name} ({self.type})>'

class UserShopItem(db.Model):
    __tablename__ = 'user_shop_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(
    db.Integer,
    db.ForeignKey('shop_items.id', ondelete='CASCADE'),
    nullable=False
)
    purchased_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='purchased_items')
    item = db.relationship(
    'ShopItem',
    backref=db.backref('purchases', cascade='all, delete-orphan')
)

from datetime import datetime

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.String(64), db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='user_achievements')
    achievement = db.relationship('Achievement', backref='user_achievements')
    unlocked = db.Column(db.Boolean, default=True)


class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.String(64), primary_key=True)  
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.Text, nullable=True)  # SVG, emoji, Cloudinary link, etc
    rarity = db.Column(db.String(50), nullable=True)
    glow_color = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    condition_type = db.Column(db.String(64), nullable=True)
    condition_value = db.Column(db.Integer, nullable=True)



#Changelog model
class Changelog(db.Model):
    __tablename__ = 'changelog'
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    added = db.Column(db.Text, nullable=True)  # List of added features (stored as text)
    changed = db.Column(db.Text, nullable=True)  # List of changes (stored as text)

    def to_dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "date": self.date.isoformat(),
            "added": self.added.split('\n') if self.added else [],
            "changed": self.changed.split('\n') if self.changed else []
        }
#News Model
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to User model
    user = db.relationship('User', backref=db.backref('news_posts', lazy=True))



@app.before_request
def check_for_maintenance():
    # Get the current maintenance status from the database.
    mode = get_setting('maintenance_mode', 'off')
    if mode != 'on':
        # If maintenance mode is off, proceed normally.
        return None

    # List the allowed routes (whitelist) even when maintenance is on.
    allowed_routes = [
        '/api/login',
        'login',
        '/api/maintenance',
        '/api/register',
        '/maintenance', 
        '/api/maintenance-status',  # Allow maintenance status check             # Our custom route to show maintenance page.
        '/static/maintenance.html'   # Direct access to the static file.
    ]

    # If the request path is whitelisted, allow it.
    if request.path in allowed_routes:
        return None

    # If this is an API request, return the static maintenance page with a 503 status code.
    if request.path.startswith('/api/'):
        return app.send_static_file('maintenance.html'), 503

    # Otherwise (a non-API request) redirect to the maintenance page.
    return redirect('/maintenance')

# Removed unused import: send_from_directory
# Removed unused import: current_app
from flask import current_app
@app.route('/maintenance')
def serve_maintenance():
    response = app.send_static_file('maintenance.html')
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/debug_static')
def debug_static():
    return jsonify({"static_folder": app.static_folder})





# -------------------------
# API Endpoints
# -------------------------

#Discord Register
@app.route('/login/discord')
def login_discord():
    redirect_uri = url_for('authorize_discord', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route('/authorize/discord')
def authorize_discord():
    # Exchange the authorization code for an access token from Discord.
    token = discord.authorize_access_token()
    print("Access token received:", token)  # Debug: Print token

    # Fetch the user's profile from Discord without extra headers (omit the leading slash)
    resp = discord.get('users/@me')
    print("Raw response from /users/@me:", resp.text)  # Debug: Print raw response

    try:
        profile = resp.json()
    except Exception as e:
        print("JSON decoding error:", e)
        return "Error: Unable to decode JSON response from Discord", 500

    session['discord_user'] = profile

    # Integrate with your database: Find or create the user
    user = User.query.filter_by(email=profile.get('email')).first()
    if not user:
        user = User(
            email=profile.get('email'),
            username=profile.get('username'),
            password_hash=bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    session['jwt_token'] = access_token

    # Redirect to your Vue dashboard with the token as a query parameter
    return redirect(f"http://localhost:5173/dashboard?token={access_token}")

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
         return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "avatar": user.avatar,
            "banner": user.banner,
            "roles": [{"id": role.id, "name": role.name} for role in user.roles]
        }
    }), 200







@app.route('/dashboard')
def dashboard():
    discord_user = session.get('discord_user')
    if (discord_user):
        return f"Hello, {discord_user['username']}! You are logged in with Discord."
    else:
        return "You are not logged in with discord."
    


# Registration Endpoint: /api/register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password_hash=password_hash)
    
    # Assign a default role
    default_role = Role.query.filter_by(name='Member').first()
    if default_role:
        new_user.roles.append(default_role)
    else:
        # Optionally, create the default role if it doesn't exist.
        default_role = Role(name='Member', badge_icon='fas fa-user', badge_color='#cccccc')
        db.session.add(default_role)
        db.session.commit()  # Commit so that default_role gets an ID
        new_user.roles.append(default_role)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201




# Login Endpoint: /api/login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401
    #  # Update login streak here:
    today = datetime.now(timezone.utc).date()  # timezone aware
    if user.last_login_date == today:
        # Already logged in today, no change
        pass
    elif user.last_login_date == today - timedelta(days=1):
        # Continued streak
        user.login_streak = (user.login_streak or 0) + 1
        user.last_login_date = today
    else:
        # Streak broken or first login
        user.login_streak = 1
        user.last_login_date = today

    check_and_unlock_login_streak_achievements(user)

    db.session.commit()

    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "avatar": user.avatar,
            "banner": user.banner, 
            "roles": [{"id": role.id, "name": role.name} for role in user.roles]
        }
    }), 200
def check_and_unlock_login_streak_achievements(user):
    achievements = Achievement.query.filter_by(condition_type='login_streak').all()
    for ach in achievements:
        if user.login_streak >= ach.condition_value:
            unlocked = UserAchievement.query.filter_by(user_id=user.id, achievement_id=ach.id).first()
            if not unlocked:
                new_unlock = UserAchievement(
                    user_id=user.id,
                    achievement_id=ach.id,
                    unlocked_at=datetime.now(timezone.utc)
                )
                db.session.add(new_unlock)


# Refresh Endpoint: /api/refresh
@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200

# Update Profile Endpoint: /api/update-profile
@app.route('/api/update-profile', methods=['POST'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    data = request.get_json()
    username = data.get('username')
    bio = data.get('bio')
    
    app.logger.debug(f"Updating user {user.id}: new username: {username}, new bio: {bio}")

    if bio is not None and len(bio) > 300:
        return jsonify({"msg": "Bio cant exceed 300 char"}), 400

    if username is not None:
        if username.strip() == "":
            return jsonify({"msg": "Username cannot be empty"}), 400
        user.username = username

    if bio is not None:
        user.bio = bio

    db.session.commit()

    return jsonify({
        "msg": "Profile updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "avatar": user.avatar
        }
    }), 200

# Api for sending message 
from flask_mail import Mail, Message

@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    name    = data.get("name")
    email   = data.get("email")
    message = data.get("message")

    if not name or not email or not message:
        return jsonify({"msg": "Missing name, email or message"}), 400

    # ——— Create a temporary mailer bound to your support SMTP ———
    temp_mail = Mail()
    app.config.update(support_config)
    temp_mail.init_app(app)

    # ——— Build the message, force sender to your support address ———
    msg = Message(
        subject=f"New Contact Form Submission from {name}",
        sender='support@hmnmentalpasienter.no',        
        recipients=['support@hmnmentalpasienter.no'],  
        reply_to=email,                                
        body=(
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}"
        )
    )

    try:
        temp_mail.send(msg)
        return jsonify({"msg": "Message sent successfully"}), 200
    except Exception as e:
        app.logger.error("Error sending support email: %s", e)
        return jsonify({"msg": "Failed to send message"}), 500


    

# Upload Avatar Endpoint: /api/upload-avatar
@app.route('/api/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if 'avatar' not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    if not file.content_type.startswith('image/'):
        return jsonify({"msg": "Invalid file type, only images are allowed"}), 400

    try:
        result = cloudinary.uploader.upload(
            file,
            folder=f"user_{user.id}/avatars",
            public_id=f"profile_picture_{user.id}",
            overwrite=True
        )
        image_url = result['secure_url']
        user.avatar = image_url
        db.session.commit()
        return jsonify({"msg": "Avatar updated successfully", "url": image_url}), 200
    except Exception as e:
        print(f"Error uploading file to Cloudinary: {e}")
        return jsonify({"msg": "File upload failed"}), 500

# Endpoint for serving uploaded files (for development purposes)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    mime_type = mimetypes.guess_type(file_path)[0]
    return send_file(file_path, mimetype=mime_type)

# Comment API Endpoints
@app.route('/api/comments', methods=['GET'])
@jwt_required()
def get_comments():
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    comments_list = [{
        "id": c.id,
        "user_id": c.user_id,
        "content": c.content,
        "parent_id": c.parent_id,
        "timestamp": c.timestamp.isoformat()
    } for c in comments]
    return jsonify({"comments": comments_list}), 200

@app.route('/api/comments', methods=['POST'])
@jwt_required()
def post_comment():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    content = data.get('content')
    # For a top-level comment, parent_id is not provided (or is None)
    parent_id = data.get('parent_id')
    if not content or content.strip() == "":
        return jsonify({"msg": "Kommentar kan ikke være tom"}), 400

    new_comment = Comment(
        user_id=int(current_user_id),
        content=content,
        parent_id=parent_id  # This will be None for a top-level comment
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "msg": "Kommentar postet",
        "comment": {
            "id": new_comment.id,
            "user_id": new_comment.user_id,
            "content": new_comment.content,
            "parent_id": new_comment.parent_id,
            "timestamp": new_comment.timestamp.isoformat()
        }
    }), 201

# Api for endring å sletting av kommenterarer
@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({"msg": "Comment does not exist"}), 404

    # Sjekk at innlogget bruker eier kommentaren
    if comment.user_id != int(current_user_id):
        return jsonify({"msg": "Not authorized to edit this comment"}), 403

    data = request.get_json()
    new_content = data.get('content')
    
    if not new_content or not new_content.strip():
        return jsonify({"msg": "Content cannot be empty"}), 400
    
    # Oppdater tekst
    comment.content = new_content.strip()
    db.session.commit()
    
    return jsonify({"msg": "Comment updated"}), 200

# Sletting av kommmentarer
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get(comment_id)
    
    if not comment:
        return jsonify({"msg": "Comment does not exist"}), 404
    
    # Sjekk at innlogget bruker eier kommentaren
    if comment.user_id != int(current_user_id):
        return jsonify({"msg": "Not authorized to delete this comment"}), 403

    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"msg": "Comment deleted"}), 200

  

# --- FriendRequest Status Enum ---
class RequestStatus(str, Enum):
    pending  = 'pending'
    accepted = 'accepted'
    declined = 'declined'

# --- Send Friend Request ---
# --- Send Friend Request ---
@app.route('/api/friend-requests', methods=['POST'])
@jwt_required()
def send_friend_request():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    receiver_id = data.get('receiver_id')
    if not receiver_id or receiver_id == current_user_id:
        return jsonify({'msg': 'Invalid user'}), 400

    # Prevent duplicate pending requests
    exists = FriendRequest.query.filter_by(
        sender_id=current_user_id,
        receiver_id=receiver_id,
        status=RequestStatus.pending.value
    ).first()
    if exists:
        return jsonify({'msg': 'Request already sent'}), 409

    # Create the friend request
    fr = FriendRequest(
        sender_id=current_user_id,
        receiver_id=receiver_id,
        status=RequestStatus.pending.value
    )
    db.session.add(fr)
    db.session.flush()   # assign fr.id

    # Create a Notification for the receiver
    sender = User.query.get(current_user_id)
    notif = Notification(
        user_id=receiver_id,
        notification_type='friend_request',
        message=f"{sender.username or sender.email} sent you a friend request",
        related_object_id=fr.id
    )
    db.session.add(notif)

    # Commit both the FriendRequest and the Notification
    db.session.commit()

    return jsonify({'msg': 'Friend request sent', 'request_id': fr.id}), 201


# --- List Incoming Requests ---
@app.route('/api/friend-requests', methods=['GET'])
@jwt_required()
def list_friend_requests():
    current_user_id = int(get_jwt_identity())
    pending = FriendRequest.query.filter_by(
        receiver_id=current_user_id,
        status=RequestStatus.pending.value
    ).all()
    return jsonify([{
        'id': fr.id,
        'sender': {
            'id': fr.sender.id,
            'username': fr.sender.username,
            'avatar': fr.sender.avatar
        }
    } for fr in pending]), 200

# --- Accept Friend Request ---
@app.route('/api/friend-requests/<int:fr_id>/accept', methods=['POST'])
@jwt_required()
def accept_friend_request(fr_id):
    current_user_id = int(get_jwt_identity())
    fr = FriendRequest.query.get(fr_id)
    
    if not fr or fr.receiver_id != current_user_id or fr.status != RequestStatus.pending.value:
        return jsonify({'msg': 'Not found or invalid'}), 404

    # ✅ Check if the friendship already exists
    existing = Friendship.query.filter_by(user_id=current_user_id, friend_id=fr.sender_id).first()
    if existing:
        return jsonify({"message": "You are already friends."}), 409
    

    # Accept the friend request
    fr.status = RequestStatus.accepted.value

    # ✅ Create mutual friendships
    db.session.add_all([
        Friendship(user_id=current_user_id, friend_id=fr.sender_id),
        Friendship(user_id=fr.sender_id, friend_id=current_user_id)
    ])
    
    db.session.commit()
    return jsonify({'msg': 'Friend request accepted'}), 200
# --- END Accept Friend Request ---


# --- Decline Friend Request ---
@app.route('/api/friend-requests/<int:fr_id>/decline', methods=['POST'])
@jwt_required()
def decline_friend_request(fr_id):
    current_user_id = int(get_jwt_identity())
    fr = FriendRequest.query.get(fr_id)
    if not fr or fr.receiver_id != current_user_id or fr.status != RequestStatus.pending.value:
        return jsonify({'msg': 'Not found or invalid'}), 404

    fr.status = RequestStatus.declined.value
    db.session.commit()
    return jsonify({'msg': 'Friend request declined'}), 200

# --- Mutual Friendship Model ---
class Friendship(db.Model):
    __tablename__ = 'friendship'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='uq_user_friend'),
    )



# Create Thread Endpoint: /api/threads (POST)
@app.route('/api/threads', methods=['POST'])
@jwt_required()
def create_thread():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    title = data.get('title')
    
    if not title or title.strip() == "":
        return jsonify({"msg": "Title is required"}), 400

    new_thread = Thread(title=title, user_id=current_user_id)
    db.session.add(new_thread)
    db.session.commit()

    # Fetch the user to include profile info in the response.
    user = User.query.get(current_user_id)

    return jsonify({
        "msg": "Thread created",
        "thread": {
            "id": new_thread.id,
            "title": new_thread.title,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar
            },
            "timestamp": new_thread.timestamp.isoformat()
        }
    }), 201


# Get Threads Endpoint: /api/threads (GET)
@app.route('/api/threads', methods=['GET'])
@jwt_required()
def get_threads():
    threads = Thread.query.order_by(Thread.timestamp.desc()).all()
    thread_list = []
    for thread in threads:
        # Get the thread creator's user info
        thread_user = User.query.get(thread.user_id)

        # Build a flat list of comments with user info
        comments_data = []
        for c in thread.comments:
            if c.user:  # Using the relationship we added
                comment_user_data = {
                    "id": c.user.id,
                    "username": c.user.username,
                    "avatar": c.user.avatar
                }
            else:
                comment_user_data = None

            # Add an empty 'replies' array for nesting
            comments_data.append({
                "id": c.id,
                "user_id": c.user_id,
                "content": c.content,
                "parent_id": c.parent_id,
                "timestamp": c.timestamp.isoformat(),
                "user": comment_user_data,
                "replies": []
            })

        # Group comments into nested structure
        grouped_comments = []
        # Create a mapping of comment id -> comment dictionary
        comment_by_id = {comment["id"]: comment for comment in comments_data}
        for comment in comments_data:
            # If the comment is a reply (has a parent_id), add it to its parent's "replies"
            if comment["parent_id"]:
                parent = comment_by_id.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment)
            else:
                # Top-level comments go directly into the grouped_comments list
                grouped_comments.append(comment)

        # Build the thread data using grouped (nested) comments
        thread_list.append({
            "id": thread.id,
            "title": thread.title,
            "user": {
                "id": thread_user.id,
                "username": thread_user.username,
                "avatar": thread_user.avatar
            } if thread_user else None,
            "timestamp": thread.timestamp.isoformat(),
            "comments": grouped_comments  # Use the nested comments here
        })
    return jsonify({"threads": thread_list}), 200





# Post Comment to a Thread Endpoint: /api/threads/<int:thread_id>/comments
@app.route('/api/threads/<int:thread_id>/comments', methods=['POST'])
@jwt_required()
def post_thread_comment(thread_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    content = data.get('content')
    parent_id = data.get('parent_id')  # Optional: ID of the parent comment for nesting
    if not content or content.strip() == "":
        return jsonify({"msg": "Comment cannot be empty"}), 400

    new_comment = Comment(
        thread_id=thread_id,
        user_id=current_user_id,
        content=content,
        parent_id=parent_id  # Will be None if not provided (i.e., a top-level comment)
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
    "msg": "Comment posted",
    "comment": {
        "id": new_comment.id,
        "thread_id": new_comment.thread_id,
        "user_id": new_comment.user_id,
        "content": new_comment.content,
        "parent_id": new_comment.parent_id,
        "timestamp": new_comment.timestamp.isoformat(),
        "user": {
            "id": new_comment.user.id,
            "username": new_comment.user.username,
            "avatar": new_comment.user.avatar
        }
    }
}), 201

@app.route('/api/threads/<int:thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    current_user_id = get_jwt_identity()       # Hent innlogget bruker
    thread = Thread.query.get(thread_id)       # Finn tråden i databasen
    
    if not thread:
        return jsonify({"msg": "Thread does not exist"}), 404
    
    # Sjekk om denne tråden tilhører innlogget bruker
    if thread.user_id != int(current_user_id):
        return jsonify({"msg": "Not authorized"}), 403

    # Slett tråden
    db.session.delete(thread)
    db.session.commit()
    
    return jsonify({"msg": "Thread deleted"}), 200

@app.route('/api/threads/<int:thread_id>', methods=['PUT'])
@jwt_required()
def update_thread(thread_id):
    current_user_id = get_jwt_identity()
    thread = Thread.query.get(thread_id)
    
    if not thread:
        return jsonify({"msg": "Thread does not exist"}), 404
    
    if thread.user_id != int(current_user_id):
        return jsonify({"msg": "Not authorized"}), 403
    
    data = request.get_json()
    new_title = data.get('title')
    
    # En enkel sjekk om tittelen er gyldig
    if not new_title or not new_title.strip():
        return jsonify({"msg": "Title cannot be empty"}), 400
    
    # Oppdater
    thread.title = new_title.strip()
    db.session.commit()

    return jsonify({"msg": "Thread updated"}), 200

# Protected Example Endpoint: /api/protected
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    return jsonify({"msg": f"Hello, {user.email}!"}), 200

# NEW: Endpoint for uploading songs: /api/upload-song
@app.route('/api/upload-song-old', methods=['POST'])
@jwt_required()
def upload_song_old():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not check_user_rank(user, allowed_ranks_for_song_management):
        return jsonify({"msg": "Insufficient rank to upload songs."}), 403

    if 'audio_file' not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"msg": "Invalid file type. Allowed types: mp3, wav, flac, ogg"}), 400

    try:
        filename = secure_filename(file.filename)
        file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path_on_server)

        # Use the filename (without extension) as the song title.
        song_title = os.path.splitext(filename)[0]
        # Old implementation assumes a 'file_path' field (which may not exist in the updated model)
        new_song = Song(
            title=song_title,
            artist=None,
            # This field is for legacy compatibility—if your model doesn't have it, this may fail.
            # You might decide to store the file path in a different way.
            cover=file_path_on_server,  # or replace with file_path=file_path_on_server if the model supported it
            soundcloudUrl=None
        )
        db.session.add(new_song)
        db.session.commit()

        song_url = '/uploads/' + filename

        return jsonify({
            "msg": "Song uploaded successfully (old)",
            "song": {
                "id": new_song.id,
                "title": new_song.title,
                "artist": new_song.artist,
                "cover": new_song.cover,
                "url": song_url
            }
        }), 201

    except Exception as e:
        print(f"Error uploading song (old): {e}")
        return jsonify({"msg": "Song upload failed (old)"}), 500

    except Exception as e:
        print(f"Error uploading song: {e}")
        return jsonify({"msg": "Song upload failed"}), 500
##Api delete songs
@app.route('/api/delete-song/<int:song_id>', methods=['DELETE'])
@cross_origin()
@jwt_required()
def delete_song(song_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not check_user_rank(user, allowed_ranks_for_song_management):
        return jsonify({"msg": "Insufficient rank to delete songs."}), 403

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found."}), 404

    # Optionally: Delete the file from storage here if needed

    db.session.delete(song)
    db.session.commit()
    return jsonify({"msg": "Song deleted successfully."}), 200

# NEW: Endpoint to get a list of songs: /api/songs (GET)

@app.route('/api/upload-song', methods=['POST'])
@jwt_required()
def upload_song():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    
    if not check_user_rank(user, allowed_ranks_for_song_management):
        return jsonify({"msg": "Insufficient rank to upload songs."}), 403

    if 'audio_file' not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"msg": "Invalid file type. Allowed types: mp3, wav, flac, ogg"}), 400

    try:
        filename = secure_filename(file.filename)
        file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path_on_server)

        song_title = os.path.splitext(filename)[0]
        new_song = Song(
            title=song_title,
            artist=None,
            cover=file_path_on_server,       # Use 'cover' field for the uploaded file path
            soundcloudUrl=None               # Set this if available
        )
        db.session.add(new_song)
        db.session.commit()

        song_url = '/uploads/' + filename

        return jsonify({
            "msg": "Song uploaded successfully",
            "song": {
                "id": new_song.id,
                "title": new_song.title,
                "artist": new_song.artist,
                "cover": new_song.cover,
                "soundcloudUrl": new_song.soundcloudUrl,
                "url": song_url
            }
        }), 201

    except Exception as e:
        print(f"Error uploading song: {e}")
        return jsonify({"msg": "Song upload failed"}), 500

@app.route('/api/songs', methods=['GET'])
def get_songs():
    try:
        songs = Song.query.order_by(Song.upload_timestamp.desc()).all()
        songs_list = []
        for song in songs:
            songs_list.append({
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "cover": song.cover,
                "soundcloudUrl": song.soundcloudUrl
            })
        return jsonify({"songs": songs_list}), 200
    except Exception as e:
        print("Error in get_songs endpoint:", e)
        return jsonify({"error": "Failed to fetch songs"}), 500



@app.route('/api/upload-banner', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@jwt_required()
def upload_banner():
    if request.method == 'OPTIONS':
        return '', 200

    if 'banner' not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files['banner']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    if not file.content_type.startswith('image/'):
        return jsonify({"msg": "Invalid file type, only images are allowed"}), 400

    try:
        # Upload using Cloudinary (or any other service)
        result = cloudinary.uploader.upload(
            file,
            folder=f"user_{get_jwt_identity()}/banners",
            public_id=f"banner_{get_jwt_identity()}",
            overwrite=True
        )
        new_banner_url = result['secure_url']
        
        # Update the user's banner field in the database
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        user.banner = new_banner_url
        db.session.commit()
        
        return jsonify({"url": new_banner_url}), 200
    except Exception as e:
        print("Error uploading banner:", e)
        return jsonify({"msg": "Banner upload failed"}), 500


# -------------------------------
# GET all news items (optional JWT)
# -------------------------------
@app.route('/api/news', methods=['GET'])
@jwt_required(optional=True)  # Allows both guest and logged-in users
def get_news():
    try:
        news_items = News.query.order_by(News.date.desc()).all()
        data = [{
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'date': item.date.isoformat()
        } for item in news_items]

        response = make_response(jsonify(data))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------------------------------
# POST a news item
# -------------------------------
@app.route('/api/news', methods=['POST'])
@jwt_required()
def create_news():
    print("RAW HEADERS:", request.headers)
    print("JWT Identity:", get_jwt_identity())
    data = request.get_json()
    current_user_id = get_jwt_identity()

    news_item = News(
        title=data['title'],
        content=data['content'],
        user_id=current_user_id
    )

    db.session.add(news_item)
    db.session.commit()

    return jsonify({
        'id': news_item.id,
        'title': news_item.title,
        'content': news_item.content,
        'date': news_item.date.isoformat(),
        'user': {
            'id': news_item.user.id,
            'username': news_item.user.username
        }
    }), 201


# -------------------------------
# PUT (Update) a news item
# -------------------------------
@app.route('/api/news/<int:news_id>', methods=['PUT'])
@jwt_required()
def update_news(news_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()

    news_item = News.query.get_or_404(news_id)

    if news_item.user_id != current_user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    news_item.title = data.get('title', news_item.title)
    news_item.content = data.get('content', news_item.content)

    db.session.commit()

    return jsonify({
        'id': news_item.id,
        'title': news_item.title,
        'content': news_item.content,
        'date': news_item.date.isoformat(),
        'user': {
            'id': news_item.user.id,
            'username': news_item.user.username
        }
    })


# -------------------------------
# DELETE a news item
# -------------------------------
@app.route('/api/news/<int:news_id>', methods=['DELETE'])
@jwt_required()
def delete_news(news_id):
    try:
        current_user_id = int(get_jwt_identity())  # Ensure integer
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        news_item = News.query.get_or_404(news_id)

        # Only allow author or admin
        if news_item.user_id != user.id and not user.has_role(['admin']):
            return jsonify({'message': 'Unauthorized'}), 403

        db.session.delete(news_item)
        db.session.commit()

        return jsonify({'message': 'News item deleted successfully'}), 200

    except Exception as e:
        print(f"🔥 DELETE /api/news/{news_id} failed:", e)
        return jsonify({'message': 'Internal server error'}), 500




# EndPoint to track dashboard visits
@app.route('/api/track-dashboard-visit', methods=['POST'])
@jwt_required()
def track_dashboard_visit():
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    seconds = int(data.get('seconds', 60))  # Default to 60 if not provided
    new_activity = Activity(
        user_id=int(current_user_id),
        activity_type='dashboard_visit',
        duration_seconds=seconds,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(new_activity)
    db.session.commit()
    return jsonify({"msg": "Dashboard activity tracked"}), 201

# Todo: update this logic to show activity based on hours
@app.route('/api/get-weekly-activity', methods=['GET'])
@jwt_required()
def get_weekly_activity():
    current_user_id = get_jwt_identity()
    today = datetime.now(timezone.utc)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Sum duration_seconds for this week
    total_seconds = db.session.query(
        db.func.sum(Activity.duration_seconds)
    ).filter(
        Activity.user_id == int(current_user_id),
        Activity.activity_type == 'dashboard_visit',
        Activity.timestamp >= start_of_week
    ).scalar() or 0

    total_hours = round(total_seconds / 3600, 2)
    return jsonify({"weekly_hours": total_hours}), 200

@app.route('/api/get-notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user_id = get_jwt_identity()
    # Fetch unread notifications, ordered by timestamp descending
    user_notifications = Notification.query.filter_by(
        user_id=current_user_id, is_read=False
    ).order_by(Notification.timestamp.desc()).all()
    notifications_list = []
    for notification in user_notifications:
        notifications_list.append({
            'id': notification.id,
            'type': notification.notification_type,
            'message': notification.message,
            'timestamp': notification.timestamp.isoformat(),
            'is_read': notification.is_read,
            'related_object_id': notification.related_object_id
        })
    return jsonify(notifications_list), 200



@app.route('/api/mark-notifications-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    current_user_id = get_jwt_identity()
    # Query all unread notifications for the current user
    notifications = Notification.query.filter_by(user_id=current_user_id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({"msg": "All notifications marked as read"}), 200


@app.route('/api/dashboard/latest-activity')
def get_latest_activity():
    """
    API endpoint to get the latest activity data - now showing recently joined users from the database.
    Fetching recently joined users based on user.id (as signup date is not explicitly tracked yet).
    Using user.id as a proxy for signup order.
    """
    try:
        # Fetch the 5 most recently registered users from the database, ordered by user.id (descending)
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()

        latest_activity_data = []
        for user in recent_users:
            activity_item = {
                "text": f"New user joined: {user.username or user.email}",  # Use username if available, otherwise email
                "timestamp": "Just now"  #  Simpler timestamp for now
            }
            latest_activity_data.append(activity_item)

        return jsonify(latest_activity=latest_activity_data)

    except Exception as e:
        print(f"Database error fetching latest users: {e}")
        return jsonify({"error": "Failed to fetch latest users"}), 500



# --- Update the /api/events POST route ---
@app.route('/api/events', methods=['POST'])
@jwt_required()
def create_event():
    """Endpoint to create a new event, now with image upload and template selection."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    # Check if the user has the 'developer' role (case-insensitive)
    if not user or not any(role.name.lower() == 'developer' for role in user.roles):
        return jsonify({"msg": "Developer role required"}), 403

    # --- Data from request ---
    event_name = request.form.get('event_name')  # Get event name from form data
    event_date_str = request.form.get('event_date')  # Get date string from form data
    event_time_str = request.form.get('event_time')  # Get time string from form data
    event_description = request.form.get('event_description')  # Get description from form data
    template_name = request.form.get('template_name')  # Get template name from form data
    notify_users_str = request.form.get('notify_users')  # Get notify_users as string
    notify_users = notify_users_str.lower() == 'true' if notify_users_str else False  # Convert string to boolean

    event_image_file = request.files.get('event_image')  # Get the uploaded image file

    if not event_name or not event_date_str or not event_time_str or not template_name:
        return jsonify({"msg": "Event name, date, time, and template are required"}), 400

    try:
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()  # Parse date string
        event_time = datetime.strptime(event_time_str, '%H:%M').time()    # Parse time string
    except ValueError:
        return jsonify({"msg": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."}), 400

    image_url = None  # Initialize image_url to None in case no image is uploaded
    if event_image_file:
        try:
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(
                event_image_file,
                folder="event_background_images",
                public_id=f"event_bg_{datetime.now().timestamp()}",
                overwrite=True
            )
            image_url = upload_result['secure_url']
        except Exception as e:
            print(f"Error uploading image to Cloudinary: {e}")
            return jsonify({"msg": "Image upload to Cloudinary failed"}), 500

    new_event = Event(
        event_name=event_name,
        event_date=event_date,
        event_time=event_time,
        event_description=event_description,
        event_image_path=image_url,
        template_name=template_name
    )

    db.session.add(new_event)
    db.session.commit()

    if notify_users:
        users_to_notify = User.query.all()
        for user_to_notify in users_to_notify:
            notification = Notification(
                user_id=user_to_notify.id,
                notification_type='event_created',
                message=f"New Event Created: {event_name}",
                related_object_id=new_event.id
            )
            db.session.add(notification)
        db.session.commit()

    return jsonify({"msg": "Event created successfully", "event_id": new_event.id}), 201


# NEW: API endpoint to get upcoming events: /api/events (GET)
@app.route('/api/events', methods=['GET'])
@jwt_required()  # Protect this endpoint as well, require login to view events
def get_events():
    """
    API endpoint to get a list of upcoming events.
    Requires authentication (JWT token).
    Returns a list of events ordered by date and time.
    """
    try:
        # Get all events from the database, ordered by event_date and then event_time
        events = Event.query.order_by(Event.event_date, Event.event_time).all()

        events_list = []
        for event in events:
            events_list.append({
                "id": event.id,
                "event_name": event.event_name,
                "event_date": event.event_date.isoformat(), # Format date as string for JSON
                "event_time": event.event_time.isoformat(), # Format time as string for JSON
                "event_description": event.event_description
            })

        return jsonify({"events": events_list}), 200 # Return list of events in JSON

    except Exception as e:
        print(f"Database error fetching events: {e}") # Log database errors
        return jsonify({"error": "Failed to fetch events"}), 500 # Return error response
    
@app.route('/api/events/<int:event_id>', methods=['GET'])
@jwt_required()  # Keep JWT protection, as events are likely private
def get_event_by_id(event_id):
    """API endpoint to get details of a single event by its ID."""
    event = Event.query.get(event_id)  # Fetch event from database by ID

    if event:
        event_data = {  # Format event data for JSON response
            "id": event.id,
            "event_name": event.event_name,
            "event_date": event.event_date.isoformat(),
            "event_time": event.event_time.isoformat(),
            "event_description": event.event_description,
            "event_image_path": event.event_image_path,
            "template_name": event.template_name
        }
        return jsonify({"event": event_data}), 200  # Return event data in JSON
    else:
        return jsonify({"message": "Event not found"}), 404  # Return 404 if event not found
    

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Optional: restrict event deletion to certain roles
    if not any(role.name.lower() == 'developer' for role in user.roles):
        return jsonify({"msg": "Only developers can delete events"}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({"msg": "Event deleted successfully"}), 200








# ===================== START get_krenke_level ENDPOINT =====================
@app.route('/api/get-krenke-level', methods=['GET'])
@jwt_required()
def get_krenke_level():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if not user:
            return jsonify({"msg": "User not found"}), 404
        level = user.krenke_level if user.krenke_level is not None else 50
        return jsonify({"level": level}), 200
    except Exception as e:
        print(f"Error in get_krenke_level: {e}")
        return jsonify({"msg": "Internal server error"}), 500
# ===================== END get_krenke_level ENDPOINT =====================

# ===================== START update_krenke_level ENDPOINT =====================
@app.route('/api/update-krenke-level', methods=['POST'])
@jwt_required()
def update_krenke_level():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    data = request.get_json()
    level = data.get("level")
    
    if level is None:
        return jsonify({"msg": "Missing level parameter"}), 400
    
    try:
        level = float(level)
    except ValueError:
        return jsonify({"msg": "Level must be a number"}), 400
    
    user.krenke_level = level
    db.session.commit()
    return jsonify({"msg": "Krenke level updated", "level": user.krenke_level}), 200
# ===================== END update_krenke_level ENDPOINT =====================




# ===================== START update_user_role ENDPOINT =====================
@app.route('/api/update-user-role', methods=['PUT'])
@jwt_required()
def update_user_role():
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    # ---> Check if current user is authorized (only developers can update roles)
    if not any(role.name.lower() == 'developer' for role in admin_user.roles):
        return jsonify({"msg": "Only developers can update user roles"}), 403


    data = request.get_json()
    user_id = data.get('user_id')     # <-- ID of the user whose role you want to update
    new_role = data.get('new_role')    # <-- New role or rank to assign

    # ---> Validate required parameters
    if not user_id or not new_role:
        return jsonify({"msg": "Missing user_id or new_role parameter"}), 400

    user_to_update = User.query.get(int(user_id))
    if not user_to_update:
        return jsonify({"msg": "User not found"}), 404

    # ---> Update the user's role in the database
    user_to_update.rank = new_role
    db.session.commit()
    
    return jsonify({"msg": "User role updated successfully"}), 200
# ===================== END update_user_role ENDPOINT =====================

# ===================== START get_users ENDPOINT =====================
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        # Build a list of role objects
        user_roles = [{
            "id": role.id,
            "name": role.name,
            "badge_icon": role.badge_icon,
            "badge_color": role.badge_color
        } for role in user.roles]

        users_list.append({
            'id': user.id,
            'username': user.username if user.username else '',
            'email': user.email if user.email else '',
            # Include the user's roles here
            'roles': user_roles
        })
    return jsonify({'users': users_list}), 200

# ===================== END get_users ENDPOINT =====================



# ===================== START get_roles ENDPOINT =====================
@app.route('/api/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    roles_list = [{
        'id': role.id,
        'name': role.name,
        'badge_icon': role.badge_icon,
        'badge_color': role.badge_color
    } for role in roles]
    return jsonify({'roles': roles_list}), 200
# ===================== END get_roles ENDPOINT =====================

# ===================== START update_user_roles ENDPOINT =====================
@app.route('/api/update-user-roles', methods=['PUT'])
@jwt_required()
def update_user_roles():
    data = request.get_json()
    user_id_to_update = data.get('user_id') # Ensure you're using the correct key
    role_ids = data.get('role_ids')       # Ensure you're using the correct key

    user = User.query.get(user_id_to_update)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Update user roles logic here
    for role_id in role_ids:
        role = Role.query.get(role_id)
        if role:
            user.roles.append(role)
    db.session.commit()

    # --- Real-time update using python-socketio client ---
    sio_client = py_socketio.Client()
    print("Flask backend: Attempting to connect to Socket.IO server...")
    try:
        sio_client.connect('http://localhost:3000') # Replace if needed
        print("Flask backend: Successfully connected.")
        roles = [{"id": role.id, "name": role.name, "badge_icon": role.badge_icon, "badge_color": role.badge_color}
                 for role in user.roles]
        print("Flask backend: Emitting 'roleUpdateFromBackend' event...")
        sio_client.emit('roleUpdateFromBackend', {'userId': str(user.id), 'roles': roles}) # Ensure userId is a string
        print("Flask backend: 'roleUpdateFromBackend' event emitted.")
        print("Flask backend: Disconnecting from Socket.IO server...")
        sio_client.disconnect()
        print("Flask backend: Disconnected from Socket.IO server.")
    except py_socketio.exceptions.ConnectionError as e:
        print(f"Flask backend: Connection error: {e}")
        import traceback
        traceback.print_exc()
        # You might want to log this error or handle it differently
        pass # Or maybe return an error status if real-time update is critical

    return jsonify({
        "msg": "User roles updated successfully",
        "updatedUser": {
            "id": user.id,
            "roles": [{"id": role.id, "name": role.name, "badge_icon": role.badge_icon, "badge_color": role.badge_color}
                      for role in user.roles]
        }
    }), 200

# ===================== END update_user_roles ENDPOINT ===================

# ===================== START Demote_user_roles ENDPOINT =====================
@app.route('/api/demote-user', methods=['PUT'])
@jwt_required()
def demote_user():
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    if not any(role.name in ['Admin', 'developer'] for role in admin_user.roles):
        return jsonify({"msg": "Only admins or developers can demote users"}), 403

    data = request.get_json()
    user_id = data.get('user_id')
    role_to_remove = data.get('role_to_remove')

    if not user_id or not role_to_remove:
        return jsonify({"msg": "Missing user_id or role_to_remove parameter"}), 400

    user_to_demote = User.query.get(int(user_id))
    if not user_to_demote:
        return jsonify({"msg": "User not found"}), 404

    role_obj = Role.query.filter_by(name=role_to_remove).first()
    if not role_obj:
        return jsonify({"msg": "Role not found"}), 404

    if role_obj not in user_to_demote.roles:
        return jsonify({"msg": "User does not have that role"}), 400

    # Remove the role and commit the changes
    user_to_demote.roles.remove(role_obj)
    db.session.commit()

    updated_roles = [{
        "id": role.id,
        "name": role.name,
        "badge_icon": role.badge_icon,
        "badge_color": role.badge_color,
    } for role in user_to_demote.roles]

    # Optional: Emit a websocket event to notify connected clients of the change
    sio_client = py_socketio.Client()
    try:
        sio_client.connect('http://localhost:3000')  # Replace if needed
        sio_client.emit('roleUpdateFromBackend', {
            'userId': str(user_to_demote.id),
            'roles': updated_roles
        })
        sio_client.disconnect()
    except py_socketio.exceptions.ConnectionError as e:
        print(f"Socket connection error: {e}")

    return jsonify({
        "msg": "User demoted successfully",
        "updatedUser": {
            "id": user_to_demote.id,
            "roles": updated_roles
        }
    }), 200
# ===================== END Demote_user_roles ENDPOINT =====================



# Endpoint to add a new role
@app.route('/api/roles', methods=['POST'])
@jwt_required()
def create_role():
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))

    # Ensure only users with the 'Admin' or 'Developer' role can add roles
    if not any(role.name in ['Admin', 'developer'] for role in admin_user.roles):
        return jsonify({"msg": "Only Admins or Developers can create roles"}), 403

    data = request.get_json()
    role_name = data.get("name")
    badge_icon = data.get("badge_icon")
    badge_color = data.get("badge_color")

    if not role_name:
        return jsonify({"msg": "Role name is required"}), 400

    new_role = Role(name=role_name, badge_icon=badge_icon, badge_color=badge_color)
    db.session.add(new_role)
    db.session.commit()

    return jsonify({"msg": "Role created successfully", "role": {
        "id": new_role.id,
        "name": new_role.name,
        "badge_icon": new_role.badge_icon,
        "badge_color": new_role.badge_color
    }}), 201


# Endpoint to delete a role
@app.route('/api/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    # Allow deletion only if the user has the Admin or Developer role
    if not any(role.name in ['Admin', 'developer'] for role in admin_user.roles):
        return jsonify({"msg": "Only Admins or Developers can delete roles"}), 403

    role = Role.query.get(role_id)
    if not role:
        return jsonify({"msg": "Role not found"}), 404

    # Optional: Prevent deletion if the role is assigned to any user
    if role.users:
        return jsonify({"msg": "Role is assigned to users. Unassign before deletion."}), 400

    db.session.delete(role)
    db.session.commit()
    return jsonify({"msg": "Role deleted successfully"}), 200


# GET fitte_points from User table
@app.route('/api/get-fitte-points', methods=['GET'])
@jwt_required()
def get_fitte_points():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"points": user.fitte_points}), 200

@app.route('/api/get-daily-claim-status', methods=['GET'])
@jwt_required()
def get_daily_claim_status():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    now = datetime.now(timezone.utc)

    if user.last_daily_reward_claim:
        last_claim = user.last_daily_reward_claim
        if last_claim.tzinfo is None:
            last_claim = last_claim.replace(tzinfo=timezone.utc)
        next_claim_time = last_claim + timedelta(days=1)
    else:
        next_claim_time = now

    daily_claimed = user.last_daily_reward_claim is not None and now < next_claim_time

    return jsonify({
        "dailyClaimed": daily_claimed,
        "nextClaimTime": next_claim_time.isoformat()
    }), 200


# POST update fitte_points in User table
from datetime import datetime, timezone, timedelta

@app.route('/api/update-fitte-points', methods=['POST'])
@jwt_required()
def update_fitte_points():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_points = data.get("points")
    is_daily_reward = data.get("is_daily_reward", False)
    
    if not isinstance(new_points, int):
        return jsonify({"msg": "Invalid points value"}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    now = datetime.now(timezone.utc)

    unlocked_achievements = []  # Will store new unlocks

    if is_daily_reward:
        if user.last_daily_reward_claim:
            last_claim = user.last_daily_reward_claim
            if last_claim.tzinfo is None:
                last_claim = last_claim.replace(tzinfo=timezone.utc)
            # Check cooldown (deny if less than 24h)
            if (now - last_claim) < timedelta(days=1):
                return jsonify({"msg": "You can only claim the daily reward once per day"}), 400
        else:
            last_claim = now - timedelta(days=1)

        # Calculate cooldown for the frontend
        elapsed = (now - last_claim).total_seconds()
        cooldown_seconds = max(0, 24*3600 - elapsed)

        user.last_daily_reward_claim = now

        # 1. Increment daily claim count
        user.daily_claim_count = (user.daily_claim_count or 0) + 1

        # 2. Check and unlock achievements for daily claims

        achievements = Achievement.query.filter_by(condition_type='daily_claims').all()
        for ach in achievements:
            if user.daily_claim_count >= ach.condition_value:
                already = UserAchievement.query.filter_by(user_id=user.id, achievement_id=ach.id).first()
                if not already:
                    new_ua = UserAchievement(
                        user_id=user.id,
                        achievement_id=ach.id,
                        unlocked=True,
                        unlocked_at=now
                    )
                    db.session.add(new_ua)
                    unlocked_achievements.append({
                        "id": ach.id,
                        "title": ach.name,
                        "description": ach.description
                    })

        # Emit socket event
        socketio.emit(
            'daily_reward_claimed',
            {
                'user_id': user_id,
                'cooldown': cooldown_seconds
            },
            namespace='/socket'
        )

    user.fitte_points = new_points
    db.session.commit()

    next_claim_time = None
    if user.last_daily_reward_claim:
        next_claim_time = (user.last_daily_reward_claim + timedelta(days=1)).isoformat()
        
    return jsonify({
        "msg": "Fitte Points updated",
        "points": user.fitte_points,
        "nextClaimTime": next_claim_time,
        "unlockedAchievements": unlocked_achievements
    }), 200



@app.route('/api/music', methods=['GET'])
def get_music():
    return jsonify([serialize_music_song(song) for song in get_ordered_songs()]), 200


@app.route('/api/music', methods=['POST'])
@jwt_required()
def create_music_track():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json() or {}
    normalized = normalize_music_payload(data)
    if not normalized['title'] or not normalized['url']:
        return jsonify({"msg": "Title and url are required"}), 400

    max_position = db.session.query(db.func.max(Song.position)).scalar()
    next_position = (max_position or 0) + 1 if max_position is not None else 0

    if normalized['featured']:
        Song.query.update({Song.featured: False})

    new_song = Song(
        title=normalized['title'],
        artist=normalized['author_name'],
        cover=normalized['thumbnail_url'],
        soundcloudUrl=normalized['url'],
        url=normalized['url'],
        author_name=normalized['author_name'],
        thumbnail_url=normalized['thumbnail_url'],
        duration=normalized['duration'],
        featured=normalized['featured'],
        position=next_position,
    )
    db.session.add(new_song)
    db.session.commit()

    return jsonify({
        "msg": "Track added",
        "track": serialize_music_song(new_song),
    }), 201


@app.route('/api/music/reorder', methods=['PUT'])
@jwt_required()
def reorder_music_tracks():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    try:
        data = request.get_json() or {}
        tracks = data.get('tracks', [])
        if not tracks:
            return jsonify({"msg": "No tracks provided for reordering"}), 400

        for track_data in tracks:
            if not isinstance(track_data, dict) or 'id' not in track_data or 'position' not in track_data:
                return jsonify({"msg": "Invalid track data format"}), 400

            song = Song.query.get(track_data['id'])
            if song:
                song.position = track_data['position']
                db.session.add(song)

        db.session.commit()
        ordered_songs = get_ordered_songs()
        return jsonify({
            "msg": "Music reordered successfully",
            "tracks": [serialize_music_song(song) for song in ordered_songs],
        }), 200
    except Exception as exc:
        db.session.rollback()
        print(f"Error reordering music: {exc}")
        return jsonify({"msg": "Failed to reorder music"}), 500


@app.route('/api/music/<int:song_id>/featured', methods=['PUT'])
@jwt_required()
def set_music_track_featured(song_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Track not found"}), 404

    Song.query.update({Song.featured: False})
    song.featured = True
    db.session.add(song)
    db.session.commit()

    return jsonify({
        "msg": "Featured track updated",
        "tracks": [serialize_music_song(item) for item in get_ordered_songs()],
    }), 200


@app.route('/api/music/<int:song_id>', methods=['DELETE'])
@jwt_required()
def delete_music_track(song_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Track not found"}), 404

    db.session.delete(song)
    db.session.commit()

    ordered_songs = get_ordered_songs()
    for index, item in enumerate(ordered_songs):
        if item.position != index:
            item.position = index
            db.session.add(item)
    db.session.commit()

    return jsonify({"msg": "Track deleted"}), 200


@app.route('/api/playlist', methods=['GET'])
def get_playlist():
    return jsonify({"songs": [serialize_playlist_song(song) for song in get_ordered_songs()]}), 200


@app.route('/api/playlist/reorder', methods=['PUT'])
@jwt_required()
def reorder_playlist():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    try:
        data = request.get_json() or {}
        songs = data.get('songs', [])
        if not songs:
            return jsonify({"msg": "No songs provided for reordering"}), 400

        for song_data in songs:
            if not isinstance(song_data, dict) or 'id' not in song_data or 'position' not in song_data:
                return jsonify({"msg": "Invalid song data format"}), 400

            song = Song.query.get(song_data['id'])
            if song:
                song.position = song_data['position']
                db.session.add(song)

        db.session.commit()
        songs_in_db = get_ordered_songs()
        return jsonify({
            "msg": "Playlist reordered successfully",
            "songs": [serialize_playlist_song(song) for song in songs_in_db],
        }), 200
    except Exception as exc:
        db.session.rollback()
        print(f"Error reordering playlist: {exc}")
        return jsonify({"msg": "Failed to reorder playlist"}), 500


# ===================== START Shops ENDPOINTs =====================

# 1️⃣ Public: List all shop items
@app.route('/api/shop-items', methods=['GET'])
def list_shop_items():
    items = ShopItem.query.order_by(ShopItem.price).all()
    return jsonify([{
      'id':          i.id,
      'name':        i.name,
      'description': i.description,
      'price':       i.price,
      'icon':        i.icon,
      'type':        i.type,
      'rarity':      i.rarity,
      'glow_color':  i.glow_color
    } for i in items]), 200

# 2️⃣ Authenticated: Purchase one
@app.route('/api/purchase-item', methods=['POST'])
@jwt_required()
def purchase_item():
    user_id = get_jwt_identity()
    item_id = request.json.get('itemId')
    
    item = ShopItem.query.get(item_id)
    user = User.query.get(user_id)

    # Check if item exists and if user has enough points
    if not item or user.fitte_points < item.price:
        return jsonify({'msg': 'Cannot purchase'}), 400

    # Check if user already owns the item
    existing = UserShopItem.query.filter_by(user_id=user.id, item_id=item.id).first()
    if existing:
        return jsonify({'msg': 'Already purchased'}), 400

    # Deduct points and save purchase
    user.fitte_points -= item.price
    purchase = UserShopItem(user_id=user.id, item_id=item.id)
    db.session.add(purchase)

    db.session.commit()

    return jsonify({'points': user.fitte_points}), 200


# — now the Admin CRUD: only for developers/admins —

# 3️⃣ Authenticated: Create new shop item
@app.route('/api/shop-items', methods=['POST'])
@jwt_required()
def create_shop_item():
    # you can add a role-check here if needed
    data = request.get_json()
    i = ShopItem(
      name        = data["name"],
      description = data.get("description"),
      price       = data["price"],
      icon        = data.get("icon"),
      type        = data.get("type", "badge"),
      rarity      = data.get("rarity"),
      glow_color  = data.get("glow_color")
    )
    db.session.add(i)
    db.session.commit()
    return jsonify({"msg":"Created","id":i.id}), 201

# 4️⃣ Authenticated: Update an existing item
@app.route('/api/shop-items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_shop_item(item_id):
    i = ShopItem.query.get_or_404(item_id)
    data = request.get_json()
    for f in ("name","description","price","icon","type","rarity","glow_color"):
        if f in data:
            setattr(i, f, data[f])
    db.session.commit()
    return jsonify({"msg":"Updated"}), 200

# 5️⃣ Authenticated: Delete an item
@app.route('/api/shop-items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_shop_item(item_id):
    i = ShopItem.query.get_or_404(item_id)
    # If the icon is a Cloudinary SVG, delete it from Cloudinary
    if i.icon and i.icon.endswith('.svg') and 'cloudinary' in i.icon:
        try:
            # Extract public_id from the URL
            # Example: https://res.cloudinary.com/your_cloud/image/upload/v1234567890/user_1/svg_icons/svg_1_filename.svg
            # public_id = user_1/svg_icons/svg_1_filename (without .svg)
            from urllib.parse import urlparse
            import os
            path = urlparse(i.icon).path  # /your_cloud/image/upload/v1234567890/user_1/svg_icons/svg_1_filename.svg
            # Remove version and extension
            parts = path.split('/')
            # Find the index of 'upload' and get everything after it except the extension
            if 'upload' in parts:
                idx = parts.index('upload')
                public_id_with_ext = '/'.join(parts[idx+1:])
                public_id = os.path.splitext(public_id_with_ext)[0]
                cloudinary.uploader.destroy(public_id, resource_type="raw")
        except Exception as e:
            print(f"Error deleting SVG from Cloudinary: {e}")

    db.session.delete(i)
    db.session.commit()
    return jsonify({"msg":"Deleted"}), 200

@app.route('/api/remove-item', methods=['POST'])
@jwt_required()
def remove_item():
    user_id = get_jwt_identity()
    item_id = request.json.get('itemId')
    
    # Find the purchased item
    purchase = UserShopItem.query.filter_by(user_id=user_id, item_id=item_id).first()
    if not purchase:
        return jsonify({'msg': 'Item not found'}), 404

    # Delete the purchase record
    db.session.delete(purchase)
    db.session.commit()
    return jsonify({'msg': 'Item removed'}), 200

# 6️⃣ Authenticated: List purchased items (for logged-in user)
@app.route('/api/purchased-items', methods=['GET'])
@jwt_required()
def list_purchased_items():
    user_id = get_jwt_identity()
    purchases = UserShopItem.query.filter_by(user_id=user_id).all()
    return jsonify([{
    'id': p.item.id,
    'name': p.item.name,
    'description': p.item.description,
    'price': p.item.price,
    'icon': p.item.icon,
    'type': p.item.type,
    'rarity': p.item.rarity,          
    'glow_color': p.item.glow_color     
} for p in purchases]), 200

# ===================== END Shops ENDPOINTs =====================





@app.route('/api/playlist', methods=['POST'])
@jwt_required()
def add_song():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json() or {}
    normalized = normalize_music_payload(data)
    if not normalized['title'] or not normalized['url']:
        return jsonify({"msg": "Title and SoundCloud URL are required"}), 400

    max_position = db.session.query(db.func.max(Song.position)).scalar()
    next_position = (max_position or 0) + 1 if max_position is not None else 0

    new_song = Song(
        title=normalized['title'],
        artist=normalized['author_name'],
        cover=normalized['thumbnail_url'],
        soundcloudUrl=normalized['url'],
        url=normalized['url'],
        author_name=normalized['author_name'],
        thumbnail_url=normalized['thumbnail_url'],
        duration=normalized['duration'],
        featured=normalized['featured'],
        position=next_position,
    )

    if normalized['featured']:
        Song.query.update({Song.featured: False})

    db.session.add(new_song)
    db.session.commit()

    return jsonify({
        "msg": "Song added",
        "song": serialize_playlist_song(new_song),
    }), 201


@app.route('/api/playlist/<int:song_id>', methods=['PUT'])
@jwt_required()
def update_playlist_song(song_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found"}), 404

    data = request.get_json() or {}
    normalized = normalize_music_payload(data)

    song.title = normalized['title'] or song.title
    song.artist = normalized['author_name'] or song.artist
    song.cover = normalized['thumbnail_url'] or song.cover
    song.soundcloudUrl = normalized['url'] or song.soundcloudUrl
    song.url = normalized['url'] or song.url
    song.author_name = normalized['author_name'] or song.author_name
    song.thumbnail_url = normalized['thumbnail_url'] or song.thumbnail_url
    song.duration = normalized['duration'] or song.duration

    if normalized['featured']:
        Song.query.update({Song.featured: False})
        song.featured = True

    db.session.commit()

    return jsonify({
        "msg": "Song updated",
        "song": serialize_playlist_song(song),
    }), 200


@app.route('/api/playlist/<int:song_id>', methods=['DELETE'])
@jwt_required()
def delete_playlist_song(song_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not can_manage_music(user):
        return jsonify({"msg": "Unauthorized"}), 403

    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found"}), 404

    db.session.delete(song)
    db.session.commit()
    return jsonify({"msg": "Song deleted"}), 200

#MAINTENANCE 
# GET maintenance status
@app.route('/api/maintenance', methods=['GET'])
def get_maintenance_mode():
    value = get_setting('maintenance_mode', 'off')
    return jsonify({"maintenance_mode": value}), 200

# POST to set maintenance mode
@app.route('/api/maintenance', methods=['POST'])
@jwt_required()
def set_maintenance_mode():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not any(role.name.lower() in ['admin', 'developer'] for role in user.roles):
        return jsonify({"msg": "Unauthorized"}), 403
    data = request.get_json()
    mode = data.get('mode')
    if mode not in ['on', 'off']:
        return jsonify({"msg": "Invalid mode"}), 400
    set_setting('maintenance_mode', mode)
    
    # Emit updated maintenance status to all clients
    notice_mode = get_setting('notice_maintenance_mode', 'off')
    notice_message = get_setting('notice_maintenance_message', '')
    notice_title = get_setting('notice_maintenance_title', '')
    notice_updated_at = get_setting('notice_maintenance_updated_at', '')
    notice_ref = get_setting('notice_maintenance_ref', '')
    socketio.emit('maintenance_status', {
        'maintenance_mode': mode,
        'notice_maintenance_mode': notice_mode,
        'notice_maintenance_message': notice_message,
        'notice_maintenance_title': notice_title,
        'notice_maintenance_updated_at': notice_updated_at,
        'notice_maintenance_ref': notice_ref
    })
    
    return jsonify({"msg": f"Maintenance mode set to {mode}"}), 200

# GET notice maintenance status
@app.route('/api/notice-maintenance', methods=['GET'])
def get_notice_maintenance_mode():
    value = get_setting('notice_maintenance_mode', 'off')
    message = get_setting('notice_maintenance_message', '')
    title = get_setting('notice_maintenance_title', '')
    updated_at = get_setting('notice_maintenance_updated_at', '')
    ref = get_setting('notice_maintenance_ref', '')
    return jsonify({
        "notice_maintenance_mode": value,
        "notice_maintenance_message": message,
        "notice_maintenance_title": title,
        "notice_maintenance_updated_at": updated_at,
        "notice_maintenance_ref": ref
    }), 200

# POST to set notice maintenance mode
@app.route('/api/notice-maintenance', methods=['POST'])
@jwt_required()
def set_notice_maintenance_mode():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not any(role.name.lower() in ['admin', 'developer'] for role in user.roles):
        return jsonify({"msg": "Unauthorized"}), 403
    data = request.get_json()
    mode = data.get('mode')
    message = data.get('message', '')
    title = data.get('title', '').strip()
    if mode not in ['on', 'off']:
        return jsonify({"msg": "Invalid mode"}), 400

    previous_message = get_setting('notice_maintenance_message', '')
    previous_title = get_setting('notice_maintenance_title', '')
    previous_updated_at = get_setting('notice_maintenance_updated_at', '')
    previous_ref = get_setting('notice_maintenance_ref', '')

    now_iso = datetime.utcnow().isoformat()
    current_ref_number = get_setting('notice_maintenance_ref_counter', '0')
    try:
        current_ref_number = int(current_ref_number)
    except (TypeError, ValueError):
        current_ref_number = 0

    inferred_title = (title or message.split('.')[0].split('\n')[0]).strip()[:80] if message else (title or 'Driftsmelding')

    if message and message != previous_message:
        history_items = []
        if previous_message:
            history_items.append({
                'title': previous_title or 'Tidligere driftsmelding',
                'message': previous_message,
                'updated_at': previous_updated_at,
                'ref': previous_ref,
            })
        history_items.extend(get_driftsmelding_history())

        deduped_history = []
        seen_messages = set()
        for item in history_items:
            item_message = item.get('message', '')
            if not item_message or item_message in seen_messages:
                continue
            seen_messages.add(item_message)
            deduped_history.append(item)
            if len(deduped_history) == 3:
                break
        set_driftsmelding_history(deduped_history)

        current_ref_number += 1
        current_ref = f'HMN-MSG-{current_ref_number:03d}'
        set_setting('notice_maintenance_ref_counter', str(current_ref_number))
        set_setting('notice_maintenance_updated_at', now_iso)
        set_setting('notice_maintenance_ref', current_ref)
    else:
        current_ref = previous_ref
        if previous_updated_at:
            now_iso = previous_updated_at
        else:
            set_setting('notice_maintenance_updated_at', now_iso)

    set_setting('notice_maintenance_mode', mode)
    set_setting('notice_maintenance_message', message)
    set_setting('notice_maintenance_title', inferred_title or 'Driftsmelding')
    
    # Emit updated maintenance status to all clients
    maintenance_mode = get_setting('maintenance_mode', 'off')
    socketio.emit('maintenance_status', {
        'maintenance_mode': maintenance_mode,
        'notice_maintenance_mode': mode,
        'notice_maintenance_message': message,
        'notice_maintenance_title': inferred_title or 'Driftsmelding',
        'notice_maintenance_updated_at': now_iso,
        'notice_maintenance_ref': current_ref
    })
    
    return jsonify({"msg": f"Notice maintenance mode set to {mode}"}), 200

@app.route('/api/maintenance-status')
def maintenance_status():
    mode = get_setting('maintenance_mode', 'off')
    notice_mode = get_setting('notice_maintenance_mode', 'off')
    notice_message = get_setting('notice_maintenance_message', '')
    notice_title = get_setting('notice_maintenance_title', '')
    notice_updated_at = get_setting('notice_maintenance_updated_at', '')
    notice_ref = get_setting('notice_maintenance_ref', '')
    return jsonify({
        'maintenance_mode': mode,
        'notice_maintenance_mode': notice_mode,
        'notice_maintenance_message': notice_message,
        'notice_maintenance_title': notice_title,
        'notice_maintenance_updated_at': notice_updated_at,
        'notice_maintenance_ref': notice_ref
    })


@app.route('/api/driftsmeldinger', methods=['GET'])
def get_driftsmeldinger():
    return jsonify(build_driftsmelding_feed()), 200

@app.route('/api/set-maintenance', methods=['POST'])
@jwt_required()
def set_maintenance():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.has_role(['developer', 'Admin']):
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    mode = data.get('mode', 'off')

    if mode not in ['on', 'off']:
        return jsonify({'message': 'Invalid mode'}), 400

    set_setting('maintenance_mode', mode)
    return jsonify({'message': f'Maintenance mode set to {mode}.'})


# -------------------------
# Friendship API Endpoints
# -------------------------

@app.route('/api/friends', methods=['GET'])
@jwt_required()
def get_friends():
    current_user_id = int(get_jwt_identity())
    
    # Use the Friendship table instead
    friendships = Friendship.query.filter_by(user_id=current_user_id).all()

    result = []
    for fr in friendships:
        user = User.query.get(fr.friend_id)
        if user:
            result.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar
            })

    return jsonify({"friends": result}), 200



@app.route('/api/friends', methods=['POST'])
@jwt_required()
def add_friend():
    """Send a friend request / add a friend by their user ID."""
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    friend_id = data.get("friend_id")

    if not friend_id:
        return jsonify({"msg": "Missing friend_id parameter"}), 400
    if friend_id == current_user_id:
        return jsonify({"msg": "Cannot friend yourself"}), 400
    if not User.query.get(friend_id):
        return jsonify({"msg": "User not found"}), 404

    # Prevent duplicates
    exists = Friend.query.filter_by(
        user_id=current_user_id,
        friend_id=friend_id
    ).first()
    if exists:
        return jsonify({"msg": "Already friends"}), 409

    new_friend = Friend(user_id=current_user_id, friend_id=friend_id)
    db.session.add(new_friend)
    db.session.commit()

    return jsonify({"msg": "Friend added"}), 201

# here 
@app.route('/api/friendship/<int:friend_id>', methods=['DELETE'])
@jwt_required()
def delete_friendship(friend_id):
    current_user_id = int(get_jwt_identity())

    # Delete both directions of friendship
    Friendship.query.filter(
        ((Friendship.user_id == current_user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == current_user_id))
    ).delete(synchronize_session=False)

    db.session.commit()
    return jsonify({"msg": "Friendship removed"}), 200

# ✅ Team Member API (Flask endpoints)
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

@app.route('/api/team-members', methods=['GET'])
def get_team_members():
    members = TeamMember.query.order_by(TeamMember.order).all()
    return jsonify({"team_members": [m.to_dict() for m in members]}), 200

@app.route('/api/team-members', methods=['POST'])
@jwt_required()
def create_team_member():
    data = request.form or request.get_json()
    name = data.get("name")
    title = data.get("title")
    bio = data.get("bio")
    order = data.get("order", 0)

    # Optional image upload
    avatar_url = None
    if 'avatar' in request.files:
        file = request.files['avatar']
        result = cloudinary.uploader.upload(file, folder="team")
        avatar_url = result['secure_url']

    new_member = TeamMember(
        name=name,
        title=title,
        bio=bio,
        order=order,
        avatar=avatar_url
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"msg": "Team member created"}), 201

@app.route('/api/team-members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_team_member(member_id):
    member = TeamMember.query.get(member_id)
    if not member:
        return jsonify({"msg": "Team member not found"}), 404

    data = request.form or request.get_json()
    member.name = data.get("name", member.name)
    member.title = data.get("title", member.title)
    member.bio = data.get("bio", member.bio)
    member.order = data.get("order", member.order)

    db.session.commit()
    return jsonify({"msg": "Team member updated"}), 200

@app.route('/api/team-members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_team_member(member_id):
    member = TeamMember.query.get(member_id)
    if not member:
        return jsonify({"msg": "Team member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"msg": "Team member deleted"}), 200

@app.route('/api/team-members/avatar', methods=['POST'])
@jwt_required()
def upload_team_avatar():
    member_id = request.form.get('member_id')
    file = request.files.get('avatar')
    if not member_id or not file:
        return jsonify({"msg": "Missing required data"}), 400

    member = TeamMember.query.get(member_id)
    if not member:
        return jsonify({"msg": "Team member not found"}), 404

    result = cloudinary.uploader.upload(file, folder=f"team/{member_id}")
    member.avatar = result['secure_url']
    db.session.commit()
    return jsonify({"msg": "Avatar updated", "avatar_url": member.avatar}), 200

# app.py (add below other endpoints)
@app.route('/api/user/points', methods=['GET'])
@jwt_required()
def user_points():
    uid = get_jwt_identity()
    user = User.query.get(int(uid))
    return jsonify({"points": user.fitte_points}), 200

#Changelog api
@app.route('/api/changelog', methods=['GET'])
def get_changelog():
    try:
        changelogs = Changelog.query.order_by(Changelog.date.desc()).all()
        return jsonify([changelog.to_dict() for changelog in changelogs]), 200
    except Exception as e:
        print(f"Error fetching changelog: {e}")
        return jsonify({"msg": "Failed to fetch changelog"}), 500
    
@app.route('/api/changelog', methods=['POST'])
@jwt_required()
def add_changelog():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Ensure only authorized users can add changelogs
    if not any(role.name.lower() in ['admin', 'developer'] for role in user.roles):
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.get_json()
    version = data.get('version')
    date = data.get('date')
    added = '\n'.join(data.get('changes', {}).get('Added', []))
    changed = '\n'.join(data.get('changes', {}).get('Changed', []))

    if not version or not date:
        return jsonify({"msg": "Version and date are required"}), 400

    try:
        new_changelog = Changelog(
            version=version,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            added=added,
            changed=changed
        )
        db.session.add(new_changelog)
        db.session.commit()
        return jsonify({"msg": "Changelog entry added successfully"}), 201
    except Exception as e:
        print(f"Error adding changelog: {e}")
        return jsonify({"msg": "Failed to add changelog entry"}), 500

@app.route('/api/changelog/<int:changelog_id>', methods=['DELETE'])
@jwt_required()
def delete_changelog(changelog_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    # Ensure only authorized users can delete changelogs
    if not any(role.name.lower() in ['admin', 'developer'] for role in user.roles):
        return jsonify({"msg": "Unauthorized"}), 403

    changelog = Changelog.query.get(changelog_id)
    if not changelog:
        return jsonify({"msg": "Changelog entry not found"}), 404

    try:
        db.session.delete(changelog)
        db.session.commit()
        return jsonify({"msg": "Changelog entry deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting changelog: {e}")
        return jsonify({"msg": "Failed to delete changelog entry"}), 500

# --- MOVE THIS OUTSIDE, UNINDENTED ---
import io

@app.route('/api/upload-svg', methods=['POST'])
@jwt_required()
def upload_svg():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if 'svg_file' not in request.files:
        return jsonify({"msg": "No file part"}), 400

    file = request.files['svg_file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    if not file.content_type in ['image/svg+xml', 'text/xml', 'application/xml']:
        return jsonify({"msg": "Invalid file type, only SVGs are allowed"}), 400

    # Read and sanitize SVG
    svg_data = file.read().decode('utf-8')
    try:
        sanitized_svg = sanitize_svg(svg_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    # Convert sanitized SVG string to a file-like object
    svg_bytes = sanitized_svg.encode('utf-8')
    svg_file_like = io.BytesIO(svg_bytes)
    svg_file_like.name = file.filename  # Cloudinary uses the .name attribute for the filename

    # Upload to Cloudinary as raw file
    try:
        result = cloudinary.uploader.upload(
            svg_file_like,
            resource_type="raw",  # SVGs are not images in Cloudinary, use 'raw'
            folder=f"user_{user.id}/svg_icons",
            public_id=f"svg_{user.id}_{os.path.splitext(file.filename)[0]}",
            overwrite=True
        )
        svg_url = result['secure_url']
        return jsonify({"msg": "SVG uploaded successfully", "url": svg_url}), 200
    except Exception as e:
        print(f"Error uploading SVG to Cloudinary: {e}")
        return jsonify({"msg": "SVG upload failed"}), 500

@app.route('/api/check-username', methods=['POST'])
@jwt_required()
def check_username():
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({"msg": "Username is required", "available": False}), 400
    
    # Check if username exists (case-insensitive)
    existing_user = User.query.filter(User.username.ilike(username)).first()
    
    # Get current user's username
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))
    
    # If the username exists but belongs to the current user, it's considered available
    if existing_user and existing_user.id == current_user.id:
        return jsonify({"available": True}), 200
    
    return jsonify({"available": not bool(existing_user)}), 200


    

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send initial maintenance status on connection
    mode = get_setting('maintenance_mode', 'off')
    notice_mode = get_setting('notice_maintenance_mode', 'off')
    notice_message = get_setting('notice_maintenance_message', '')
    notice_title = get_setting('notice_maintenance_title', '')
    notice_updated_at = get_setting('notice_maintenance_updated_at', '')
    notice_ref = get_setting('notice_maintenance_ref', '')
    socketio.emit('maintenance_status', {
        'maintenance_mode': mode,
        'notice_maintenance_mode': notice_mode,
        'notice_maintenance_message': notice_message,
        'notice_maintenance_title': notice_title,
        'notice_maintenance_updated_at': notice_updated_at,
        'notice_maintenance_ref': notice_ref
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Add event handler for maintenance status updates
@socketio.on('request_maintenance_status')
def handle_maintenance_status_request():
    mode = get_setting('maintenance_mode', 'off')
    notice_mode = get_setting('notice_maintenance_mode', 'off')
    notice_message = get_setting('notice_maintenance_message', '')
    notice_title = get_setting('notice_maintenance_title', '')
    notice_updated_at = get_setting('notice_maintenance_updated_at', '')
    notice_ref = get_setting('notice_maintenance_ref', '')
    socketio.emit('maintenance_status', {
        'maintenance_mode': mode,
        'notice_maintenance_mode': notice_mode,
        'notice_maintenance_message': notice_message,
        'notice_maintenance_title': notice_title,
        'notice_maintenance_updated_at': notice_updated_at,
        'notice_maintenance_ref': notice_ref
    })

# ===================== Achievements API Endpoints =====================

@app.route('/api/user/achievements', methods=['GET'])
@jwt_required()
def get_user_achievements():
    user_id = get_jwt_identity()
    # Fetch all possible achievements
    all_achievements = Achievement.query.all()
    # Fetch user's unlocked
    unlocked_ids = set(
        ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id)
    )
    # Build a list showing locked/unlocked status
    result = []
    for ach in all_achievements:
        result.append({
        "id": ach.id,
        "title": ach.name,  # or ach.title, just pick one everywhere!
        "description": ach.description,
        "icon": ach.icon,   # or 'svg', just be consistent!
        "achieved": ach.id in unlocked_ids,
        "unlocked_at": next(
            (ua.unlocked_at.isoformat() for ua in UserAchievement.query.filter_by(user_id=user_id, achievement_id=ach.id)), None
        ) if ach.id in unlocked_ids else None,
        "rarity": ach.rarity,
        "glow_color": ach.glow_color
    })
    return jsonify(result)


@app.route('/api/achievements/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_achievement(id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not any(role.name.lower() in ['admin', 'developer'] for role in user.roles):
        return jsonify({"msg": "Unauthorized"}), 403
    achievement = Achievement.query.get(id)
    if not achievement:
        return jsonify({"msg": "Achievement not found"}), 404
    db.session.delete(achievement)
    db.session.commit()
    return jsonify({"msg": "Achievement deleted"}), 200

@app.route('/api/user/achievements/unlock', methods=['POST'])
@jwt_required()
def unlock_achievement():
    user_id = get_jwt_identity()
    achievement_id = request.json.get('achievement_id')
    if not achievement_id:
        return jsonify({"status": "missing_achievement_id"}), 400
    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return jsonify({"status": "invalid_achievement"}), 404
    already = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if already:
        return jsonify({
            "status": "already_unlocked",
            "achievement_id": achievement_id,
            "unlocked_at": already.unlocked_at.isoformat() if already.unlocked_at else None
        }), 200
    now = datetime.now(timezone.utc)
    new_unlock = UserAchievement(user_id=user_id, achievement_id=achievement_id, unlocked_at=now)
    db.session.add(new_unlock)
    db.session.commit()
    return jsonify({
        "status": "ok",
        "achievement_id": achievement_id,
        "unlocked_at": now.isoformat()
    }), 201

# --- Only unlocked achievements for the user ---
@app.route('/api/user/achievements/unlocked', methods=['GET'])
@jwt_required()
def get_user_achievements_unlocked():
    current_user_id = get_jwt_identity()
    achievements = UserAchievement.query.filter_by(user_id=current_user_id).all()
    result = [{
        "id": ua.achievement.id,
        "title": ua.achievement.name,
        "icon": ua.achievement.icon,
        "unlocked_at": ua.unlocked_at.isoformat()
    } for ua in achievements]
    return jsonify(result), 200

# --- Optional: All achievements, not user-specific ---
@app.route('/api/all-achievements', methods=['GET'])

def get_all_achievements():
    all_achievements = Achievement.query.all()
    result = [{
        "id": a.id,
        "title": a.name,
        "icon": a.icon,
        "description": a.description
    } for a in all_achievements]
    return jsonify(result), 200

@app.route('/api/achievements', methods=['POST'])
@jwt_required()
def create_achievement():
    data = request.get_json()
    # Validate the required fields
    if not data.get('title') or not data.get('description'):
        return jsonify({'msg': 'Missing required fields'}), 400

    new_ach = Achievement(
        name=data.get('title'),
        description=data.get('description'),
        icon=data.get('icon'),
        condition_type=data.get('condition_type'),
        condition_value=data.get('condition_value'),
        rarity=data.get('rarity'),
        glow_color=data.get('glow_color')
    )
    db.session.add(new_ach)
    db.session.commit()
    return jsonify({'msg': 'Achievement created', 'id': new_ach.id}), 201


@app.route('/api/achievements/<int:ach_id>', methods=['PUT'])
@jwt_required()
def update_achievement(ach_id):
    data = request.get_json()
    ach = Achievement.query.get(ach_id)
    if not ach:
        return jsonify({'msg': 'Achievement not found'}), 404

    ach.name = data.get('title', ach.name)
    ach.description = data.get('description', ach.description)
    ach.icon = data.get('icon', ach.icon)
    ach.condition_type = data.get('condition_type', ach.condition_type)
    ach.condition_value = data.get('condition_value', ach.condition_value)
    ach.rarity = data.get('rarity', ach.rarity)
    ach.glow_color = data.get('glow_color', ach.glow_color)

    db.session.commit()
    return jsonify({'msg': 'Achievement updated'}), 200


# ===================== END Achievements API Endpoints =====================
def check_and_unlock_clicker_achievements(user):
    stats = {
        "clicks": user.clicker_clicks,
        "autoClickers": user.clicker_auto_clickers,
        "perClick": user.clicker_per_click,
    }
    for ach in GAME_ACHIEVEMENTS:
        progress = stats.get(ach["type"])
        if progress is not None and progress >= ach["value"]:
            unlocked = UserAchievement.query.filter_by(user_id=user.id, achievement_id=ach["id"]).first()
            if not unlocked:
                new_unlock = UserAchievement(
                    user_id=user.id,
                    achievement_id=ach["id"],
                    unlocked_at=datetime.now(timezone.utc)
                )
                db.session.add(new_unlock)

@app.route('/api/clicker/update', methods=['POST'])
@jwt_required()
def update_clicker_stats():
    user_id = get_jwt_identity()
    data = request.json

    # e.g. {"clicks": 1337, "autoClickers": 2, "perClick": 3}
    clicks = data.get('clicks')
    autoClickers = data.get('autoClickers')
    perClick = data.get('perClick')

    user = User.query.get(user_id)
    user.clicker_clicks = clicks
    user.clicker_auto_clickers = autoClickers
    user.clicker_per_click = perClick

    check_and_unlock_clicker_achievements(user)
    db.session.commit()
    return jsonify({"msg": "Updated!"}), 200

@app.route('/api/clicker-achievements', methods=['GET'])
@jwt_required()
def get_clicker_achievements():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Get all unlocked achievement IDs for this user
    unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
    unlocked_ids = {a.achievement_id: a.unlocked_at for a in unlocked}

    # List to return
    achievements = []
    for ach in GAME_ACHIEVEMENTS:
        is_unlocked = ach["id"] in unlocked_ids
        achievements.append({
            "id": ach["id"],
            "title": ach.get("title"),
            "description": ach.get("description"),
            "svg": ach.get("icon") or ach.get("svg"),  # adjust field name
            "rarity": ach.get("rarity", "common"),
            "glow_color": ach.get("glow_color", "#fff"),
            "achieved": is_unlocked,
            "unlocked_at": unlocked_ids.get(ach["id"]),
            "category": "clicker"
        })

    return jsonify(achievements)

@app.route('/api/admin/delete-user-achievement', methods=['POST'])
@jwt_required()  # or some admin auth
def delete_user_achievement():
    user_id = request.json.get('user_id')
    achievement_id = request.json.get('achievement_id')
    ua = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if ua:
        db.session.delete(ua)
        db.session.commit()
        return jsonify({"msg": "Deleted!"})
    return jsonify({"msg": "Not found"}), 404

@app.route('/api/user/<int:user_id>/achievements', methods=['GET'])
@jwt_required()
def get_any_user_achievements(user_id):
    print("JWT identity:", get_jwt_identity())
    # Optionally check if current user is admin/dev
    requesting_user = User.query.get(int(get_jwt_identity()))
    if not any(role.name.lower() in ['admin', 'developer'] for role in requesting_user.roles):
        return jsonify({"msg": "Unauthorized"}), 403

    unlocked = UserAchievement.query.filter_by(user_id=user_id).all()
    result = [{
        "achievement_id": ua.achievement.id,
        "name": ua.achievement.name,
        "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else None,
    } for ua in unlocked]
    return jsonify(result), 200


from mini_games.ClickerApi import clicker_api, init_db
init_db(db, User)  # Pass both db and User model
app.register_blueprint(clicker_api)
# -------------------------
# Run the Flask App
# -------------------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv("FLASK_ENV") != "production"
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)

# Check Username Availability Endpoint: /api/check-username
