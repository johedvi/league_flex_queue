# backend/models.py

from database import db
from datetime import datetime

class Player(db.Model):
    __tablename__ = 'players'  # Renamed to 'players' to match conventions
    id = db.Column(db.Integer, primary_key=True)
    summoner_name = db.Column(db.String(80), unique=True, nullable=False)
    tagline = db.Column(db.String(10), nullable=False)
    puuid = db.Column(db.String(100), unique=True, nullable=False)
    total_score = db.Column(db.Float, default=0.0)
    average_score = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Match model
    matches = db.relationship('Match', backref='player', lazy=True, cascade="all, delete-orphan")

    def __init__(self, summoner_name, tagline, puuid, total_score=0.0, average_score=0.0):
        self.summoner_name = summoner_name
        self.tagline = tagline
        self.puuid = puuid
        self.total_score = total_score
        self.average_score = average_score
        self.last_updated = datetime.utcnow()

    def __repr__(self):
        return f'<Player {self.summoner_name}#{self.tagline}>'

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), unique=True, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    kills = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    cs = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, match_id, player_id, score, kills, deaths, assists, cs, timestamp):
        self.match_id = match_id
        self.player_id = player_id
        self.score = score
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.cs = cs
        self.timestamp = timestamp

    def __repr__(self):
        return f'<Match {self.match_id} for Player ID {self.player_id}>'
