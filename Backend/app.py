# -------------------------
# Import Libraries and Modules
# -------------------------
import eventlet
eventlet.monkey_patch()

from dotenv import load_dotenv
import os
import re
import secrets
import requests
from flask import Flask, request, jsonify, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone, timedelta
import socketio as py_socketio
from flask_socketio import SocketIO, Namespace
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
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
try:
    from permissions import DEFAULT_DASHBOARD_FLAVOR, PERMISSION_DEFINITIONS, default_role_metadata, normalize_permission_keys
    from role_permission_routes import register_role_permission_routes
    from soundcloud_routes import soundcloud_bp
    from steam_achievement_utils import select_latest_recent_steam_achievement
except ModuleNotFoundError:
    from Backend.permissions import DEFAULT_DASHBOARD_FLAVOR, PERMISSION_DEFINITIONS, default_role_metadata, normalize_permission_keys
    from Backend.role_permission_routes import register_role_permission_routes
    from Backend.soundcloud_routes import soundcloud_bp
    from Backend.steam_achievement_utils import select_latest_recent_steam_achievement

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
app.secret_key = os.getenv('FLASK_SECRET_KEY') or os.getenv('JWT_SECRET_KEY', 'dev-insecure-secret')
app.config['SECRET_KEY'] = app.secret_key
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

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
CANONICAL_ROLE_NAMES = {
    'admin': 'Admin',
    'developer': 'developer',
    'producer': 'producer',
}


def normalize_role_name(role_name):
    if not isinstance(role_name, str):
        return ''

    cleaned_name = role_name.strip()
    if not cleaned_name:
        return ''

    return CANONICAL_ROLE_NAMES.get(cleaned_name.lower(), cleaned_name)


def resolve_role_for_assignment(role_id):
    role = Role.query.get(role_id)
    if not role:
        return None

    canonical_name = CANONICAL_ROLE_NAMES.get(role.name.lower())
    if not canonical_name:
        return role

    return Role.query.filter_by(name=canonical_name).first() or role

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
        return os.path.join(os.path.dirname(__file__), "test_email.log")
    else:
        # Use the project directory in development!
        return os.path.join(os.path.dirname(__file__), "test_email.log")

log_path = get_dynamic_log_path()
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


@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


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
configured_frontend_origin = (os.getenv('FRONTEND_URL') or '').rstrip('/')
allowed_cors_origins = [
    origin for origin in {
        configured_frontend_origin,
        'http://localhost:5173',
        'http://localhost:5174',
    } if origin
]

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_cors_origins}},
    supports_credentials=True
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.register_blueprint(soundcloud_bp)


@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    identity = jwt_payload.get('sub')
    if not identity:
        return False

    revoked_after_raw = get_user_setting(identity, 'session_revoked_after')
    if not revoked_after_raw:
        return False

    try:
        revoked_after = datetime.fromisoformat(revoked_after_raw.replace('Z', '+00:00'))
    except ValueError:
        return False

    token_iat = jwt_payload.get('iat')
    if token_iat is None:
        return False

    token_issued_at = datetime.fromtimestamp(token_iat, tz=timezone.utc)
    revoked_after_utc = to_utc_datetime(revoked_after)
    return bool(revoked_after_utc and token_issued_at <= revoked_after_utc)


import os
import logging

configured_app_log_path = os.getenv('APP_DEBUG_LOG_PATH') or os.getenv('APP_LOG_PATH')
if configured_app_log_path:
    log_file_path = configured_app_log_path
elif os.getenv("FLASK_ENV") == "production":
    preferred_production_log = '/var/www/Backend/app_debug.log'
    production_dir = os.path.dirname(preferred_production_log)
    if os.path.isdir(production_dir):
        log_file_path = preferred_production_log
    else:
        log_file_path = os.path.join(os.getcwd(), 'app_debug.log')
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

# Discord OAuth configuration
discord_client_id = os.getenv('DISCORD_CLIENT_ID')
discord_client_secret = os.getenv('DISCORD_CLIENT_SECRET')

if not discord_client_id or not discord_client_secret:
    raise RuntimeError(
        "Discord OAuth is not configured. Set DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET "
        "in the backend environment file."
    )

# Register Discord as an OAuth provider with the necessary endpoints and scopes
discord = oauth.register(
    name='discord',  
    client_id=discord_client_id,  
    client_secret=discord_client_secret,  
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
    discord_id = db.Column(db.String(32), unique=True, nullable=True)
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
    connected_accounts = db.relationship(
        'ConnectedAccount',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )



    def __repr__(self):
        return f'<User {self.email}>'

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    def has_role(self, role_names):
        """Check if a user has any of the specified roles"""
        return any(role.name in role_names for role in self.roles)


class ConnectedAccount(db.Model):
    __tablename__ = 'connected_account'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    provider = db.Column(db.String(32), nullable=False)
    provider_account_id = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    profile_url = db.Column(db.String(500), nullable=True)
    connected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint('provider', 'provider_account_id', name='uq_connected_account_provider_account'),
        db.UniqueConstraint('user_id', 'provider', name='uq_connected_account_user_provider'),
    )

    def __repr__(self):
        return f'<ConnectedAccount {self.provider}:{self.provider_account_id}>'
# Define which ranks are allowed to manage songs
allowed_ranks_for_song_management = ['admin', 'developer', 'producer']

def check_user_rank(user, allowed_ranks):
    # Convert both the allowed list and role names to lowercase for case-insensitive comparison.
    return any(role.name.lower() in [r.lower() for r in allowed_ranks] for role in user.roles)

