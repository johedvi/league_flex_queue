# riot_api.py
import settings
import requests
import math
import time
from urllib.parse import urlencode

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
    for attempt in range(retries):
        try:
            # Wait if necessary
            short_term_limiter.wait()
            long_term_limiter.wait()
            # Make the request
            response = requests.get(url, params=params)
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

    params = {'api_key': settings.Config.API_KEY}
    api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tagline}"

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting summoner data from API: {e}')
        return None

def get_match_ids_by_summoner_puuid(summoner_puuid, match_count=1, region=settings.Config.DEFAULT_REGION):
    params = {
        'api_key': settings.Config.API_KEY,
        'count': match_count,
        'queue': 440  # Only fetch matches from queueId 440 (Flex Ranked 5v5)
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
    params = {'api_key': settings.Config.API_KEY}
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
        'api_key': settings.Config.API_KEY,
        'start': 0,
        'count': 1,
        'queue': 440  # Only fetch matches from queueId 440
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
    params = {'api_key': settings.Config.API_KEY}

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

def calculate_scores_v1(team_members):
    """Calculates individual scores for a team based on match performance."""
    scores = []
    for member in team_members:
        kills = member.get('kills', 0)
        deaths = member.get('deaths', 0)
        assists = member.get('assists', 0)
        cs = member.get('totalMinionsKilled', 0) + member.get('neutralMinionsKilled', 0)

        # Example scoring formula
        score = (kills * 2 + assists - deaths * 1.5 + cs * 0.1)
        scores.append({'summonerName': member.get('summonerName', 'Unknown'), 'score': score})

    return scores

def calculate_scores(team_members):
    """Calculates individual scores for a team based on match performance."""
    match_scores = []
    w = {'kills': 4, 'deaths': -2, 'assists': 2, 'cs': 2}
    target_name = 'lil newton'  # Lowercase target name for comparison

    for member in team_members:
        summoner_name = member.get('summonerName', 'Unknown')
        is_lil_newton = summoner_name.lower() == target_name

        kills = member.get('kills', 0)
        deaths = member.get('deaths', 0)
        assists = member.get('assists', 0)
        cs = member.get('totalMinionsKilled', 0) + member.get('neutralMinionsKilled', 0)

        # Apply scaling
        scaled_kills = math.erf(1/10 * kills)
        scaled_deaths = math.erf(1/10 * deaths)
        scaled_assists = math.erf(1/10 * assists)
        scaled_cs = math.erf(1/200 * cs)

        # Calculate the score
        base_score = (
            w['kills'] * scaled_kills +
            w['assists'] * scaled_assists +
            w['deaths'] * scaled_deaths +
            w['cs'] * scaled_cs
        )

        if is_lil_newton:
            adjusted_score = base_score - 3
        else:
            adjusted_score = base_score

        rounded_score = round(adjusted_score, 2)

        match_scores.append({
            'summonerName': summoner_name,
            'score': rounded_score,
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'cs': cs,
            'matchId': member.get('matchId'),
            'timestamp': member.get('timestamp')
        })

    return match_scores


# New methods

def get_match_data(match_id, region=settings.Config.DEFAULT_REGION):
    """Fetches match data given a match ID."""
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    params = {'api_key': settings.Config.API_KEY}

    try:
        response = rate_limited_request(api_url, params)
        if response is None:
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue fetching match data: {e}')
        return None

def get_player_stats_in_match(puuid, match_data):
    """Extracts player's performance stats from match data."""
    participants = match_data['info']['participants']
    for participant in participants:
        if participant['puuid'] == puuid:
            return participant
    return None

def get_player_aggregated_score(puuid, match_count=20, region=settings.Config.DEFAULT_REGION):
    """Fetches the latest matches for a player and aggregates their scores."""
    match_ids = get_match_ids_by_summoner_puuid(puuid, match_count=match_count, region=region)
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

def create_leaderboard(player_list, match_count=5, region=settings.Config.DEFAULT_REGION):
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
    player_list = [
        ('bigbrainburton', 'EUNE'),
        ('lil newton', 'EUNE'),
        # Add more players as needed
    ]

    # Create the leaderboard
    leaderboard = create_leaderboard(player_list, match_count=20)

    # Display the leaderboard
    print("Leaderboard:")
    for rank, entry in enumerate(leaderboard, start=1):
        print(f"{rank}. {entry['summonerName']}: {entry['totalScore']} points")
