# riot_api.py
import settings
import requests
import math
from urllib.parse import urlencode

def get_summoner_info(summoner_name=None, summoner_tagline=None, region=settings.Config.DEFAULT_REGION):
    if not summoner_name:
        summoner_name = input("Summoner name: ")
    
    if not summoner_tagline:
        summoner_tagline = input("Summoner tagline: ")
    
    params = {'api_key': settings.Config.API_KEY}
    # Ensure the region code is correct
    api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tagline}"
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting summoner data from API: {e}')
        return None

def get_match_ids_by_summoner_puuid(summoner_puuid, matches_count=1, region=settings.Config.DEFAULT_REGION):
    params = {'api_key': settings.Config.API_KEY, 'count': matches_count}
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids"
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Issue getting summoner match data from API: {e}')
        return None

def did_player_win_match(summoner_puuid, match_id, region=settings.Config.DEFAULT_REGION):
    params = {'api_key': settings.Config.API_KEY}
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
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
    params = {'api_key': settings.Config.API_KEY, 'start': 0, 'count': 1}
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
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
        response = requests.get(api_url, params=params)
        response.raise_for_status()
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

import settings
import requests
import math
from urllib.parse import urlencode

def calculate_scores(team_members):
    """Calculates individual scores for a team based on match performance.
    
    Players named 'Lil Newton' receive a flat score of -3.
    """
    scores = []
    w = {'kills': 4, 'deaths': -2, 'assists': 2, 'cs': 2}
    for member in team_members:
        summoner_name = member.get('summonerName', 'Unknown')
        
        # Check if the summoner is 'Lil Newton' (case-insensitive)
        if summoner_name.lower() == 'lil newton':
            score = -3
        else:
            kills = member.get('kills', 0)
            deaths = member.get('deaths', 0)
            assists = member.get('assists', 0)
            cs = member.get('totalMinionsKilled', 0) + member.get('neutralMinionsKilled', 0)

            # Apply sigmoid-like scaling using the error function
            scaled_kills = math.erf(1/10 * kills)
            scaled_deaths = math.erf(1/10 * deaths)
            scaled_assists = math.erf(1/10 * assists)
            scaled_cs = math.erf(1/200 * cs)
            
            # Calculate the score based on weighted metrics
            score = (
                w['kills'] * scaled_kills +
                w['assists'] * scaled_assists +
                w['deaths'] * scaled_deaths +
                w['cs'] * scaled_cs
            )
        
        scores.append({'summonerName': summoner_name, 'score': score})
    
    return scores