def get_setting(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default


def set_setting(key, value):
    setting = Setting.query.filter_by(key=key).first()
    if not setting:
        setting = Setting(key=key)
        db.session.add(setting)
    setting.value = value
    return setting


def get_user_setting_key(user_id, suffix):
    return f"user:{user_id}:{suffix}"


def get_user_setting(user_id, suffix, default=None):
    return get_setting(get_user_setting_key(user_id, suffix), default)


def set_user_setting(user_id, suffix, value):
    return set_setting(get_user_setting_key(user_id, suffix), value)


def get_user_setting_json(user_id, suffix, default=None):
    raw_value = get_user_setting(user_id, suffix)
    if not raw_value:
        return default
    try:
        return json.loads(raw_value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def set_user_setting_json(user_id, suffix, payload):
    set_user_setting(user_id, suffix, json.dumps(payload, separators=(',', ':')))


def get_role_setting_key(role_id, suffix):
    return f"role:{role_id}:{suffix}"


def get_role_setting_json(role_id, suffix, default=None):
    raw_value = get_setting(get_role_setting_key(role_id, suffix))
    if not raw_value:
        return default
    try:
        return json.loads(raw_value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def set_role_setting_json(role_id, suffix, payload):
    set_setting(get_role_setting_key(role_id, suffix), json.dumps(payload, separators=(',', ':')))


def get_role_metadata(role):
    if not role:
        return {
            "system_role": False,
            "dashboard_flavor": DEFAULT_DASHBOARD_FLAVOR,
            "permissions": [],
        }

    metadata = default_role_metadata(role.name)
    stored_metadata = get_role_setting_json(role.id, 'meta', {}) or {}

    if isinstance(stored_metadata, dict):
        if 'system_role' in stored_metadata:
            metadata['system_role'] = bool(stored_metadata.get('system_role'))
        if stored_metadata.get('dashboard_flavor'):
            metadata['dashboard_flavor'] = stored_metadata.get('dashboard_flavor')
        metadata['permissions'] = normalize_permission_keys(
            stored_metadata.get('permissions', metadata.get('permissions', []))
        )

    return metadata


def set_role_metadata(role, metadata):
    payload = {
        "system_role": bool(metadata.get('system_role', False)),
        "dashboard_flavor": metadata.get('dashboard_flavor') or DEFAULT_DASHBOARD_FLAVOR,
        "permissions": normalize_permission_keys(metadata.get('permissions', [])),
    }
    set_role_setting_json(role.id, 'meta', payload)
    return payload


def serialize_role(role):
    metadata = get_role_metadata(role)
    return {
        "id": role.id,
        "name": role.name,
        "badge_color": role.badge_color,
        "badge_icon": role.badge_icon,
        "system_role": metadata.get('system_role', False),
        "dashboard_flavor": metadata.get('dashboard_flavor', DEFAULT_DASHBOARD_FLAVOR),
        "permissions": metadata.get('permissions', []),
    }


def get_user_permissions(user):
    if not user:
        return []
    permissions = set()
    for role in user.roles:
        permissions.update(get_role_metadata(role).get('permissions', []))
    return sorted(permissions)


def user_has_permission(user, permission_key):
    return permission_key in set(get_user_permissions(user))


def user_has_any_permission(user, permission_keys):
    effective_permissions = set(get_user_permissions(user))
    return any(permission in effective_permissions for permission in permission_keys)


def get_user_dashboard_flavor(user):
    if not user:
        return DEFAULT_DASHBOARD_FLAVOR

    role_flavors = []
    for role in user.roles:
        metadata = get_role_metadata(role)
        flavor = metadata.get('dashboard_flavor') or DEFAULT_DASHBOARD_FLAVOR
        if flavor != DEFAULT_DASHBOARD_FLAVOR:
            role_flavors.append(flavor)

    if role_flavors:
        return role_flavors[0]
    return DEFAULT_DASHBOARD_FLAVOR


def serialize_permission_catalog():
    return PERMISSION_DEFINITIONS


def get_user_display_name(user):
    if not user:
        return None
    return get_user_setting(user.id, 'display_name', user.username or user.email)


def get_authenticated_user():
    current_user_id = get_jwt_identity()
    return User.query.get(int(current_user_id)) if current_user_id else None


def get_user_from_access_token(raw_token):
    if not raw_token:
        return None

    token = str(raw_token).strip()
    if token.lower().startswith('bearer '):
        token = token.split(' ', 1)[1].strip()

    try:
        payload = decode_token(token)
    except Exception:
        return None

    identity = payload.get('sub')
    if not identity:
        return None

    try:
        return User.query.get(int(identity))
    except (TypeError, ValueError):
        return None


def get_backend_base_url():
    configured = os.getenv('BACKEND_URL')
    if configured:
        return configured.rstrip('/')
    return request.host_url.rstrip('/')


def get_frontend_base_url():
    configured = os.getenv('FRONTEND_URL')
    if configured:
        return configured.rstrip('/')
    return 'http://localhost:5174'


def get_openxbl_api_key():
    return (os.getenv('OPENXBL_API_KEY') or os.getenv('XBL_IO_API_KEY') or '').strip()


def get_openxbl_app_public_key():
    return (os.getenv('OPENXBL_APP_PUBLIC_KEY') or os.getenv('XBL_IO_APP_PUBLIC_KEY') or '').strip()


def get_cito_api_key():
    return (os.getenv('CITO_API_KEY') or '').strip()


def is_openxbl_configured():
    return bool(get_openxbl_api_key())


def is_cito_configured():
    return bool(get_cito_api_key())


def openxbl_api_get(path, params=None, auth_key=None, use_contract=False):
    api_key = (auth_key or get_openxbl_api_key() or '').strip()
    if not api_key:
        raise RuntimeError('OPENXBL_API_KEY is not configured')

    headers = {
        'X-Authorization': api_key,
        'Accept': 'application/json',
        'Accept-Language': 'en-US',
    }
    if use_contract:
        headers['X-Contract'] = '100'

    response = requests.get(
        f"https://api.xbl.io/api/v2/{path.lstrip('/')}",
        params=params,
        headers=headers,
        timeout=8,
    )
    response.raise_for_status()
    return response.json()


def cito_api_get(path, params=None):
    api_key = get_cito_api_key()
    if not api_key:
        raise RuntimeError('CITO_API_KEY is not configured')

    response = requests.get(
        f"https://api.citoapi.com/api/v1/{path.lstrip('/')}",
        params=params,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
        },
        timeout=8,
    )
    response.raise_for_status()
    return response.json()


def first_non_empty(*values):
    for value in values:
        if value not in (None, '', [], {}):
            return value
    return None


def parse_int(value, default=0):
    try:
        if value in (None, ''):
            return default
        return int(str(value).replace(',', '').strip())
    except (TypeError, ValueError):
        return default


def normalize_xbox_profile(profile):
    settings = {}
    for setting in profile.get('settings', []) or []:
        values = setting.get('value')
        if isinstance(values, list):
            values = values[0] if values else None
        settings[setting.get('id')] = values

    return {
        'xuid': first_non_empty(profile.get('xuid'), profile.get('id'), profile.get('hostId')),
        'display_name': first_non_empty(
            profile.get('gamertag'),
            profile.get('modernGamertag'),
            profile.get('uniqueModernGamertag'),
            profile.get('displayName'),
            settings.get('Gamertag'),
        ),
        'gamerscore': parse_int(first_non_empty(profile.get('gamerscore'), profile.get('gamerScore'), settings.get('Gamerscore'))),
        'avatar_url': first_non_empty(
            profile.get('displayPicRaw'),
            profile.get('avatar'),
            settings.get('GameDisplayPicRaw'),
            settings.get('GameDisplayPic'),
        ),
        'presence_state': first_non_empty(profile.get('presenceState'), settings.get('PresenceState')),
        'presence_text': first_non_empty(profile.get('presenceText'), settings.get('PresenceText')),
        'bio': first_non_empty(profile.get('bio'), settings.get('Bio')),
    }


def normalize_xbox_search_results(payload):
    results = []
    for person in payload.get('people', []) or []:
        normalized = normalize_xbox_profile(person)
        if not normalized['xuid']:
            continue
        normalized['raw'] = person
        results.append(normalized)
    return results


def normalize_xbox_achievement_title(item):
    title_id = first_non_empty(
        item.get('titleId'),
        item.get('serviceConfigId'),
        item.get('productId'),
        item.get('id'),
    )
    title_name = first_non_empty(
        item.get('name'),
        item.get('titleName'),
        item.get('title'),
        item.get('productTitle'),
        item.get('serviceConfigId'),
    )
    earned = parse_int(first_non_empty(item.get('earnedAchievements'), item.get('progression'), item.get('currentAchievements')))
    total = parse_int(first_non_empty(item.get('totalAchievements'), item.get('maxAchievements')))
    gamerscore = parse_int(first_non_empty(item.get('earnedGamerscore'), item.get('currentGamerscore'), item.get('gamerscore')))
    total_gamerscore = parse_int(first_non_empty(item.get('maxGamerscore'), item.get('totalGamerscore')))
    image_url = first_non_empty(item.get('displayImage'), item.get('artwork'), item.get('image'), item.get('tileImageUrl'))
    last_unlock = first_non_empty(item.get('lastUnlock'), item.get('lastUnlockTime'), item.get('lastPlayed'))

    return {
        'id': title_id or title_name or 'xbox-title',
        'title_id': title_id,
        'title': title_name or 'Xbox-tittel',
        'code': ''.join(part[0] for part in (title_name or 'Xbox').split()[:3]).upper()[:4] or 'XB',
        'platform': 'Xbox',
        'platform_class': 'gp-x',
        'left_stat': f'{gamerscore}G' if gamerscore else (f'{earned}/{total} ach' if total else 'Xbox'),
        'right_stat': f'{earned}/{total} ach' if total else (f'{total_gamerscore}G mulig' if total_gamerscore else 'Achievement-data'),
        'gamerscore': gamerscore,
        'total_gamerscore': total_gamerscore,
        'earned_achievements': earned,
        'total_achievements': total,
        'image_url': image_url,
        'logo_url': image_url,
        'last_unlock': last_unlock,
    }


def normalize_xbox_achievement_item(item, fallback_title=None):
    name = first_non_empty(item.get('name'), item.get('achievementName'), item.get('title'))
    title_name = fallback_title or first_non_empty(item.get('titleName'), item.get('gameName'), item.get('title')) or 'Xbox'
    gamerscore = parse_int(first_non_empty(item.get('rewardsGamerscore'), item.get('gamerscore'), item.get('value')))
    unlocked = bool(first_non_empty(item.get('isUnlocked'), item.get('unlocked')))
    unlocked_at = first_non_empty(item.get('timeUnlocked'), item.get('unlockTime'), item.get('dateUnlocked'))
    media_assets = item.get('mediaAssets') or []
    icon_url = first_non_empty(
        item.get('lockedIconUrl'),
        item.get('icon'),
        media_assets[0].get('url') if media_assets else None,
    )

    parsed_timestamp = None
    if isinstance(unlocked_at, str) and unlocked_at:
        try:
            parsed_timestamp = to_utc_datetime(datetime.fromisoformat(unlocked_at.replace('Z', '+00:00')))
        except ValueError:
            parsed_timestamp = None

    return {
        'id': first_non_empty(item.get('id'), item.get('achievementId'), name, title_name),
        'title': name or 'Xbox achievement',
        'game': title_name,
        'icon': icon_url or '🏆',
        'is_img': bool(icon_url),
        'icon_class': 'aigg',
        'platform': 'Xbox',
        'platform_class': 'apx',
        'timestamp': parsed_timestamp,
        'unlocked': unlocked,
        'gamerscore': gamerscore,
    }


def fetch_current_xbox_profile(auth_key=None, use_contract=False):
    payload = openxbl_api_get('account', auth_key=auth_key, use_contract=use_contract)
    print("XBOX_DEBUG_PROFILE_RAW:", payload)
    people = payload.get('people', []) or payload.get('profileUsers', []) or []
    if people:
        return normalize_xbox_profile(people[0])
    if isinstance(payload, dict):
        normalized = normalize_xbox_profile(payload)
        if normalized.get('xuid'):
            return normalized
    return None


def fetch_xbox_profile_by_xuid(xuid, auth_key=None, use_contract=False):
    payload = openxbl_api_get(f'account/{xuid}', auth_key=auth_key, use_contract=use_contract)
    people = payload.get('people', []) or payload.get('profileUsers', []) or []
    if people:
        return normalize_xbox_profile(people[0])
    return None


def fetch_xbox_presence(xuid, auth_key=None, use_contract=False):
    payload = openxbl_api_get(f'{xuid}/presence', auth_key=auth_key, use_contract=use_contract)
    presence_root = payload.get('presence') or payload.get('people') or payload
    if isinstance(presence_root, list) and presence_root:
        return presence_root[0]
    return presence_root if isinstance(presence_root, dict) else {}


def fetch_xbox_title_achievements(xuid, auth_key=None, use_contract=False):
    payload = openxbl_api_get(f'achievements/player/{xuid}', auth_key=auth_key, use_contract=use_contract)
    titles = payload.get('titles') or payload.get('achievements') or payload.get('results') or []
    return [normalize_xbox_achievement_title(item) for item in titles if isinstance(item, dict)]


def fetch_xbox_achievement_details(xuid, title_id, fallback_title=None, auth_key=None, use_contract=False):
    payload = openxbl_api_get(f'achievements/player/{xuid}/{title_id}', auth_key=auth_key, use_contract=use_contract)
    achievements = payload.get('achievements') or payload.get('items') or payload.get('results') or []
    return [
        normalize_xbox_achievement_item(item, fallback_title=fallback_title)
        for item in achievements
        if isinstance(item, dict)
    ]


def claim_openxbl_app_code(code):
    app_public_key = get_openxbl_app_public_key()
    if not app_public_key:
        raise RuntimeError('OPENXBL_APP_PUBLIC_KEY is not configured')

    response = requests.post(
        'https://api.xbl.io/app/claim',
        json={
            'code': code,
            'app_key': app_public_key,
        },
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        timeout=8,
    )
    response.raise_for_status()

    payload = response.json() if response.content else {}
    claimed_key = first_non_empty(
        payload.get('key'),
        payload.get('app_key'),
        payload.get('appKey'),
        payload.get('secret'),
        payload.get('token'),
        payload.get('authorization'),
        payload.get('authorization_key'),
    )
    if not claimed_key and len(payload) == 1:
        only_value = next(iter(payload.values()))
        if isinstance(only_value, str) and only_value.strip():
            claimed_key = only_value.strip()

    if not claimed_key:
        raise ValueError('OpenXBL claim response did not contain an app key')

    return claimed_key, payload


def build_xbox_summary(account):
    if not account:
        return {
            'connected': False,
            'configured': is_openxbl_configured(),
            'provider': 'xbox',
            'message': 'Xbox er ikke tilkoblet.',
            'current_game': None,
            'recent_games': [],
            'all_games': [],
            'totals': {
                'gamerscore': 0,
                'owned_games': 0,
                'recent_games': 0,
                'achievements_unlocked': 0,
            },
        }

    auth_key = (account.access_token or '').strip() or get_openxbl_api_key()
    use_contract = bool((account.access_token or '').strip())

    if not auth_key:
        return {
            'connected': True,
            'configured': False,
            'provider': 'xbox',
            'message': 'Xbox er koblet til, men OpenXBL-nøkkel mangler i backend-env eller kontodata.',
            'current_game': None,
            'recent_games': [],
            'all_games': [],
            'totals': {
                'gamerscore': 0,
                'owned_games': 0,
                'recent_games': 0,
                'achievements_unlocked': 0,
            },
        }

    profile = (
        fetch_xbox_profile_by_xuid(account.provider_account_id, auth_key=auth_key, use_contract=use_contract)
        or fetch_current_xbox_profile(auth_key=auth_key, use_contract=use_contract)
        or {}
    )
    presence = fetch_xbox_presence(account.provider_account_id, auth_key=auth_key, use_contract=use_contract) or {}
    titles = fetch_xbox_title_achievements(account.provider_account_id, auth_key=auth_key, use_contract=use_contract)

    recent_games = titles[:3]
    all_games = titles[:6]
    current_game_name = first_non_empty(
        presence.get('presenceText'),
        profile.get('presence_text'),
        recent_games[0]['title'] if recent_games else None,
    )
    current_game = None
    if current_game_name:
        current_game = {
            'title': current_game_name,
            'subtitle': 'Xbox Live',
            'provider': 'Xbox',
        }

    return {
        'connected': True,
        'configured': True,
        'provider': 'xbox',
        'message': None,
        'current_game': current_game,
        'recent_games': recent_games,
        'all_games': all_games,
        'totals': {
            'gamerscore': profile.get('gamerscore', 0),
            'owned_games': len(titles),
            'recent_games': len(recent_games),
            'achievements_unlocked': sum(item.get('earned_achievements', 0) for item in titles),
        },
    }


def get_xbox_oauth_config():
    client_id = (os.getenv('MICROSOFT_CLIENT_ID') or '').strip()
    client_secret = (os.getenv('MICROSOFT_CLIENT_SECRET') or '').strip()
    tenant_id = (os.getenv('MICROSOFT_TENANT_ID') or 'common').strip() or 'common'

    if not client_id or not client_secret:
        return None

    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'tenant_id': tenant_id,
        'authorize_url': f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize',
        'token_url': f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
        'scope': 'openid profile email offline_access User.Read',
    }


def fetch_microsoft_profile(access_token):
    profile_response = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        },
        timeout=8,
    )
    profile_response.raise_for_status()
    profile = profile_response.json()

    avatar_url = None
    try:
        avatar_response = requests.get(
            'https://graph.microsoft.com/v1.0/me/photos/48x48/$value',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=8,
        )
        if avatar_response.ok:
            avatar_url = 'https://graph.microsoft.com/v1.0/me/photos/48x48/$value'
    except requests.RequestException:
        avatar_url = None

    return {
        'account_id': profile.get('id'),
        'display_name': profile.get('displayName') or profile.get('userPrincipalName') or profile.get('mail'),
        'email': profile.get('mail') or profile.get('userPrincipalName'),
        'avatar_url': avatar_url,
        'profile_url': 'https://account.microsoft.com/',
    }


