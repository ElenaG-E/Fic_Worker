from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
import base64

db = SQLAlchemy()

# Generate or load encryption key for API keys
def get_encryption_key():
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        # In production, store this securely
        print(f"Generated encryption key: {key}")
    return key.encode()

cipher = Fernet(get_encryption_key())

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    api_keys = db.Column(db.Text, nullable=True)  # Encrypted JSON string of API keys
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_api_keys(self, keys_list):
        """Encrypt and store API keys as JSON string"""
        import json
        keys_json = json.dumps(keys_list)
        self.api_keys = cipher.encrypt(keys_json.encode()).decode()

    def get_api_keys(self):
        """Decrypt and return API keys as list"""
        if not self.api_keys:
            return []
        import json
        decrypted = cipher.decrypt(self.api_keys.encode()).decode()
        return json.loads(decrypted)

    def __repr__(self):
        return f'<User {self.username}>'

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('stories', lazy=True))

    def __repr__(self):
        return f'<Story {self.title or "Untitled"}>'
