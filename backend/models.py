from database import db
from datetime import datetime

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    summoner_name = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(10), nullable=False, default='')
    puuid = db.Column(db.String(100), unique=True, nullable=False, default='')
    total_score = db.Column(db.Float, default=0.0)
    average_score = db.Column(db.Float, default=0.0)
    last_match_id = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    all_time_highest_score = db.Column(db.Float, default=0.0)  # Track all-time highest score
    all_time_lowest_score = db.Column(db.Float, nullable=True)  # Track all-time lowest score

    # Relationship to Match model
    matches = db.relationship('Match', backref='player', lazy=True, cascade="all, delete-orphan")

    def __init__(self, summoner_name, tagline='', puuid='', last_match_id=None):
        self.summoner_name = summoner_name
        self.tagline = tagline
        self.puuid = puuid
        self.total_score = 0.0
        self.average_score = 0.0
        self.last_match_id = last_match_id
        self.last_updated = datetime.utcnow()
        self.all_time_highest_score = 0.0
        self.all_time_lowest_score = None

    def __repr__(self):
        return f'<Player {self.summoner_name}#{self.tagline}>'


class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    kills = db.Column(db.Integer, nullable=False)
    deaths = db.Column(db.Integer, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    cs = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    assigned_role = db.Column(db.String(20), default="Undefined") 


    __table_args__ = (db.UniqueConstraint('match_id', 'player_id', name='_match_player_uc'),)

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