def build_connection_payload(user):
    connected_accounts = {account.provider.lower(): account for account in user.connected_accounts}
    discord_suffix = str(user.discord_id)[-4:] if user.discord_id else 'link'
    steam_account = connected_accounts.get('steam')
    xbox_account = connected_accounts.get('xbox')
    battlenet_account = connected_accounts.get('battlenet')

    return {
        "connections": [
            {
                "provider": "steam",
                "connected": steam_account is not None,
                "displayName": steam_account.display_name if steam_account else None,
                "subtitle": "Steam-konto tilkoblet" if steam_account else "Ikke tilkoblet",
                "avatarUrl": steam_account.avatar_url if steam_account else None,
                "avatarText": "S",
                "providerAccountId": steam_account.provider_account_id if steam_account else None,
                "canDisconnect": steam_account is not None,
            },
            {
                "provider": "xbox",
                "connected": xbox_account is not None,
                "displayName": xbox_account.display_name if xbox_account else None,
                "subtitle": "Xbox-konto tilkoblet" if xbox_account else "Ikke tilkoblet",
                "avatarUrl": xbox_account.avatar_url if xbox_account else None,
                "avatarText": "X",
                "providerAccountId": xbox_account.provider_account_id if xbox_account else None,
                "canDisconnect": xbox_account is not None,
            },
            {
                "provider": "battlenet",
                "connected": battlenet_account is not None,
                "displayName": battlenet_account.display_name if battlenet_account else None,
                "subtitle": "Ikke tilkoblet",
                "avatarUrl": battlenet_account.avatar_url if battlenet_account else None,
                "avatarText": "B",
                "providerAccountId": battlenet_account.provider_account_id if battlenet_account else None,
                "canDisconnect": battlenet_account is not None,
            },
            {
                "provider": "discord",
                "connected": bool(user.discord_id),
                "displayName": user.username or user.email,
                "subtitle": f"Discord · {discord_suffix}" if user.discord_id else "Primær innlogging mangler",
                "avatarUrl": user.avatar,
                "avatarText": "D",
                "providerAccountId": user.discord_id,
                "canDisconnect": False,
            }
        ]
    }


def build_connection_payload(user):
    connected_accounts = {account.provider.lower(): account for account in user.connected_accounts}
    discord_suffix = str(user.discord_id)[-4:] if user.discord_id else 'link'
    steam_account = connected_accounts.get('steam')
    xbox_account = connected_accounts.get('xbox')
    battlenet_account = connected_accounts.get('battlenet')
    cod_account = connected_accounts.get('cod')
    epic_account = connected_accounts.get('epic')

    return {
        "connections": [
            {
                "provider": "steam",
                "connected": steam_account is not None,
                "displayName": steam_account.display_name if steam_account else None,
                "subtitle": "Steam-konto tilkoblet" if steam_account else "Ikke tilkoblet",
                "avatarUrl": steam_account.avatar_url if steam_account else None,
                "avatarText": "S",
                "providerAccountId": steam_account.provider_account_id if steam_account else None,
                "canDisconnect": steam_account is not None,
            },
            {
                "provider": "xbox",
                "connected": xbox_account is not None,
                "displayName": xbox_account.display_name if xbox_account else None,
                "subtitle": "Xbox-konto tilkoblet" if xbox_account else "Ikke tilkoblet",
                "avatarUrl": xbox_account.avatar_url if xbox_account else None,
                "avatarText": "X",
                "providerAccountId": xbox_account.provider_account_id if xbox_account else None,
                "canDisconnect": xbox_account is not None,
            },
            {
                "provider": "battlenet",
                "connected": battlenet_account is not None,
                "displayName": battlenet_account.display_name if battlenet_account else None,
                "subtitle": "Battle.net-konto tilkoblet" if battlenet_account else "Ikke tilkoblet",
                "avatarUrl": battlenet_account.avatar_url if battlenet_account else None,
                "avatarText": "B",
                "providerAccountId": battlenet_account.provider_account_id if battlenet_account else None,
                "canDisconnect": battlenet_account is not None,
            },
            {
                "provider": "discord",
                "connected": bool(user.discord_id),
                "displayName": get_user_display_name(user),
                "subtitle": f"Discord · {discord_suffix}" if user.discord_id else "Primær innlogging mangler",
                "avatarUrl": user.avatar,
                "avatarText": "D",
                "providerAccountId": user.discord_id,
                "canDisconnect": False,
            },
            {
                "provider": "cod",
                "connected": cod_account is not None,
                "displayName": cod_account.display_name if cod_account else None,
                "subtitle": "CoD-esportsprofil koblet" if cod_account else "Ikke koblet",
                "avatarUrl": cod_account.avatar_url if cod_account else None,
                "avatarText": "C",
                "providerAccountId": cod_account.provider_account_id if cod_account else None,
                "canDisconnect": cod_account is not None,
            },
            {
                "provider": "epic",
                "connected": epic_account is not None,
                "displayName": epic_account.display_name if epic_account else None,
                "subtitle": "Epic Games-profil koblet" if epic_account else "Ikke koblet",
                "avatarUrl": epic_account.avatar_url if epic_account else None,
                "avatarText": "E",
                "providerAccountId": epic_account.provider_account_id if epic_account else None,
                "canDisconnect": epic_account is not None,
            },
        ]
    }


def serialize_authenticated_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "discord_id": user.discord_id,
        "username": user.username,
        "display_name": get_user_display_name(user),
        "bio": user.bio,
        "avatar": user.avatar,
        "banner": user.banner,
        "roles": [serialize_role(role) for role in user.roles],
        "permissions": get_user_permissions(user),
        "dashboard_flavor": get_user_dashboard_flavor(user),
    }


def fetch_steam_profile(steam_id):
    steam_api_key = os.getenv('STEAM_WEB_API_KEY')
    profile = {
        "display_name": f"Steam {steam_id[-4:]}",
        "avatar_url": None,
        "profile_url": f"https://steamcommunity.com/profiles/{steam_id}",
    }

    if not steam_api_key:
        return profile

    response = requests.get(
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
        params={'key': steam_api_key, 'steamids': steam_id},
        timeout=8
    )
    response.raise_for_status()
    players = response.json().get('response', {}).get('players', [])
    if not players:
        return profile

    player = players[0]
    return {
        "display_name": player.get('personaname') or profile["display_name"],
        "avatar_url": player.get('avatarfull') or player.get('avatarmedium') or player.get('avatar'),
        "profile_url": player.get('profileurl') or profile["profile_url"],
    }


def steam_api_get(interface, method, version, params):
    steam_api_key = os.getenv('STEAM_WEB_API_KEY')
    if not steam_api_key:
        return None

    response = requests.get(
        f'https://api.steampowered.com/{interface}/{method}/{version}/',
        params={'key': steam_api_key, **params},
        timeout=8
    )
    response.raise_for_status()
    return response.json()


def get_display_name(user):
    if not user:
        return 'Ukjent'
    if user.username:
        return user.username
    if user.email:
        return user.email.split('@')[0]
    return f'Bruker {user.id}'


def minutes_to_hours(minutes):
    hours = round((minutes or 0) / 60, 2)
    if float(hours).is_integer():
        return int(hours)
    return hours


def build_user_color(user):
    palette = [
        'linear-gradient(135deg,#c8102e,#7a0e1e)',
        'linear-gradient(135deg,#1a4a7a,#0a2a5a)',
        'linear-gradient(135deg,#1a6a3a,#0a3a1a)',
        'linear-gradient(135deg,#4a1a7a,#2a0a5a)',
        'linear-gradient(135deg,#5a5a1a,#3a3a0a)',
        'linear-gradient(135deg,#1a3a5a,#0a1a3a)',
    ]
    if not user:
        return palette[0]
    return palette[user.id % len(palette)]


