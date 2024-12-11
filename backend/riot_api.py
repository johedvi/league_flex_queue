# riot_api.py
import settings
import requests
import math
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

ROLE_WEIGHTS = {
    'Top': {'kills': 3, 'deaths': -2.5, 'assists': 1, 'csPerMin': 2.5, 'visionScore': 0.5,'totalDamage': 3},
    'Mid': {'kills': 2.5, 'deaths': -2, 'assists': 1.5, 'csPerMin': 2, 'visionScore': 1,'totalDamage': 3},
    'Jungle': {'kills': 2, 'deaths': -2, 'assists': 2, 'csPerMin': 2, 'visionScore': 1.5,'totalDamage': 2.5},
    'ADC': {'kills': 3.5, 'deaths': -3, 'assists': 0.5, 'csPerMin': 2.5, 'visionScore': 0.5,'totalDamage': 3},
    'Support': {'kills': 1, 'deaths': -1, 'assists': 4.5, 'csPerMin': 0.5, 'visionScore': 3,'totalDamage': 1},
    'Undefined': {'kills': 4, 'deaths': -2, 'assists': 2, 'csPerMin': 2, 'visionScore': 1,'totalDamage': 3}
}

AGGRESSIVE_SUPPORTS = ["Pyke","Malphite","Brand", "Senna","Xerath","Lux","Vel'koz","Camille","Pantheon","Singed","Hwei","Teemo","Shaco","Swain"]

class RateLimiter:
    def __init__(self, max_requests, period):
        self.max_requests = max_requests  # Maximum requests allowed
        self.period = period  # Time period in seconds
        self.requests = []
    
    def wait(self):
        current_time = time.time()
        # Remove requests that are outside the period
        self.requests = [req_time for req_time in self.requests if req_time > current_time - self.period]
        if len(self.requests) >= self.max_requests:
            # Calculate the time to wait
            sleep_time = self.period - (current_time - self.requests[0])
            print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
            # After sleeping, remove the oldest request
            self.requests.pop(0)
        # Record the new request
        self.requests.append(time.time())

# Initialize the rate limiters
short_term_limiter = RateLimiter(max_requests=20, period=1)      # 20 requests per 1 second
long_term_limiter = RateLimiter(max_requests=100, period=120)    # 100 requests per 120 seconds

def rate_limited_request(url, params, retries=3):
    headers = {'X-Riot-Token': settings.Config.API_KEY}
    for attempt in range(retries):
        try:
            # Wait if necessary
            short_term_limiter.wait()
            long_term_limiter.wait()
            # Make the request
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                # Rate limit exceeded, wait and retry
                retry_after = int(response.headers.get('Retry-After', 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
            else:
                print(f"HTTP error: {e}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {e}")
            break
    return None

def get_summoner_info(summoner_name=None, summoner_tagline=None, region=settings.Config.DEFAULT_REGION):
    if not summoner_name:
        summoner_name = input("Summoner name: ")
    if not summoner_tagline:
        summoner_tagline = input("Summoner tagline: ")

    params = {}
    api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tagline}"

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting summoner data from API: {e}')
        return None

def get_match_ids_by_summoner_puuid(summoner_puuid, start=0, count=10, queue=440, region=settings.Config.DEFAULT_REGION):
    params = {
        'start': start,
        'count': count,
        'queue': queue  # Only fetch matches from queueId 440 (Flex Ranked 5v5)
    }
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids"

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting summoner match data from API: {e}')
        return None

def did_player_win_match(summoner_puuid, match_id, region=settings.Config.DEFAULT_REGION):
    params = {}
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        match_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting match data from match ID from API: {e}')
        return None

    if summoner_puuid in match_data['metadata']['participants']:
        player_index = match_data['metadata']['participants'].index(summoner_puuid)
    else:
        return None

    player_info = match_data['info']['participants'][player_index]
    return player_info['win']

def get_recent_match_id(puuid, region=settings.Config.DEFAULT_REGION):
    """Fetches the most recent match ID for the given PUUID."""
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        'start': 0,
        'count': 1,
    }

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        match_ids = response.json()
        if match_ids:
            return match_ids[0]
    except requests.exceptions.RequestException as e:
        print(f'Issue getting recent match ID: {e}')
    return None

