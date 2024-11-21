# backend/models.py

from database import db  # Import db from database.py

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summoner_name = db.Column(db.String(50), unique=True, nullable=False)
    last_score = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Player {self.summoner_name}>'