def to_utc_datetime(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def format_time_ago(value):
    dt = to_utc_datetime(value)
    if not dt:
        return ''
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = max(int(diff.total_seconds()), 0)
    if seconds < 60:
        return 'nettopp'
    if seconds < 3600:
        minutes = seconds // 60
        return f'{minutes} min siden'
    if seconds < 86400:
        hours = seconds // 3600
        return f'{hours}t siden'
    if seconds < 604800:
        days = seconds // 86400
        return f'{days}d siden'
    return dt.strftime('%d.%m.%Y')


def build_steam_game_payload(game):
    app_id = game.get('appid')
    name = game.get('name') or f"App {app_id}"
    logo_hash = game.get('img_logo_url')
    return {
        "id": app_id,
        "title": name,
        "code": ''.join(part[0] for part in name.split()[:3]).upper()[:4] or 'GM',
        "platform": "Steam",
        "platform_class": "gp-s",
        "left_stat": f"{minutes_to_hours(game.get('playtime_forever', 0))}t totalt",
        "right_stat": f"{minutes_to_hours(game.get('playtime_2weeks', 0))}t siste 2 uker",
        "playtime_forever_minutes": game.get('playtime_forever', 0),
        "playtime_2weeks_minutes": game.get('playtime_2weeks', 0),
        "app_id": app_id,
        "image_url": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg" if app_id else None,
        "logo_url": (
            f"https://media.steampowered.com/steamcommunity/public/images/apps/{app_id}/{logo_hash}.jpg"
            if app_id and logo_hash else None
        ),
    }


def fetch_steam_presence(account):
    if not account or not account.provider_account_id or not os.getenv('STEAM_WEB_API_KEY'):
        return None

    steam_id = account.provider_account_id
    player_summary = steam_api_get(
        'ISteamUser',
        'GetPlayerSummaries',
        'v0002',
        {'steamids': steam_id}
    )
    recent_games_response = steam_api_get(
        'IPlayerService',
        'GetRecentlyPlayedGames',
        'v0001',
        {'steamid': steam_id, 'count': 3}
    )

    player = (player_summary or {}).get('response', {}).get('players', [{}])[0]
    recent_games = (recent_games_response or {}).get('response', {}).get('games', []) or []
    recent_payload = [build_steam_game_payload(game) for game in recent_games]
    recent_primary = recent_payload[0] if recent_payload else None
    is_playing = bool(player.get('gameextrainfo'))

    return {
        'steam_id': steam_id,
        'player': player,
        'recent_games': recent_games,
        'recent_payload': recent_payload,
        'current_game_name': player.get('gameextrainfo'),
        'current_game': recent_primary if is_playing and recent_primary else None,
        'last_game': recent_primary,
        'is_playing': is_playing,
        'last_seen': format_time_ago(
            datetime.fromtimestamp(player.get('lastlogoff', 0), tz=timezone.utc)
        ) if player.get('lastlogoff') else '',
    }


def _legacy_fetch_latest_steam_achievement_event(account, presence=None):
    if not account or not account.provider_account_id or not os.getenv('STEAM_WEB_API_KEY'):
        return None

    presence = presence or fetch_steam_presence(account)
    if not presence:
        return None

    recent_games = presence.get('recent_games', [])
    for game in recent_games[:2]:
        app_id = game.get('appid')
        if not app_id:
            continue
        try:
            achievement_response = steam_api_get(
                'ISteamUserStats',
                'GetPlayerAchievements',
                'v0001',
                {'steamid': account.provider_account_id, 'appid': app_id, 'l': 'english'}
            )
        except requests.RequestException:
            continue

        achievements = (achievement_response or {}).get('playerstats', {}).get('achievements', []) or []
        unlocked = [
            achievement for achievement in achievements
            if achievement.get('achieved') == 1 and achievement.get('unlocktime')
        ]
        if not unlocked:
            continue

        latest = max(unlocked, key=lambda item: item.get('unlocktime', 0))
        unlocked_at = datetime.fromtimestamp(latest['unlocktime'], tz=timezone.utc)
        return {
            'timestamp': unlocked_at,
            'kind': 'game_achievement',
            'provider': 'steam',
            'providerLabel': 'Steam',
            'actor_name': get_display_name(account.user),
            'actor_avatar_url': account.user.avatar,
            'actor_color': build_user_color(account.user),
            'text': (
                f"<strong>{get_display_name(account.user)}</strong> låste opp achievement "
                f"<em>{latest.get('name') or latest.get('apiname') or 'Ukjent achievement'}</em>"
            ),
            'game': game.get('name'),
            'time': format_time_ago(unlocked_at),
            'thumb': build_steam_game_payload(game),
        }
    return None


def fetch_latest_steam_achievement_event(account, presence=None):
    if not account or not account.provider_account_id or not os.getenv('STEAM_WEB_API_KEY'):
        return None

    presence = presence or fetch_steam_presence(account)
    if not presence:
        return None

    latest_match = select_latest_recent_steam_achievement(
        presence.get('recent_games', []),
        account.provider_account_id,
        steam_api_get,
    )
    if not latest_match:
        return None

    game = latest_match['game']
    latest = latest_match['achievement']
    unlocked_at = datetime.fromtimestamp(latest['unlocktime'], tz=timezone.utc)
    return {
        'timestamp': unlocked_at,
        'kind': 'game_achievement',
        'provider': 'steam',
        'providerLabel': 'Steam',
        'actor_name': get_display_name(account.user),
        'actor_avatar_url': account.user.avatar,
        'actor_color': build_user_color(account.user),
        'text': (
            f"<strong>{get_display_name(account.user)}</strong> lÃ¥ste opp achievement "
            f"<em>{latest.get('name') or latest.get('apiname') or 'Ukjent achievement'}</em>"
        ),
        'game': game.get('name'),
        'time': format_time_ago(unlocked_at),
        'thumb': build_steam_game_payload(game),
    }


def can_manage_music(user):
    return user_has_permission(user, 'manage_music')


def can_manage_bedriftsmeldinger(user):
    return user_has_any_permission(user, [
        'publish_bedriftsmeldinger',
        'edit_bedriftsmeldinger',
        'delete_bedriftsmeldinger',
    ])


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




if os.getenv('FLASK_ENV') == 'production':
    backend_url = (os.getenv('BACKEND_URL') or '').lower()

    # Only pin the session cookie to the custom domain when the backend is
    # actually served from that domain. Render callback traffic on *.onrender.com
    # needs a host-only cookie or OAuth state validation will fail.
    if 'hmnmentalpasienter.no' in backend_url:
        app.config.update(
            SESSION_COOKIE_DOMAIN='.hmnmentalpasienter.no',
            SESSION_COOKIE_SAMESITE='None',
            SESSION_COOKIE_SECURE=True
        )
    else:
        app.config.update(
            SESSION_COOKIE_DOMAIN=None,
            # Steam linking starts via cross-site XHR from the frontend domain to
            # the Render backend, so the session cookie must be allowed in a
            # cross-site context while remaining host-only on *.onrender.com.
            SESSION_COOKIE_SAMESITE='None',
            SESSION_COOKIE_SECURE=True
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


class Bedriftsmelding(db.Model):
    __tablename__ = 'bedriftsmeldinger'
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='oppdatering')
    tag = db.Column(db.String(50), nullable=True)
    pinned = db.Column(db.Boolean, default=False, nullable=False)
    notify_users = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('bedriftsmeldinger', lazy=True))



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
@app.route('/api/login/discord')
def login_discord():
    redirect_uri = url_for('authorize_discord', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route('/authorize/discord')
@app.route('/api/authorize/discord')
def authorize_discord():
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173').rstrip('/')

    try:
        # Exchange the authorization code for an access token from Discord.
        discord.authorize_access_token()

        # Fetch the user's profile from Discord without extra headers (omit the leading slash)
        resp = discord.get('users/@me')
        profile = resp.json()
    except Exception as e:
        print("Discord OAuth error:", e)
        return redirect(f"{frontend_url}/login?error=discord_oauth_failed")

    if not isinstance(profile, dict) or profile.get('id') is None:
        print("Unexpected Discord profile payload:", profile)
        return redirect(f"{frontend_url}/login?error=discord_profile_failed")

    session['discord_user'] = profile
    discord_id = str(profile.get('id'))
    discord_email = profile.get('email')

    if not discord_email:
        return redirect(f"{frontend_url}/login?error=discord_email_missing")

    # Resolve user by Discord identity first, then fall back to email for one-time linking.
    user = User.query.filter_by(discord_id=discord_id).first()
    if not user:
        user = User.query.filter_by(email=discord_email).first()
        if user:
            conflict = User.query.filter(User.discord_id == discord_id, User.id != user.id).first()
            if conflict:
                return redirect(f"{frontend_url}/login?error=discord_already_linked")
            user.discord_id = discord_id

    if not user:
        username_base = profile.get('global_name') or profile.get('username') or f"discord_{profile.get('id')}"
        username_candidate = username_base
        suffix = 1
        while User.query.filter_by(username=username_candidate).first():
            username_candidate = f"{username_base}_{suffix}"
            suffix += 1

        user = User(
            email=discord_email,
            discord_id=discord_id,
            username=username_candidate,
            password_hash=bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()
    else:
        desired_username = profile.get('global_name') or profile.get('username')
        if desired_username and user.username != desired_username:
            if not User.query.filter(User.username == desired_username, User.id != user.id).first():
                user.username = desired_username
        if user.discord_id != discord_id:
            user.discord_id = discord_id
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    session['jwt_token'] = access_token

    # Redirect to the frontend with the token as a query parameter.
    return redirect(f"{frontend_url}/login?token={access_token}")

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = get_authenticated_user()
    if not user:
         return jsonify({"msg": "User not found"}), 404
    return jsonify({"user": serialize_authenticated_user(user)}), 200


@app.route('/api/connections', methods=['GET'])
@jwt_required()
def get_connections():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(build_connection_payload(user)), 200


@app.route('/api/connections/<provider>', methods=['DELETE'])
@jwt_required()
def delete_connection(provider):
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    normalized_provider = (provider or '').lower()
    if normalized_provider == 'discord':
        return jsonify({"error": "Discord er primær innlogging og kan ikke kobles fra her."}), 400

    account = ConnectedAccount.query.filter_by(
        user_id=user.id,
        provider=normalized_provider
    ).first()

    if not account:
        return jsonify({"error": "Kontoen er ikke tilkoblet."}), 404

    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": f"{normalized_provider} koblet fra."}), 200


USERNAME_PATTERN = re.compile(r'^[A-Za-z0-9_]{3,30}$')

DEFAULT_ALERT_PREFERENCES = {
    "bedriftsmeldinger": True,
    "hendelser": True,
    "achievements": True,
    "venner": False,
    "thomas": True,
}

DEFAULT_PRIVACY_PREFERENCES = {
    "public_profile": True,
    "show_activity": True,
    "show_in_leaderboard": True,
}


def validate_settings_username(candidate_username, current_user_id=None):
    normalized_username = (candidate_username or '').strip()
    if not normalized_username:
        return False, "Brukernavn kan ikke være tomt.", None
    if not USERNAME_PATTERN.fullmatch(normalized_username):
        return False, "Brukernavn må være 3-30 tegn og kan bare bruke bokstaver, tall og underscore.", None

    existing_user = User.query.filter_by(username=normalized_username).first()
    if existing_user and existing_user.id != current_user_id:
        return False, "Brukernavnet er allerede i bruk.", None

    return True, None, normalized_username


def get_or_create_connected_account(user_id, provider):
    account = ConnectedAccount.query.filter_by(user_id=user_id, provider=provider).first()
    if not account:
        account = ConnectedAccount(user_id=user_id, provider=provider, provider_account_id='')
        db.session.add(account)
    return account


@app.route('/api/settings/username-availability', methods=['GET'])
@jwt_required()
def check_settings_username_availability():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    candidate_username = request.args.get('username', '')
    normalized_username = candidate_username.strip()
    if not normalized_username:
        return jsonify({
            "available": False,
            "state": "empty",
            "message": "Skriv inn et brukernavn først."
        }), 200

    if normalized_username == (user.username or ''):
        return jsonify({
            "available": True,
            "state": "unchanged",
            "message": "Dette er ditt nåværende brukernavn."
        }), 200

    is_valid, error_message, sanitized_username = validate_settings_username(
        normalized_username,
        current_user_id=user.id
    )
    if not is_valid:
        return jsonify({
            "available": False,
            "state": "invalid",
            "message": error_message
        }), 200

    return jsonify({
        "available": True,
        "state": "available",
        "message": "Brukernavnet er ledig.",
        "username": sanitized_username
    }), 200


@app.route('/api/settings/account', methods=['POST'])
@jwt_required()
def update_settings_account():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json() or {}
    requested_email = (payload.get('email') or '').strip()
    current_password = payload.get('current_password') or ''
    new_password = payload.get('new_password') or ''

    wants_email_change = bool(requested_email) and requested_email != user.email
    wants_password_change = bool(new_password)

    if not wants_email_change and not wants_password_change:
        return jsonify({"msg": "Ingen kontoendringer å lagre."}), 400

    if not current_password or not user.check_password(current_password):
        return jsonify({"msg": "Nåværende passord er feil."}), 400

    if wants_email_change:
        existing_email_owner = User.query.filter(User.email == requested_email, User.id != user.id).first()
        if existing_email_owner:
            return jsonify({"msg": "E-postadressen er allerede i bruk."}), 400
        user.email = requested_email

    if wants_password_change:
        if len(new_password) < 8:
            return jsonify({"msg": "Nytt passord må være minst 8 tegn."}), 400
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    db.session.commit()

    return jsonify({
        "msg": "Konto oppdatert.",
        "user": serialize_authenticated_user(user)
    }), 200


@app.route('/api/settings/notifications', methods=['GET'])
@jwt_required()
def get_settings_notifications():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    alert_preferences = get_user_setting_json(
        user.id,
        'alert_preferences',
        DEFAULT_ALERT_PREFERENCES.copy()
    ) or DEFAULT_ALERT_PREFERENCES.copy()

    return jsonify({"alert_preferences": alert_preferences}), 200


@app.route('/api/settings/notifications', methods=['POST'])
@jwt_required()
def save_settings_notifications():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json() or {}
    alert_preferences = {
        key: bool(payload.get(key, default_value))
        for key, default_value in DEFAULT_ALERT_PREFERENCES.items()
    }
    set_user_setting_json(user.id, 'alert_preferences', alert_preferences)
    db.session.commit()

    return jsonify({
        "msg": "Varslingsinnstillinger lagret.",
        "alert_preferences": alert_preferences
    }), 200


@app.route('/api/settings/privacy', methods=['GET'])
@jwt_required()
def get_settings_privacy():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    privacy_preferences = get_user_setting_json(
        user.id,
        'privacy_preferences',
        DEFAULT_PRIVACY_PREFERENCES.copy()
    ) or DEFAULT_PRIVACY_PREFERENCES.copy()

    return jsonify({"privacy_preferences": privacy_preferences}), 200


@app.route('/api/settings/privacy', methods=['POST'])
@jwt_required()
def save_settings_privacy():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json() or {}
    privacy_preferences = {
        key: bool(payload.get(key, default_value))
        for key, default_value in DEFAULT_PRIVACY_PREFERENCES.items()
    }
    set_user_setting_json(user.id, 'privacy_preferences', privacy_preferences)
    db.session.commit()

    return jsonify({
        "msg": "Personverninnstillinger lagret.",
        "privacy_preferences": privacy_preferences
    }), 200


@app.route('/api/settings/connections/cod/search', methods=['GET'])
@jwt_required()
def search_cod_connection_profiles():
    query = (request.args.get('q') or '').strip()
    if len(query) < 2:
        return jsonify({"results": []}), 200

    try:
        search_payload = cito_api_get('cod/search', params={'q': query})
    except RuntimeError as exc:
        return jsonify({"msg": str(exc)}), 503
    except requests.RequestException:
        return jsonify({"msg": "Kunne ikke hente CoD-profiler akkurat nå."}), 502

    player_results = ((search_payload or {}).get('results') or {}).get('players') or []
    normalized_results = []

    for player in player_results[:8]:
        current_team = player.get('currentTeam') or {}
        subtitle_parts = [
            current_team.get('name'),
            first_non_empty(player.get('country'), player.get('region'))
        ]
        subtitle = " · ".join(part for part in subtitle_parts if part)

        normalized_results.append({
            "provider_account_id": player.get('codPlayerId') or player.get('ign'),
            "codPlayerId": player.get('codPlayerId'),
            "display_name": player.get('ign') or player.get('realName') or 'Ukjent spiller',
            "real_name": player.get('realName'),
            "avatar_url": player.get('imageUrl'),
            "subtitle": subtitle,
            "country": player.get('country'),
            "region": player.get('region'),
            "team_name": current_team.get('name'),
            "total_earnings": player.get('totalEarnings'),
            "tournament_count": player.get('tournamentCount'),
        })

    return jsonify({"results": normalized_results}), 200


@app.route('/api/settings/connections/cod', methods=['POST'])
@jwt_required()
def save_cod_connection():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json() or {}
    provider_account_id = (
        payload.get('provider_account_id')
        or payload.get('codPlayerId')
        or ''
    ).strip()
    display_name = (payload.get('display_name') or payload.get('displayName') or '').strip()
    avatar_url = (payload.get('avatar_url') or payload.get('avatarUrl') or '').strip() or None
    subtitle = (payload.get('subtitle') or '').strip() or None

    if not provider_account_id:
        return jsonify({"msg": "Manglende CoD-profil."}), 400

    existing_owner = ConnectedAccount.query.filter_by(
        provider='cod',
        provider_account_id=provider_account_id
    ).first()
    if existing_owner and existing_owner.user_id != user.id:
        return jsonify({"msg": "Denne CoD-profilen er allerede koblet til en annen bruker."}), 409

    cod_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='cod').first()
    if not cod_account:
        cod_account = ConnectedAccount(
            user_id=user.id,
            provider='cod',
            provider_account_id=provider_account_id
        )
        db.session.add(cod_account)

    cod_account.provider_account_id = provider_account_id
    cod_account.display_name = display_name or provider_account_id
    cod_account.avatar_url = avatar_url
    cod_account.profile_url = subtitle
    cod_account.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "msg": "CoD-profil koblet til.",
        "connections": build_connection_payload(user)["connections"]
    }), 200