def get_team_members(puuid, match_id, region=settings.Config.DEFAULT_REGION):
    """Gets all team members for the given match."""
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    params = {}

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        match_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue fetching match details: {e}')
        return None

    participants = match_data['info']['participants']
    # Identify team ID of the player
    team_id = None
    for participant in participants:
        if participant['puuid'] == puuid:
            team_id = participant['teamId']
            break

    if not team_id:
        return None

    # Return all team members
    team_members = [p for p in participants if p['teamId'] == team_id]
    return team_members


def get_support_weights(champion_name):
    """Adjust support weights dynamically based on champion playstyle."""
    if champion_name in AGGRESSIVE_SUPPORTS:
        return {'kills': 3, 'deaths': -1, 'assists': 2.5, 'csPerMin': 0.5, 'visionScore': 3,'totalDamage': 1}
    else:
        return {'kills': 1, 'deaths': -1, 'assists': 4.5, 'csPerMin': 0.5, 'visionScore': 3,'totalDamage': 1}

def get_role_weights(role, champion_name=None):
    """Fetch weights for a given role, with dynamic support adjustments."""
    if role == 'Support' and champion_name:
        return get_support_weights(champion_name)
    return ROLE_WEIGHTS.get(role, ROLE_WEIGHTS['Undefined'])

def assign_roles_by_team_position(team_members):
    """Assign roles using the teamPosition field from the Riot API."""
    for member in team_members:
        # Use the teamPosition field directly
        team_position = member.get('teamPosition', 'UNKNOWN')

        # Map teamPosition to a human-readable role
        if team_position == "TOP":
            member['assignedRole'] = "Top"
        elif team_position == "JUNGLE":
            member['assignedRole'] = "Jungle"
        elif team_position == "MIDDLE":
            member['assignedRole'] = "Mid"
        elif team_position == "BOTTOM":
            member['assignedRole'] = "ADC"
        elif team_position == "UTILITY":
            member['assignedRole'] = "Support"
        else:
            member['assignedRole'] = "Undefined"  # Handle edge cases

    return team_members

def calculate_scores(team_members):
    """Calculates individual scores for a team based on assigned roles."""
    import math
    match_scores = []

    # Assign roles to team members using teamPosition
    team_members = assign_roles_by_team_position(team_members)

    for member in team_members:
        # Retrieve assigned role and weights
        role = member.get('assignedRole', 'Undefined')
        champion_name = member.get('championName', None)  # Optional: Fetch champion name
        weights = get_role_weights(role, champion_name)

        # Fetch performance metrics
        kills = member.get('kills', 0)
        deaths = member.get('deaths', 0)
        assists = member.get('assists', 0)
        cs = member.get('totalMinionsKilled', 0) + member.get('neutralMinionsKilled', 0)  # Calculate CS
        vision_score = member.get('visionScore', 0)
        total_damage = member.get('totalDamageDealtToChampions', 0)

        game_duration = match_data['info'].get('gameDuration', 0)
        game_duration = game_duration/60
        cs_per_min = cs/game_duration


        # Apply scaling to metrics
        scaled_kills = math.erf(30 / (10 * game_duration) * kills)
        scaled_deaths = math.erf(30 / (10 * game_duration) * deaths)
        scaled_assists = math.erf(30 / (10 * game_duration) * assists)
        scaled_cs_min = math.erf(1 / 5 * cs_per_min) 
        scaled_vision = math.erf(30 / (50 * game_duration) * vision_score)
        scaled_total_damage = math.erf(30 / (30000 * game_duration) * total_damage)


        # Calculate the score using role-specific weights
        base_score = (
            weights['kills'] * scaled_kills +
            weights['deaths'] * scaled_deaths +
            weights['assists'] * scaled_assists +
            weights['csPerMin'] * scaled_cs_min +
            weights['visionScore'] * scaled_vision +
            weights['totalDamage'] * scaled_total_damage
        )

        # Round the score to 2 decimal places
        rounded_score = round(base_score, 2)

        # Append the calculated score with details
        match_scores.append({
            'summonerName': member.get('summonerName', 'Unknown'),
            'role': role,
            'score': rounded_score,
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'csPerMin': round(cs_per_min, 2),
            'visionScore': vision_score,
            'totalDamage': round(total_damage, 2)
        })

    return match_scores

