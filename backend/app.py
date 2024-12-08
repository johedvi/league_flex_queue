# backend/app.py

# Import gevent monkey patching
from gevent import monkey
monkey.patch_all()

import os
import time
from threading import Lock
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate  # Import Flask-Migrate
import logging
from datetime import datetime

from riot_api import (
    get_summoner_info,
    get_match_ids_by_summoner_puuid,
    get_recent_match_id,
    get_match_data,
    get_player_stats_in_match,
    calculate_scores
)
import settings
from database import db

from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
app.config.from_object(settings.Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Configure SocketIO with the allowed origins
socketio = SocketIO(app, cors_allowed_origins=[
    "https://blackultras.com",
    "http://blackultras.com",
    "https://www.blackultras.com"
], async_mode='gevent')

# Import models after initializing db to prevent circular imports
from models import Player, Match  # Ensure Match model is imported

# In-memory queue for players (use a database or persistent storage in production)
player_queue = []

# Define the predefined list of players for the leaderboard
PREDEFINED_PLAYERS = [
    {'summoner_name': 'lil newton', 'tagline': 'EUNE'},
    {'summoner_name': 'bigbrainburton', 'tagline': 'EUNE'},
    {'summoner_name': 'mysman', 'tagline': 'EUNE'},
    {'summoner_name': 'optimus d snutz', 'tagline': '6969'},
    {'summoner_name': 'zyzz enjoyer', 'tagline': '1337'},
    {'summoner_name': 'bajveck', 'tagline': 'EUNE'},
    {'summoner_name': 'rob', 'tagline': '13371'},
    {'summoner_name': 'jonteproo', 'tagline': 'EUNE'},
    {'summoner_name': 'stiga12', 'tagline': 'EUNE'},
    {'summoner_name': 'lHgXRudolf', 'tagline': 'EUNE'},
    # Add more players as needed
]

# Initialize caching
from flask_caching import Cache  # Import Flask-Caching

cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})  # Cache timeout set to 5 minutes
cache.init_app(app)

# Initialize the lock and last update time for leaderboard updates
leaderboard_lock = Lock()
last_leaderboard_update = 0  # Timestamp of the last update

# Initialize the scheduler
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

def update_leaderboard_task():
    with app.app_context():
        update_leaderboard()

# Schedule the leaderboard update every 2 minutes
scheduler.add_job(func=update_leaderboard_task, trigger="interval", minutes=2)

@app.after_request
def add_cors_headers(response):
    allowed_origins = ["https://blackultras.com", "https://www.blackultras.com"]
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    response = jsonify({'error': 'Internal server error'})
    response.status_code = 500
    return response

@app.route('/')
def index():
    return "Backend is running!", 200

@app.route('/api/queue', methods=['GET', 'POST'])
def manage_queue():
    """
    GET: Retrieve the current queue.
    POST: Add a new player to the queue.
    """
    if request.method == 'GET':
        return jsonify({'queue': player_queue}), 200

    if request.method == 'POST':
        data = request.get_json()
        player_name = data.get('player_name')
        if player_name:
            # Check if player is already in the queue
            if player_name in player_queue:
                return jsonify({'error': 'Player already in the queue.'}), 400

            player_queue.append(player_name)
            # Do NOT add to the database
            # Emit the updated queue to all connected clients
            socketio.emit('queue_updated', {'queue': player_queue})
            logging.info(f"Emitted 'queue_updated' event: {player_queue}")
            return jsonify({'message': f'{player_name} added to the queue.', 'queue': player_queue}), 201
        else:
            return jsonify({'error': 'Player name is required.'}), 400