@app.route('/api/settings/connections/cod', methods=['DELETE'])
@jwt_required()
def delete_cod_connection():
    return delete_connection('cod')


@app.route('/api/settings/connections/epic', methods=['POST'])
@jwt_required()
def save_epic_connection():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json() or {}
    epic_username = (payload.get('provider_account_id') or payload.get('username') or '').strip()
    if not epic_username:
        return jsonify({"msg": "Epic-brukernavn mangler."}), 400

    existing_owner = ConnectedAccount.query.filter_by(
        provider='epic',
        provider_account_id=epic_username
    ).first()
    if existing_owner and existing_owner.user_id != user.id:
        return jsonify({"msg": "Denne Epic-profilen er allerede koblet til en annen bruker."}), 409

    epic_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='epic').first()
    if not epic_account:
        epic_account = ConnectedAccount(
            user_id=user.id,
            provider='epic',
            provider_account_id=epic_username
        )
        db.session.add(epic_account)

    epic_account.provider_account_id = epic_username
    epic_account.display_name = epic_username
    epic_account.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        "msg": "Epic-profil koblet til.",
        "connections": build_connection_payload(user)["connections"]
    }), 200


@app.route('/api/settings/connections/epic', methods=['DELETE'])
@jwt_required()
def delete_epic_connection():
    return delete_connection('epic')


@app.route('/api/settings/sessions/revoke-all', methods=['POST'])
@jwt_required()
def revoke_all_sessions():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    revoke_timestamp = datetime.now(timezone.utc).isoformat()
    set_user_setting(user.id, 'session_revoked_after', revoke_timestamp)
    db.session.commit()

    return jsonify({
        "msg": "Alle aktive sesjoner er logget ut.",
        "danger_zone_result": {"revoked_after": revoke_timestamp}
    }), 200


@app.route('/api/settings/account', methods=['DELETE'])
@jwt_required()
def delete_settings_account():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    payload = request.get_json(silent=True) or {}
    current_password = payload.get('current_password') or ''
    if not current_password or not user.check_password(current_password):
        return jsonify({"msg": "Nåværende passord er feil."}), 400

    FriendRequest.query.filter(
        (FriendRequest.sender_id == user.id) | (FriendRequest.receiver_id == user.id)
    ).delete(synchronize_session=False)
    Notification.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Activity.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    UserShopItem.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    UserAchievement.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    News.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Bedriftsmelding.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Thread.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Comment.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    ConnectedAccount.query.filter_by(user_id=user.id).delete(synchronize_session=False)

    db.session.execute(user_roles.delete().where(user_roles.c.user_id == user.id))

    for setting_suffix in (
        'display_name',
        'alert_preferences',
        'privacy_preferences',
        'session_revoked_after',
    ):
        Setting.query.filter_by(key=get_user_setting_key(user.id, setting_suffix)).delete(synchronize_session=False)

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "msg": "Konto slettet.",
        "danger_zone_result": {"deleted": True}
    }), 200


@app.route('/api/connections/steam/start', methods=['GET'])
@jwt_required(optional=True)  # CHANGED THIS - allows JWT context without requiring it
def start_steam_connection():
    user = get_authenticated_user()
    if not user:
        query_token = request.args.get('access_token')  # CHANGED THIS - browser passes token via query param
        user = get_user_from_access_token(query_token)

    if not user:
        return jsonify({"msg": "User not found"}), 401

    backend_base = get_backend_base_url()

    # CHANGED THIS - use a signed JWT state token instead of session (survives cross-origin redirects)
    state_token = create_access_token(
        identity=str(user.id),
        additional_claims={"purpose": "steam_link"},
        expires_delta=timedelta(minutes=10)
    )

    return_to = f"{backend_base}/api/connections/steam/callback?state={state_token}"
    steam_url = (
        "https://steamcommunity.com/openid/login"
        f"?openid.ns=http://specs.openid.net/auth/2.0"
        f"&openid.mode=checkid_setup"
        f"&openid.return_to={requests.utils.quote(return_to, safe='')}"
        f"&openid.realm={requests.utils.quote(backend_base, safe='')}"
        f"&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
        f"&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
    )

    return redirect(steam_url)  # CHANGED THIS - redirect browser directly instead of returning JSON


@app.route('/api/connections/xbox/start', methods=['GET'])
@jwt_required(optional=True)
def start_xbox_connection():
    user = get_authenticated_user()
    if not user:
        query_token = request.args.get('access_token')
        user = get_user_from_access_token(query_token)

    if not user:
        return jsonify({"msg": "User not found"}), 401

    app_public_key = get_openxbl_app_public_key()
    print("XBOX_DEBUG_PUBLIC_KEY:", repr(app_public_key))
    if not app_public_key:
        return redirect(f"{get_frontend_base_url()}/dashboard?connection_error=xbox_not_configured")

    session['xbox_link_user_id'] = int(user.id)
    session['xbox_link_started_at'] = datetime.now(timezone.utc).isoformat()
    session.modified = True

    return redirect(f"https://api.xbl.io/app/auth/{requests.utils.quote(app_public_key, safe='')}")


@app.route('/api/connections/steam/callback', methods=['GET'])
def steam_connection_callback():
    frontend_url = get_frontend_base_url()

    # CHANGED THIS - decode signed state token instead of reading from session
    state_token = request.args.get('state')
    if not state_token:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_state_invalid")

    try:
        state_payload = decode_token(state_token)
    except Exception:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_state_invalid")

    if state_payload.get('purpose') != 'steam_link':
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_state_invalid")

    session_user_id = state_payload.get('sub')  # CHANGED THIS - user ID from signed token
    if not session_user_id:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_state_invalid")

    verification_payload = {key: value for key, value in request.args.items() if key.startswith('openid.')}
    verification_payload['openid.mode'] = 'check_authentication'

    try:
        verification_response = requests.post(
            'https://steamcommunity.com/openid/login',
            data=verification_payload,
            timeout=8
        )
        verification_response.raise_for_status()
    except requests.RequestException:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_verify_failed")

    if 'is_valid:true' not in verification_response.text:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_invalid")

    claimed_id = request.args.get('openid.claimed_id', '')
    steam_id_match = re.search(r'/id/(\d+)$', claimed_id) or re.search(r'/profiles/(\d+)$', claimed_id)
    if not steam_id_match:
        steam_id_match = re.search(r'/openid/id/(\d+)$', claimed_id)
    if not steam_id_match:
        steam_id_match = re.search(r'(\d{17})', claimed_id)

    if not steam_id_match:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_id_missing")

    steam_id = steam_id_match.group(1)
    user = User.query.get(int(session_user_id))  # session_user_id now comes from signed state token
    if not user:
        return redirect(f"{frontend_url}/dashboard?connection_error=user_missing")

    existing_owner = ConnectedAccount.query.filter_by(
        provider='steam',
        provider_account_id=steam_id
    ).first()
    if existing_owner and existing_owner.user_id != user.id:
        return redirect(f"{frontend_url}/dashboard?connection_error=steam_already_linked")

    try:
        steam_profile = fetch_steam_profile(steam_id)
    except requests.RequestException:
        steam_profile = {
            "display_name": f"Steam {steam_id[-4:]}",
            "avatar_url": None,
            "profile_url": f"https://steamcommunity.com/profiles/{steam_id}",
        }

    account = ConnectedAccount.query.filter_by(user_id=user.id, provider='steam').first()
    if not account:
        account = ConnectedAccount(
            user_id=user.id,
            provider='steam',
            provider_account_id=steam_id,
        )
        db.session.add(account)

    account.provider_account_id = steam_id
    account.display_name = steam_profile.get('display_name')
    account.avatar_url = steam_profile.get('avatar_url')
    account.profile_url = steam_profile.get('profile_url')
    account.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return redirect(f"{frontend_url}/dashboard?linked=steam")  # CHANGED THIS - no session cleanup needed


@app.route('/api/connections/xbox/callback', methods=['GET'])
def xbox_connection_callback():
    print("XBOX_DEBUG_CALLBACK_HIT:", request.url)
    print("XBOX_DEBUG_CALLBACK_ARGS:", dict(request.args))
    print("XBOX_DEBUG_CALLBACK_SESSION:", dict(session))
    frontend_url = get_frontend_base_url()
    if not get_openxbl_app_public_key():
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_not_configured")

    session_user_id = session.get('xbox_link_user_id')
    auth_code = request.args.get('code')
    auth_error = request.args.get('error')

    if auth_error:
        session.pop('xbox_link_user_id', None)
        session.pop('xbox_link_started_at', None)
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_access_denied")

    if not session_user_id:
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_state_invalid")

    if not auth_code:
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_code_missing")

    try:
        print("XBOX_DEBUG_CLAIM_START:", auth_code[:12] + "..." if isinstance(auth_code, str) else auth_code)
        app_key, _claim_payload = claim_openxbl_app_code(auth_code)
        print("XBOX_DEBUG_CLAIM_SUCCESS:", repr(app_key))
        print("XBOX_DEBUG_CLAIM_PAYLOAD:", _claim_payload)
    except (requests.RequestException, ValueError) as exc:
        print("XBOX_DEBUG_CLAIM_FAILED:", repr(exc))
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_profile_failed_claim")

    try:
        xbox_profile = fetch_current_xbox_profile(auth_key=app_key, use_contract=True) or {}
        print("XBOX_DEBUG_PROFILE_SUCCESS:", xbox_profile)
    except (requests.RequestException, ValueError) as exc:
        print("XBOX_DEBUG_PROFILE_FETCH_FAILED:", repr(exc))
        xbox_profile = normalize_xbox_profile(_claim_payload)
        print("XBOX_DEBUG_PROFILE_FROM_CLAIM:", xbox_profile)

    provider_account_id = xbox_profile.get('xuid')
    if not provider_account_id:
        xbox_profile = normalize_xbox_profile(_claim_payload)
        provider_account_id = xbox_profile.get('xuid')
        print("XBOX_DEBUG_PROFILE_FALLBACK_CLAIM:", xbox_profile)
    if not provider_account_id:
        print("XBOX_DEBUG_PROFILE_EMPTY_XUID:", xbox_profile)
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_profile_failed_empty")

    user = User.query.get(int(session_user_id))
    if not user:
        return redirect(f"{frontend_url}/dashboard?connection_error=user_missing")

    existing_owner = ConnectedAccount.query.filter_by(
        provider='xbox',
        provider_account_id=provider_account_id
    ).first()
    if existing_owner and existing_owner.user_id != user.id:
        return redirect(f"{frontend_url}/dashboard?connection_error=xbox_already_linked")

    account = ConnectedAccount.query.filter_by(user_id=user.id, provider='xbox').first()
    if not account:
        account = ConnectedAccount(
            user_id=user.id,
            provider='xbox',
            provider_account_id=provider_account_id,
        )
        db.session.add(account)

    account.provider_account_id = provider_account_id
    account.display_name = xbox_profile.get('display_name') or 'Xbox bruker'
    account.avatar_url = xbox_profile.get('avatar_url')
    account.profile_url = 'https://account.xbox.com/en-us/Profile'
    account.access_token = app_key
    account.refresh_token = None
    account.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    session.pop('xbox_link_user_id', None)
    session.pop('xbox_link_started_at', None)
    return redirect(f"{frontend_url}/dashboard?linked=xbox")