# New methods

def get_match_data(match_id, region=settings.Config.DEFAULT_REGION):
    """Fetches match data given a match ID."""
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    params = {}

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue fetching match data: {e}')
        return None

def get_player_stats_in_match(puuid, match_data, team_only=False):
    """Extracts player's performance stats from match data."""
    participants = match_data['info']['participants']
    player_stats = None
    player_team_id = None

    for participant in participants:
        if participant['puuid'] == puuid:
            player_stats = participant
            player_team_id = participant.get('teamId')
            break

    if player_stats is None:
        logging.error("Player stats not found in match data.")
        return None

    if team_only:
        team_members = [p for p in participants if p.get('teamId') == player_team_id]
        return team_members
    else:
        return player_stats

def get_player_aggregated_score(puuid, match_count=10, region=settings.Config.DEFAULT_REGION):
    """Fetches the latest matches for a player and aggregates their scores."""
    match_ids = get_match_ids_by_summoner_puuid(puuid, count=match_count, region=region)
    if not match_ids:
        print(f"No matches found for PUUID {puuid}")
        return 0

    total_score = 0
    processed_matches = 0
    for match_id in match_ids:
        match_data = get_match_data(match_id, region=region)
        if not match_data:
            continue  # Skip if match data couldn't be retrieved

        # Verify that the match is of queueId 440
        if match_data.get('info', {}).get('queueId') != 440:
            continue  # Skip matches that are not Flex Ranked 5v5

        player_stats = get_player_stats_in_match(puuid, match_data)
        if not player_stats:
            continue  # Skip if player stats couldn't be found

        scores = calculate_scores([player_stats])
        score = scores[0]['score']  # Extract the score from the result

        total_score += score
        processed_matches += 1

    if processed_matches == 0:
        return 0

    average_score = total_score / processed_matches
    print(f"Processed {processed_matches} matches for PUUID {puuid}")
    return round(average_score, 2)

def create_leaderboard(player_list, match_count=10, region=settings.Config.DEFAULT_REGION):
    """Creates a leaderboard by aggregating scores for a list of players.

    player_list: list of tuples (summoner_name, summoner_tagline)
    """
    leaderboard = []
    for player_name, player_tagline in player_list:
        # Fetch PUUID for the player
        summoner_info = get_summoner_info(
            summoner_name=player_name,
            summoner_tagline=player_tagline,
            region=region
        )
        if not summoner_info:
            print(f"Could not retrieve summoner info for {player_name}")
            continue

        puuid = summoner_info.get('puuid')
        if not puuid:
            print(f"No PUUID found for {player_name}")
            continue

        total_score = get_player_aggregated_score(
            puuid,
            match_count=match_count,
            region=region
        )
        leaderboard.append({'summonerName': player_name, 'totalScore': total_score})

    # Sort the leaderboard by total score in descending order
    leaderboard.sort(key=lambda x: x['totalScore'], reverse=True)
    return leaderboard

# Example usage:
if __name__ == "__main__":
    # List of player names and taglines to include in the leaderboard
    """
    Search for a player and calculate team scores.
    """
    summoner_name = 'bajveck'
    summoner_tagline = 'EUNE'

    # Fetch player PUUID
    player_info = get_summoner_info(summoner_name, summoner_tagline, region=settings.Config.DEFAULT_REGION)

    puuid = player_info.get('puuid')

    # Fetch recent match ID
    match_id = get_recent_match_id(puuid, region=settings.Config.DEFAULT_REGION)

    # Fetch team members
    match_data = get_match_data(match_id, region=settings.Config.DEFAULT_REGION)

    team_members = get_player_stats_in_match(puuid, match_data, team_only=True)

    # Calculate scores
    scores = calculate_scores(team_members)

    # Identify the player with the lowest score
    scores_sorted = sorted(scores, key=lambda x: x['score'])
    player_to_remove = scores_sorted[0] if scores_sorted else None

for score in scores_sorted:
    print(score)
    print()