@app.route('/api/search', methods=['GET'])
def search_player():
    """
    Search for a player and calculate team scores.
    """
    summoner_name = request.args.get('summoner_name')
    summoner_tagline = request.args.get('summoner_tagline')

    if not summoner_name or not summoner_tagline:
        logging.warning("Summoner name or tagline missing in the request.")
        return jsonify({'error': 'Summoner name and tagline are required.'}), 400

    logging.info(f"Searching for summoner: {summoner_name}#{summoner_tagline}")

    # Fetch player PUUID
    player_info = get_summoner_info(summoner_name, summoner_tagline, region=settings.Config.DEFAULT_REGION)
    if not player_info:
        logging.error(f"Player {summoner_name}#{summoner_tagline} not found.")
        return jsonify({'error': 'Player not found.'}), 404

    puuid = player_info.get('puuid')
    if not puuid:
        logging.error(f"PUUID not found for player {summoner_name}#{summoner_tagline}.")
        return jsonify({'error': 'PUUID not found for the player.'}), 404

    # Fetch recent match ID
    match_id = get_recent_match_id(puuid, region=settings.Config.DEFAULT_REGION)
    if not match_id:
        logging.error(f"No recent matches found for PUUID: {puuid}.")
        return jsonify({'error': 'No recent matches found.'}), 404


    # Fetch team members
    match_data = get_match_data(match_id, region=settings.Config.DEFAULT_REGION)
    if not match_data:
        logging.error(f"Unable to retrieve match data for match ID: {match_id}.")
        return jsonify({'error': 'Unable to retrieve match data.'}), 404

    team_members = get_player_stats_in_match(puuid, match_data, team_only=True)
    if not team_members:
        logging.error(f"Unable to retrieve team members for match ID: {match_id}.")
        return jsonify({'error': 'Unable to retrieve team members.'}), 404

    # Calculate scores
    scores = calculate_scores(team_members)

    # Identify the player with the lowest score
    scores_sorted = sorted(scores, key=lambda x: x['score'])
    player_to_remove = scores_sorted[0] if scores_sorted else None

    # Handle queue logic
    if player_queue:
        new_player_name = player_queue.pop(0)  # Remove the first player in the queue
        logging.info(f"Adding new player from queue: {new_player_name}")
        # Emit the updated queue to all connected clients
        socketio.emit('queue_updated', {'queue': player_queue})
        logging.info(f"Emitted 'queue_updated' event: {player_queue}")
    else:
        new_player_name = None  # No one in the queue

    # Remove the player being searched for from wherever necessary
    logging.info(f"Player to remove: {player_to_remove}")
    logging.info(f"New player added: {new_player_name}")

    return jsonify({
        'scores': scores_sorted,
        'player_to_remove': player_to_remove,
        'new_player_added': new_player_name
    }), 200