@app.route('/api/dashboard/gaming-summary', methods=['GET'])
@jwt_required()
def get_dashboard_gaming_summary():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    steam_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='steam').first()
    xbox_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='xbox').first()

    steam_summary = {
        'connected': False,
        'configured': bool(os.getenv('STEAM_WEB_API_KEY')),
        'provider': 'steam',
        'message': 'Steam er ikke tilkoblet.',
        'current_game': None,
        'recent_games': [],
        'all_games': [],
        'totals': {'total_hours': 0, 'owned_games': 0, 'recent_games': 0},
    }

    if steam_account:
        if not os.getenv('STEAM_WEB_API_KEY'):
            steam_summary.update({
                'connected': True,
                'configured': False,
                'message': 'Steam er koblet til, men STEAM_WEB_API_KEY mangler i backend-env.',
            })
        else:
            steam_id = steam_account.provider_account_id
            try:
                owned_games_response = steam_api_get(
                    'IPlayerService',
                    'GetOwnedGames',
                    'v0001',
                    {'steamid': steam_id, 'include_appinfo': 1, 'include_played_free_games': 1}
                )
                presence = fetch_steam_presence(steam_account)
            except requests.RequestException as exc:
                steam_summary.update({
                    'connected': True,
                    'configured': True,
                    'message': f'Kunne ikke hente Steam-data akkurat nå: {exc}',
                })
            else:
                player = (presence or {}).get('player', {})
                recent_games = (presence or {}).get('recent_games', [])
                owned_games = (owned_games_response or {}).get('response', {}).get('games', []) or []

                recent_payload = [build_steam_game_payload(game) for game in recent_games[:3]]
                all_games_payload = [
                    build_steam_game_payload(game)
                    for game in sorted(owned_games, key=lambda item: item.get('playtime_forever', 0), reverse=True)[:6]
                ]

                current_game_name = player.get('gameextrainfo') or (recent_payload[0]['title'] if recent_payload else None)
                current_game = None
                if current_game_name:
                    matched_recent = next((game for game in recent_payload if game['title'] == current_game_name), None)
                    current_game = {
                        'title': current_game_name,
                        'subtitle': matched_recent['right_stat'] if matched_recent else (
                            f"{minutes_to_hours(recent_games[0].get('playtime_2weeks', 0))}t siste 2 uker" if recent_games else 'Steam'
                        ),
                        'provider': 'Steam',
                    }

                total_minutes = sum((game.get('playtime_forever', 0) or 0) for game in owned_games)
                steam_summary = {
                    'connected': True,
                    'configured': True,
                    'provider': 'steam',
                    'message': None,
                    'current_game': current_game,
                    'recent_games': recent_payload,
                    'all_games': all_games_payload or recent_payload,
                    'totals': {
                        'total_hours': minutes_to_hours(total_minutes),
                        'owned_games': len(owned_games),
                        'recent_games': len(recent_games),
                    },
                }

    try:
        xbox_summary = build_xbox_summary(xbox_account)
    except (requests.RequestException, RuntimeError) as exc:
        xbox_summary = {
            'connected': xbox_account is not None,
            'configured': is_openxbl_configured(),
            'provider': 'xbox',
            'message': f'Kunne ikke hente Xbox-data akkurat nå: {exc}',
            'current_game': None,
            'recent_games': [],
            'all_games': [],
            'totals': {
                'gamerscore': 0,
                'owned_games': 0,
                'recent_games': 0,
                'achievements_unlocked': 0,
            },
        }

    if not steam_summary.get('connected') and not xbox_summary.get('connected'):
        return jsonify({
            'connected': False,
            'configured': steam_summary.get('configured') or xbox_summary.get('configured'),
            'provider': 'steam',
            'message': 'Steam eller Xbox er ikke tilkoblet.',
            'current_game': None,
            'recent_games': [],
            'all_games': [],
            'totals': {
                'total_hours': 0,
                'owned_games': 0,
                'recent_games': 0,
                'gamerscore': 0,
                'achievements_unlocked': 0,
            },
            'providers': {
                'steam': steam_summary,
                'xbox': xbox_summary,
            },
        }), 200

    merged_recent_games = []
    merged_all_games = []
    if steam_summary.get('connected'):
        merged_recent_games.extend(steam_summary.get('recent_games', []))
        merged_all_games.extend(steam_summary.get('all_games', []))
    if xbox_summary.get('connected'):
        merged_recent_games.extend(xbox_summary.get('recent_games', []))
        merged_all_games.extend(xbox_summary.get('all_games', []))

    deduped_recent_games = []
    seen_recent = set()
    for item in merged_recent_games:
        key = (item.get('platform'), item.get('title'))
        if key in seen_recent:
            continue
        seen_recent.add(key)
        deduped_recent_games.append(item)
        if len(deduped_recent_games) >= 6:
            break

    deduped_all_games = []
    seen_all = set()
    for item in merged_all_games:
        key = (item.get('platform'), item.get('title'))
        if key in seen_all:
            continue
        seen_all.add(key)
        deduped_all_games.append(item)
        if len(deduped_all_games) >= 6:
            break

    active_summary = steam_summary if steam_summary.get('connected') else xbox_summary
    return jsonify({
        'connected': True,
        'configured': steam_summary.get('configured') or xbox_summary.get('configured'),
        'provider': active_summary.get('provider', 'steam'),
        'message': active_summary.get('message'),
        'current_game': active_summary.get('current_game') or xbox_summary.get('current_game'),
        'recent_games': deduped_recent_games,
        'all_games': deduped_all_games or deduped_recent_games,
        'totals': {
            'total_hours': steam_summary.get('totals', {}).get('total_hours', 0),
            'owned_games': len(deduped_all_games),
            'recent_games': len(deduped_recent_games),
            'gamerscore': xbox_summary.get('totals', {}).get('gamerscore', 0),
            'achievements_unlocked': xbox_summary.get('totals', {}).get('achievements_unlocked', 0),
        },
        'providers': {
            'steam': steam_summary,
            'xbox': xbox_summary,
        },
    }), 200


