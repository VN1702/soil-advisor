from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class RecommendationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String(100))
    soil_info = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    language = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