@app.route('/api/players', methods=['GET'])
def get_players():
    """
    Retrieve all players from the predefined list.
    """
    players_data = [
        {
            'summoner_name': player_info['summoner_name'],
            'tagline': player_info['tagline']
        }
        for player_info in PREDEFINED_PLAYERS
    ]
    return jsonify({'players': players_data}), 200

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Retrieve the leaderboard data from the cache.
    """
    leaderboard_data = cache.get('leaderboard_data')
    if leaderboard_data:
        return jsonify({'leaderboard': leaderboard_data}), 200
    else:
        return jsonify({'error': 'Unable to retrieve leaderboard data.'}), 500

def update_leaderboard():
    """
    Updates the leaderboard by checking for new matches for each player.
    """
    with app.app_context():
        for player_info in PREDEFINED_PLAYERS:
            summoner_name = player_info['summoner_name']
            tagline = player_info['tagline']

            # Fetch player from database or create if not exists
            player = Player.query.filter_by(summoner_name=summoner_name, tagline=tagline).first()
            if not player:
                # Fetch player PUUID
                player_data = get_summoner_info(summoner_name, tagline, region=settings.Config.DEFAULT_REGION)
                if not player_data:
                    logging.error(f"Player {summoner_name}#{tagline} not found.")
                    continue  # Skip to the next player

                puuid = player_data.get('puuid')
                if not puuid:
                    logging.error(f"PUUID not found for player {summoner_name}#{tagline}.")
                    continue

                # Create new Player instance
                player = Player(summoner_name=summoner_name, tagline=tagline, puuid=puuid)
                db.session.add(player)
                db.session.commit()
            else:
                puuid = player.puuid

            # Fetch the latest match ID
            match_ids = get_match_ids_by_summoner_puuid(puuid, count=1, region=settings.Config.DEFAULT_REGION)
            if not match_ids:
                logging.info(f"No matches found for {summoner_name}#{tagline}")
                continue

            latest_match_id = match_ids[0]

            # Check if the latest match is already processed
            if player.last_match_id == latest_match_id:
                logging.info(f"No new matches for {summoner_name}#{tagline}")
                continue  # Skip to the next player

            # Fetch new matches since the last processed match
            all_match_ids = get_match_ids_by_summoner_puuid(puuid, start=0, count=10, region=settings.Config.DEFAULT_REGION)
            if not all_match_ids:
                logging.info(f"No matches found for {summoner_name}#{tagline}")
                continue

            # Find new matches
            if player.last_match_id:
                try:
                    last_match_index = all_match_ids.index(player.last_match_id)
                    new_match_ids = all_match_ids[:last_match_index]
                except ValueError:
                    # Last match ID not found in the list; process all matches
                    new_match_ids = all_match_ids
            else:
                # No last match ID; process up to 20 matches
                new_match_ids = all_match_ids

            if not new_match_ids:
                logging.info(f"No new matches to process for {summoner_name}#{tagline}")
                continue

            # Limit the number of new matches to process (e.g., max 5)
            new_match_ids = new_match_ids[:10] # Change if API requests grow too large

            # Process new matches
            for match_id in new_match_ids:
                match_data = get_match_data(match_id, region=settings.Config.DEFAULT_REGION)
                if not match_data:
                    continue

                # Verify queue ID (e.g., Flex Ranked 5v5 is queueId 440)
                if match_data.get('info', {}).get('queueId') != 440:
                    logging.info(f"Skipping match {match_id} (non-Flex Ranked 5v5)")
                    continue

                player_stats = get_player_stats_in_match(puuid, match_data)
                if not player_stats:
                    logging.info(f"Player stats not found in match {match_id}")
                    continue

                # Calculate score
                scores = calculate_scores([player_stats])
                score_data = scores[0]
                match_score = score_data['score']

                # Create Match entry
                match = Match(
                    match_id=match_id,
                    player_id=player.id,
                    score=match_score,
                    kills=player_stats.get('kills', 0),
                    deaths=player_stats.get('deaths', 0),
                    assists=player_stats.get('assists', 0),
                    cs=player_stats.get('totalMinionsKilled', 0) + player_stats.get('neutralMinionsKilled', 0),
                    timestamp=datetime.fromtimestamp(match_data['info']['gameEndTimestamp'] / 1000)
                )
                db.session.add(match)

                # Introduce delay between API calls to respect rate limits
                time.sleep(1.2)

            # Commit new matches to the database    
            db.session.commit()

            # Update player's last_match_id
            player.last_match_id = latest_match_id

            # Remove old matches if total exceeds 10
            player_matches = player.matches
            if len(player_matches) > 10:
                matches_to_delete = sorted(player_matches, key=lambda m: m.timestamp)[:-10]
                for old_match in matches_to_delete:
                    db.session.delete(old_match)
                db.session.commit()
                logging.info(f"Deleted {len(matches_to_delete)} old matches for {summoner_name}#{tagline}")

            # Recalculate total_score and average_score based on current matches
            player_matches = player.matches  # Fetch updated matches after deletion
            total_score = sum(match.score for match in player_matches)
            match_count = len(player_matches)

            player.average_score = total_score / match_count if match_count > 0 else 0.0
            player.total_score = total_score
            player.last_updated = datetime.utcnow()
            db.session.commit()

            logging.info(f"Updated {summoner_name}#{tagline}: Average Score={player.average_score}")

            # Introduce delay between players to respect rate limits
            time.sleep(1.2)

        # Update the cached leaderboard data
        leaderboard_entries = Player.query.order_by(Player.average_score.desc()).limit(100).all()
        leaderboard_data = [
            {
                'summoner_name': entry.summoner_name,
                'tagline': entry.tagline,
                'average_score': entry.average_score,
                'last_updated': entry.last_updated.isoformat()
            }
            for entry in leaderboard_entries
        ]
        cache.set('leaderboard_data', leaderboard_data, timeout=300)
        logging.info("Leaderboard data updated and cached.")


# Define Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    logging.info("A client has connected.")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info("A client has disconnected.")

# Run the SocketIO server
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