@app.route('/api/home/social-summary', methods=['GET'])
@jwt_required()
def get_home_social_summary():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    now_playing = []
    activity_events = []

    steam_accounts = ConnectedAccount.query.filter_by(provider='steam').order_by(ConnectedAccount.updated_at.desc()).limit(8).all()
    prioritized_accounts = []
    seen_account_ids = set()

    user_steam = next((account for account in steam_accounts if account.user_id == user.id), None)
    if user_steam:
        prioritized_accounts.append(user_steam)
        seen_account_ids.add(user_steam.id)

    for account in steam_accounts:
        if account.id not in seen_account_ids:
            prioritized_accounts.append(account)
            seen_account_ids.add(account.id)

    steam_presences = []
    for account in prioritized_accounts[:5]:
        try:
            presence = fetch_steam_presence(account)
        except requests.RequestException:
            presence = None

        if not presence:
            continue

        account_user = account.user
        recent_primary = presence.get('last_game')
        is_playing = presence.get('is_playing')
        current_title = presence.get('current_game_name') or (recent_primary['title'] if recent_primary else 'Ingen nylig aktivitet')
        steam_presences.append({
            "timestamp_rank": recent_primary['playtime_2weeks_minutes'] if recent_primary else 0,
            "username": get_display_name(account_user),
            "avatarUrl": account_user.avatar,
            "color": build_user_color(account_user),
            "platform": 'steam' if is_playing else 'offline',
            "platformLabel": 'Steam' if is_playing else 'Offline',
            "online": bool(is_playing),
            "game": current_title if is_playing else (f"Sist spilte: {recent_primary['title']}" if recent_primary else 'Ingen nylig spilling'),
            "code": (recent_primary or {}).get('code', 'ST'),
            "artBg": build_user_color(account_user),
            "imageUrl": (recent_primary or {}).get('image_url') or (recent_primary or {}).get('logo_url'),
            "meta": (
                recent_primary['right_stat'] if is_playing and recent_primary
                else (recent_primary['left_stat'] if recent_primary else 'Ikke nok data ennå')
            ),
            "lastSeen": presence.get('last_seen') or 'ukjent',
        })

        latest_steam_achievement = fetch_latest_steam_achievement_event(account, presence)
        if latest_steam_achievement:
            activity_events.append(latest_steam_achievement)

    steam_presences.sort(key=lambda item: (not item['online'], -(item['timestamp_rank'] or 0), item['username'].lower()))
    now_playing = steam_presences[:3]
    for item in now_playing:
        item.pop('timestamp_rank', None)

    latest_site_achievements = (
        db.session.query(UserAchievement, User, Achievement)
        .join(User, UserAchievement.user_id == User.id)
        .join(Achievement, UserAchievement.achievement_id == Achievement.id)
        .order_by(UserAchievement.unlocked_at.desc())
        .limit(5)
        .all()
    )

    for unlock, unlock_user, achievement in latest_site_achievements:
        activity_events.append({
            'timestamp': to_utc_datetime(unlock.unlocked_at),
            'kind': 'site_achievement',
            'provider': 'hmn',
            'providerLabel': 'HMN',
            'actor_name': get_display_name(unlock_user),
            'actor_avatar_url': unlock_user.avatar,
            'actor_color': build_user_color(unlock_user),
            'text': (
                f"<strong>{get_display_name(unlock_user)}</strong> låste opp achievement "
                f"<em>{achievement.name}</em>"
            ),
            'game': None,
            'time': format_time_ago(unlock.unlocked_at),
            'thumb': None,
        })

    recent_music_activities = (
        db.session.query(Activity, User)
        .join(User, Activity.user_id == User.id)
        .filter(Activity.activity_type.like('music_upload:%'))
        .order_by(Activity.timestamp.desc())
        .limit(4)
        .all()
    )

    for activity, activity_user in recent_music_activities:
        song_id_part = activity.activity_type.split(':', 1)[1] if ':' in activity.activity_type else ''
        song = Song.query.get(int(song_id_part)) if song_id_part.isdigit() else None
        if not song:
            continue
        activity_events.append({
            'timestamp': to_utc_datetime(activity.timestamp),
            'kind': 'music_upload',
            'provider': 'sc',
            'providerLabel': 'SoundCloud',
            'actor_name': get_display_name(activity_user),
            'actor_avatar_url': activity_user.avatar,
            'actor_color': build_user_color(activity_user),
            'text': (
                f"<strong>{get_display_name(activity_user)}</strong> lastet opp ny banger "
                f"<em>{song.title}</em> til Bangerfabrikken"
            ),
            'game': None,
            'time': format_time_ago(activity.timestamp),
            'thumb': {
                'code': ''.join(part[0] for part in song.title.split()[:3]).upper()[:4] or 'SC',
                'image_url': song.thumbnail_url or song.cover,
                'bg': 'linear-gradient(135deg,#2d120a,#7c2d12)',
            },
        })

    activity_events.sort(key=lambda item: item.get('timestamp') or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    activity_feed = []
    for item in activity_events[:6]:
        thumb = item.get('thumb')
        activity_feed.append({
            'isNew': True,
            'avatar': (item.get('actor_name') or 'H')[0].upper(),
            'avatarUrl': item.get('actor_avatar_url'),
            'color': item.get('actor_color'),
            'online': False,
            'text': item.get('text'),
            'time': item.get('time') or format_time_ago(item.get('timestamp')),
            'plat': item.get('provider'),
            'platLabel': item.get('providerLabel'),
            'game': item.get('game'),
            'thumb': {
                'bg': thumb.get('bg') if thumb else 'linear-gradient(135deg,#0a1628,#1a3a6a)',
                'code': thumb.get('code') if thumb else '',
                'imageUrl': thumb.get('image_url') if thumb else None,
            } if thumb else None,
        })

    return jsonify({
        'now_playing': now_playing,
        'activity_feed': activity_feed,
    }), 200


@app.route('/api/dashboard/recent-achievements', methods=['GET'])
@jwt_required()
def get_dashboard_recent_achievements():
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    max_items = 4
    achievement_items = []

    steam_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='steam').first()
    if steam_account:
        try:
            steam_item = fetch_latest_steam_achievement_event(steam_account)
        except requests.RequestException:
            steam_item = None
        if steam_item:
            thumb = steam_item.get('thumb') or {}
            achievement_items.append({
                'id': f"steam-{steam_account.user_id}-{thumb.get('id') or steam_item.get('timestamp').timestamp()}",
                'title': re.search(r'<em>(.*?)</em>', steam_item.get('text', '')) and re.search(r'<em>(.*?)</em>', steam_item.get('text', '')).group(1) or 'Steam achievement',
                'game': steam_item.get('game') or 'Steam',
                'icon': thumb.get('image_url') or thumb.get('logo_url') or '🏆',
                'is_img': bool(thumb.get('image_url') or thumb.get('logo_url')),
                'icon_class': 'aig',
                'platform': 'Steam',
                'platform_class': 'aps',
                'timestamp': steam_item.get('timestamp'),
                'source': 'steam',
            })

    latest_site_achievements = (
        db.session.query(UserAchievement, Achievement)
        .join(Achievement, UserAchievement.achievement_id == Achievement.id)
        .filter(UserAchievement.user_id == user.id)
        .order_by(UserAchievement.unlocked_at.desc())
        .limit(6)
        .all()
    )

    for unlock, achievement in latest_site_achievements:
        achievement_items.append({
            'id': f"hmn-{achievement.id}",
            'title': achievement.name,
            'game': 'HMN Portalen',
            'icon': achievement.icon or '🔥',
            'is_img': isinstance(achievement.icon, str) and (achievement.icon.startswith('http') or achievement.icon.startswith('data:')),
            'icon_class': 'air',
            'platform': 'HMN',
            'platform_class': 'aph',
            'timestamp': to_utc_datetime(unlock.unlocked_at),
            'source': 'hmn',
        })

    xbox_account = ConnectedAccount.query.filter_by(user_id=user.id, provider='xbox').first()
    xbox_auth_key = ((xbox_account.access_token or '').strip() if xbox_account else '') or get_openxbl_api_key()
    xbox_use_contract = bool(xbox_account and (xbox_account.access_token or '').strip())
    if xbox_account and xbox_auth_key:
        try:
            xbox_titles = fetch_xbox_title_achievements(
                xbox_account.provider_account_id,
                auth_key=xbox_auth_key,
                use_contract=xbox_use_contract,
            )
        except requests.RequestException:
            xbox_titles = []

        for title in xbox_titles[:3]:
            title_id = title.get('title_id')
            if not title_id:
                continue
            try:
                xbox_achievements = fetch_xbox_achievement_details(
                    xbox_account.provider_account_id,
                    title_id,
                    fallback_title=title.get('title'),
                    auth_key=xbox_auth_key,
                    use_contract=xbox_use_contract,
                )
            except requests.RequestException:
                continue

            unlocked_items = [item for item in xbox_achievements if item.get('unlocked')]
            if not unlocked_items:
                continue

            unlocked_items.sort(key=lambda entry: entry.get('timestamp') or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
            latest = unlocked_items[0]
            achievement_items.append({
                'id': f"xbox-{title_id}-{latest['id']}",
                'title': latest['title'],
                'game': latest['game'],
                'icon': latest['icon'],
                'is_img': latest['is_img'],
                'icon_class': latest['icon_class'],
                'platform': 'Xbox',
                'platform_class': 'apx',
                'timestamp': latest.get('timestamp'),
                'source': 'xbox',
            })

    deduped = []
    seen = set()
    for item in sorted(achievement_items, key=lambda entry: entry.get('timestamp') or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
        dedupe_key = (item['source'], item['title'], item['game'])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break

    return jsonify({
        'items': [
            {
                'id': item['id'],
                'title': item['title'],
                'game': item['game'],
                'icon': item['icon'],
                'is_img': item['is_img'],
                'icon_class': item['icon_class'],
                'platform': item['platform'],
                'platform_class': item['platform_class'],
            }
            for item in deduped
        ],
        'disclaimer': 'Eksterne achievements vises bare når Steam/Xbox returnerer dem for nylige spill og profiler vi faktisk har tilgang til.',
        'rules': {
            'max_items': max_items,
            'steam_per_account': 1,
            'dedupe_by_title_and_game': True,
            'fills_indefinitely': False,
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
            "discord_id": user.discord_id,
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
    user = get_authenticated_user()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json() or {}
    requested_username = data.get('username')
    requested_display_name = data.get('display_name')
    requested_bio = data.get('bio')
    requested_banner_url = data.get('banner_url')

    if requested_username is not None:
        is_valid, error_message, sanitized_username = validate_settings_username(
            requested_username,
            current_user_id=user.id
        )
        if not is_valid:
            return jsonify({"msg": error_message}), 400
        user.username = sanitized_username

    if requested_bio is not None:
        normalized_bio = str(requested_bio).strip()
        if len(normalized_bio) > 300:
            return jsonify({"msg": "Bio kan ikke overstige 300 tegn."}), 400
        user.bio = normalized_bio or None

    if requested_display_name is not None:
        normalized_display_name = str(requested_display_name).strip()
        if len(normalized_display_name) > 80:
            return jsonify({"msg": "Visningsnavn kan ikke overstige 80 tegn."}), 400
        set_user_setting(user.id, 'display_name', normalized_display_name or user.username or user.email)

    if requested_banner_url is not None:
        normalized_banner_url = str(requested_banner_url).strip()
        user.banner = normalized_banner_url or None

    db.session.commit()

    return jsonify({
        "msg": "Profil oppdatert.",
        "user": serialize_authenticated_user(user)
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
    
    if not can_manage_music(user):
        return jsonify({"msg": "Insufficient permission to upload songs."}), 403

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
    
    if not can_manage_music(user):
        return jsonify({"msg": "Insufficient permission to delete songs."}), 403

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
    
    if not can_manage_music(user):
        return jsonify({"msg": "Insufficient permission to upload songs."}), 403

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


@app.route('/api/hendelser', methods=['GET'])
def get_public_upcoming_hendelser():
    """Public endpoint for homepage upcoming events."""
    try:
        today = datetime.utcnow().date()
        limit = request.args.get('limit', default=3, type=int) or 3
        upcoming_only = str(request.args.get('upcoming', 'true')).lower() in ('1', 'true', 'yes')

        query = Event.query
        if upcoming_only:
            query = query.filter(Event.event_date >= today)

        events = query.order_by(Event.event_date.asc(), Event.event_time.asc()).limit(max(1, min(limit, 6))).all()

        hendelser = []
        for event in events:
            badge_type = 'planned'
            if event.event_date == today:
                badge_type = 'today'
            elif (event.event_date - today).days <= 3:
                badge_type = 'soon'

            hendelser.append({
                "id": event.id,
                "title": event.event_name,
                "date": event.event_date.isoformat() if event.event_date else None,
                "time": event.event_time.isoformat() if event.event_time else None,
                "description": event.event_description,
                "badge_type": badge_type,
                "template_name": event.template_name,
            })

        return jsonify(hendelser), 200

    except Exception as e:
        print(f"Database error fetching public hendelser: {e}")
        return jsonify({"error": "Failed to fetch hendelser"}), 500


@app.route('/api/cod/leaderboard', methods=['GET'])
@jwt_required()
def get_cod_leaderboard():
    try:
        if not is_cito_configured():
            return jsonify({
                "configured": False,
                "leaderboard": [],
                "message": "CITO_API_KEY mangler i backend-env.",
            }), 200

        current_user_id = int(get_jwt_identity())
        friend_ids = [
            friendship.friend_id
            for friendship in Friendship.query.filter_by(user_id=current_user_id).all()
        ]
        relevant_user_ids = [current_user_id, *friend_ids]

        linked_accounts = (
            ConnectedAccount.query
            .filter(
                ConnectedAccount.user_id.in_(relevant_user_ids),
                ConnectedAccount.provider == 'cod'
            )
            .all()
        )

        if not linked_accounts:
            return jsonify({
                "configured": True,
                "leaderboard": [],
                "message": "Ingen venner har koblet til CoD-profil ennå.",
            }), 200

        users_by_id = {
            user.id: user
            for user in User.query.filter(User.id.in_(relevant_user_ids)).all()
        }

        rows = []
        for account in linked_accounts:
            try:
                payload = cito_api_get(f'cod/players/{account.provider_account_id}')
                row = payload.get('data') or {}
                if not isinstance(row, dict) or not row:
                    continue
                row['_linked_user'] = users_by_id.get(account.user_id)
                row['_linked_account'] = account
                rows.append(row)
            except Exception as inner_error:
                print(f"Cito player fetch error for account {account.provider_account_id}: {inner_error}")

        trimmed_rows = sorted(
            rows,
            key=lambda row: parse_int((row.get('earningsSummary') or {}).get('totalEarnings') or row.get('totalEarnings')),
            reverse=True
        )[:6]

        highest_earnings = max(
            [
                parse_int((row.get('earningsSummary') or {}).get('totalEarnings') or row.get('totalEarnings'))
                for row in trimmed_rows
            ] or [0]
        )

        gradients = [
            'linear-gradient(135deg,#0b5cad,#103f73)',
            'linear-gradient(135deg,#c8102e,#7a0e1e)',
            'linear-gradient(135deg,#7a3cff,#3a1b75)',
            'linear-gradient(135deg,#12805b,#0f4d38)',
            'linear-gradient(135deg,#d89820,#8a6112)',
            'linear-gradient(135deg,#3556a8,#1d2f63)',
        ]

        leaderboard = []
        for index, row in enumerate(trimmed_rows, start=1):
            earnings = parse_int((row.get('earningsSummary') or {}).get('totalEarnings') or row.get('totalEarnings'))
            percent = int(round((earnings / highest_earnings) * 100)) if highest_earnings else 0
            current_team = row.get('currentTeam') or {}
            linked_user = row.get('_linked_user')
            linked_account = row.get('_linked_account')
            subtitle_bits = []
            if linked_user and linked_user.username:
                subtitle_bits.append(linked_user.username)
            if current_team.get('name'):
                subtitle_bits.append(current_team.get('name'))
            elif row.get('country'):
                subtitle_bits.append(row.get('country'))
            elif row.get('region'):
                subtitle_bits.append(row.get('region'))

            subtitle = ' · '.join(subtitle_bits) if subtitle_bits else 'CoD esports'

            leaderboard.append({
                'position': index,
                'name': first_non_empty(
                    linked_account.display_name if linked_account else None,
                    row.get('ign'),
                    row.get('playerName'),
                    row.get('realName'),
                    'Ukjent spiller'
                ),
                'subtitle': subtitle,
                'pct': percent,
                'value': earnings,
                'value_label': f"${earnings:,.0f}",
                'avatar_url': first_non_empty(
                    row.get('imageUrl'),
                    linked_account.avatar_url if linked_account else None,
                    linked_user.avatar if linked_user else None,
                ),
                'color': gradients[(index - 1) % len(gradients)],
            })

        return jsonify({
            "configured": True,
            "leaderboard": leaderboard,
        }), 200
    except Exception as e:
        print(f"Cito leaderboard error: {e}")
        return jsonify({"error": "Failed to fetch CoD leaderboard"}), 500


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
        user_roles = [serialize_role(role) for role in user.roles]

        users_list.append({
            'id': user.id,
            'username': user.username if user.username else '',
            'email': user.email if user.email else '',
            'permissions': get_user_permissions(user),
            'dashboard_flavor': get_user_dashboard_flavor(user),
            'roles': user_roles
        })
    return jsonify({'users': users_list}), 200

# ===================== END get_users ENDPOINT =====================



# ===================== START get_roles ENDPOINT =====================
@app.route('/api/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    roles_list = [serialize_role(role) for role in roles]
    return jsonify({'roles': roles_list, 'permission_catalog': serialize_permission_catalog()}), 200
# ===================== END get_roles ENDPOINT =====================

# ===================== START update_user_roles ENDPOINT =====================
@app.route('/api/update-user-roles', methods=['PUT'])
@jwt_required()
def update_user_roles():
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    if not admin_user or not user_has_any_permission(admin_user, ['manage_users', 'manage_roles']):
        return jsonify({"msg": "Only users with role management access can update user roles"}), 403

    data = request.get_json()
    user_id_to_update = data.get('user_id')
    role_ids = data.get('role_ids')

    if not user_id_to_update or not isinstance(role_ids, list) or not role_ids:
        return jsonify({"msg": "Missing user_id or role_ids parameter"}), 400

    user = User.query.get(user_id_to_update)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    added_any_role = False
    for role_id in role_ids:
        role = resolve_role_for_assignment(role_id)
        if role and role not in user.roles:
            user.roles.append(role)
            added_any_role = True

    if not added_any_role:
        return jsonify({"msg": "User already has the selected role"}), 200

    db.session.commit()

    # --- Real-time update using python-socketio client ---
    sio_client = py_socketio.Client()
    print("Flask backend: Attempting to connect to Socket.IO server...")
    try:
        sio_client.connect('http://localhost:3000') # Replace if needed
        print("Flask backend: Successfully connected.")
        roles = [serialize_role(role) for role in user.roles]
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
            "roles": [serialize_role(role) for role in user.roles]
        }
    }), 200

# ===================== END update_user_roles ENDPOINT ===================

# ===================== START Demote_user_roles ENDPOINT =====================
@app.route('/api/demote-user', methods=['PUT'])
@jwt_required()
def demote_user():
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    if not user_has_any_permission(admin_user, ['manage_users', 'manage_roles']):
        return jsonify({"msg": "Only users with role management access can demote users"}), 403

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

    updated_roles = [serialize_role(role) for role in user_to_demote.roles]

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

    if not user_has_permission(admin_user, 'manage_roles'):
        return jsonify({"msg": "Only users with role management access can create roles"}), 403

    data = request.get_json()
    role_name = normalize_role_name(data.get("name"))
    badge_icon = data.get("badge_icon")
    badge_color = data.get("badge_color")
    dashboard_flavor = data.get("dashboard_flavor") or DEFAULT_DASHBOARD_FLAVOR

    if not role_name:
        return jsonify({"msg": "Role name is required"}), 400

    existing_role = Role.query.filter(db.func.lower(Role.name) == role_name.lower()).first()
    if existing_role:
        return jsonify({
            "msg": f"Role '{existing_role.name}' already exists",
            "role": serialize_role(existing_role)
        }), 409

    new_role = Role(name=role_name, badge_icon=badge_icon, badge_color=badge_color)
    db.session.add(new_role)
    db.session.flush()
    set_role_metadata(new_role, {
        "system_role": False,
        "dashboard_flavor": dashboard_flavor,
        "permissions": [],
    })
    db.session.commit()

    return jsonify({"msg": "Role created successfully", "role": serialize_role(new_role)}), 201


# Endpoint to delete a role
@app.route('/api/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    current_user_id = get_jwt_identity()
    admin_user = User.query.get(int(current_user_id))
    if not user_has_permission(admin_user, 'manage_roles'):
        return jsonify({"msg": "Only users with role management access can delete roles"}), 403

    role = Role.query.get(role_id)
    if not role:
        return jsonify({"msg": "Role not found"}), 404

    if get_role_metadata(role).get('system_role'):
        return jsonify({"msg": "System roles cannot be deleted"}), 400

    # Optional: Prevent deletion if the role is assigned to any user
    if role.users:
        return jsonify({"msg": "Role is assigned to users. Unassign before deletion."}), 400

    role_meta_setting = Setting.query.filter_by(key=get_role_setting_key(role.id, 'meta')).first()
    if role_meta_setting:
        db.session.delete(role_meta_setting)

    db.session.delete(role)
    db.session.commit()
    return jsonify({"msg": "Role deleted successfully"}), 200


register_role_permission_routes(
    app,
    User=User,
    Role=Role,
    db=db,
    serialize_role=serialize_role,
    get_role_metadata=get_role_metadata,
    set_role_metadata=set_role_metadata,
    normalize_permission_keys=normalize_permission_keys,
)


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
    db.session.flush()
    db.session.add(Activity(
        user_id=user.id,
        activity_type=f'music_upload:{new_song.id}'
    ))
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
    db.session.flush()
    db.session.add(Activity(
        user_id=user.id,
        activity_type=f'music_upload:{new_song.id}'
    ))
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


@app.route('/api/achievements/<string:id>', methods=['DELETE'])
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
    result = []
    for a in all_achievements:
        unlocked_count = UserAchievement.query.filter_by(achievement_id=a.id).count()
        result.append({
            "id": a.id,
            "title": a.name,
            "icon": a.icon,
            "description": a.description,
            "rarity": a.rarity,
            "glow_color": a.glow_color,
            "condition_type": a.condition_type,
            "condition_value": a.condition_value,
            "unlocked_count": unlocked_count,
        })
    return jsonify(result), 200

@app.route('/api/achievements', methods=['POST'])
@jwt_required()
def create_achievement():
    import uuid, re as _re
    data = request.get_json()
    if not data.get('title') or not data.get('description'):
        return jsonify({'msg': 'Missing required fields'}), 400

    # Auto-generate slug ID from title, fall back to UUID on collision
    base_id = _re.sub(r'[^a-z0-9]+', '-', data['title'].lower()).strip('-') or str(uuid.uuid4())
    final_id = base_id
    counter = 1
    while Achievement.query.get(final_id):
        final_id = f"{base_id}-{counter}"
        counter += 1

    new_ach = Achievement(
        id=final_id,
        name=data.get('title'),
        description=data.get('description'),
        icon=data.get('icon'),
        condition_type=data.get('condition_type') or None,
        condition_value=data.get('condition_value'),
        rarity=data.get('rarity', 'common'),
        glow_color=data.get('glow_color')
    )
    db.session.add(new_ach)
    db.session.commit()
    return jsonify({'msg': 'Achievement created', 'id': new_ach.id}), 201


@app.route('/api/admin/give-achievement', methods=['POST'])
@jwt_required()
def admin_give_achievement():
    current_user_id = get_jwt_identity()
    admin = User.query.get(int(current_user_id))
    if not admin or not any(r.name.lower() in ['admin', 'developer'] for r in admin.roles):
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.get_json()
    user_id = data.get('user_id')
    achievement_id = data.get('achievement_id')
    if not user_id or not achievement_id:
        return jsonify({'msg': 'Missing fields'}), 400
    target = User.query.get(int(user_id))
    ach = Achievement.query.get(achievement_id)
    if not target or not ach:
        return jsonify({'msg': 'User or achievement not found'}), 404
    existing = UserAchievement.query.filter_by(user_id=user_id, achievement_id=achievement_id).first()
    if existing:
        return jsonify({'msg': 'Already unlocked'}), 409
    ua = UserAchievement(user_id=user_id, achievement_id=achievement_id,
                         unlocked_at=datetime.now(timezone.utc), unlocked=True)
    db.session.add(ua)
    db.session.commit()
    return jsonify({'msg': 'Achievement given'}), 201


@app.route('/api/achievements/<string:ach_id>', methods=['PUT'])
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


# -----------------------------------------------
# BEDRIFTSMELDINGER ROUTES
# -----------------------------------------------

def _melding_dict(m):
    author = None
    if m.user:
        author = {
            'id': m.user.id,
            'username': m.user.username,
            'avatar': m.user.avatar if hasattr(m.user, 'avatar') else None,
            'roles': [r.name for r in m.user.roles] if m.user.roles else [],
        }
    return {
        'id': m.id,
        'ref': m.ref,
        'title': m.title,
        'content': m.content,
        'category': m.category,
        'tag': m.tag,
        'pinned': m.pinned,
        'notify_users': m.notify_users,
        'created_at': m.created_at.isoformat() + 'Z',
        'author': author,
    }


@app.route('/api/bedriftsmeldinger', methods=['GET'])
@jwt_required(optional=True)
def get_bedriftsmeldinger():
    items = Bedriftsmelding.query.order_by(Bedriftsmelding.pinned.desc(), Bedriftsmelding.created_at.desc()).all()
    return jsonify([_melding_dict(m) for m in items])


@app.route('/api/bedriftsmeldinger/<int:melding_id>', methods=['GET'])
@jwt_required(optional=True)
def get_single_bedriftsmelding(melding_id):
    m = Bedriftsmelding.query.get_or_404(melding_id)
    others = Bedriftsmelding.query.filter(Bedriftsmelding.id != melding_id)\
        .order_by(Bedriftsmelding.pinned.desc(), Bedriftsmelding.created_at.desc())\
        .limit(3).all()
    return jsonify({
        'melding': _melding_dict(m),
        'others': [_melding_dict(o) for o in others],
    })


@app.route('/api/bedriftsmeldinger', methods=['POST'])
@jwt_required()
def create_bedriftsmelding():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not can_manage_bedriftsmeldinger(user):
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()

    # Auto-generate ref
    count = Bedriftsmelding.query.count()
    ref = f"HMN-MSG-{count + 1:03d}"
    # Ensure uniqueness
    while Bedriftsmelding.query.filter_by(ref=ref).first():
        count += 1
        ref = f"HMN-MSG-{count + 1:03d}"

    # If pinning, unpin all others
    if data.get('pinned'):
        Bedriftsmelding.query.filter_by(pinned=True).update({'pinned': False})

    m = Bedriftsmelding(
        ref=ref,
        title=data['title'],
        content=data['content'],
        category=data.get('category', 'oppdatering'),
        tag=data.get('tag'),
        pinned=data.get('pinned', False),
        notify_users=data.get('notify_users', False),
        user_id=current_user_id,
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(_melding_dict(m)), 201


@app.route('/api/bedriftsmeldinger/<int:melding_id>', methods=['PUT'])
@jwt_required()
def update_bedriftsmelding(melding_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not can_manage_bedriftsmeldinger(user):
        return jsonify({'message': 'Unauthorized'}), 403

    m = Bedriftsmelding.query.get_or_404(melding_id)
    data = request.get_json()

    # If pinning this one, unpin all others first
    if data.get('pinned') and not m.pinned:
        Bedriftsmelding.query.filter_by(pinned=True).update({'pinned': False})

    m.title = data.get('title', m.title)
    m.content = data.get('content', m.content)
    m.category = data.get('category', m.category)
    m.tag = data.get('tag', m.tag)
    m.pinned = data.get('pinned', m.pinned)
    m.notify_users = data.get('notify_users', m.notify_users)

    db.session.commit()
    return jsonify(_melding_dict(m))


@app.route('/api/bedriftsmeldinger/<int:melding_id>', methods=['DELETE'])
@jwt_required()
def delete_bedriftsmelding(melding_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not can_manage_bedriftsmeldinger(user):
        return jsonify({'message': 'Unauthorized'}), 403

    m = Bedriftsmelding.query.get_or_404(melding_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200


try:
    from mini_games.ClickerApi import clicker_api, init_db
except ModuleNotFoundError:
    from Backend.mini_games.ClickerApi import clicker_api, init_db
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
