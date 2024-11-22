# backend/models.py

from database import db

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    summoner_name = db.Column(db.String(80), unique=True, nullable=False)
    last_score = db.Column(db.Float)

    def __init__(self, summoner_name, last_score=None):
        self.summoner_name = summoner_name
        self.last_score = last_score