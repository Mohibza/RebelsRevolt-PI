from . import db
from datetime import datetime

class ApiCredential(db.Model):
    __tablename__ = 'api_credentials'
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(200), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(100), nullable=False, default='Eyecon Key')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ImportedNumber(db.Model):
    __tablename__ = 'imported_numbers'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), unique=True, nullable=False)
    searched = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EyeconResult(db.Model):
    __tablename__ = 'eyecon_results'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(500))
    credential_used = db.Column(db.String(200))
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

class FacebookResult(db.Model):
    __tablename__ = 'facebook_results'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), nullable=False)
    fb_id = db.Column(db.String(200))
    fb_link = db.Column(db.String(500))
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)
