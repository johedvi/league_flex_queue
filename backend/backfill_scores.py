from app import app, db
from models import Player, Match

with app.app_context():
    players = Player.query.all()  # Get all players

    for player in players:
        matches = Match.query.filter_by(player_id=player.id).all()

        if matches:
            # Calculate highest and lowest scores
            highest_score = max([match.score for match in matches])
            lowest_score = min([match.score for match in matches])

            # Update player fields
            player.all_time_highest_score = highest_score
            player.all_time_lowest_score = lowest_score

            print(f"Updated {player.summoner_name}: Highest = {highest_score}, Lowest = {lowest_score}")
        else:
            # If no matches, leave fields unchanged
            print(f"No matches found for {player.summoner_name}, skipping.")

    # Commit the changes to the database
    db.session.commit()
    print("Backfill completed!")
