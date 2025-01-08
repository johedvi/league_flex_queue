# rank_utils.py

import time
import requests
import logging
from riot_api import rate_limited_request  # Reuse if you have this in riot_api.py
from settings import Config

# Maps for converting tier/division to a single numeric
TIER_VALUES = {
    "IRON": 1,
    "BRONZE": 2,
    "SILVER": 3,
    "GOLD": 4,
    "PLATINUM": 5,
    "DIAMOND": 6,
    "MASTER": 7,
    "GRANDMASTER": 8,
    "CHALLENGER": 9
}

DIVISION_VALUES = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4
}

def rank_to_numeric(tier, division):
    """
    Convert Tier + Division to a single integer. Example:
      GOLD III -> tier=4, div=2 -> 4*4 - (2-1) = 15
    """
    tier_value = TIER_VALUES.get(tier.upper(), 0)
    div_value = DIVISION_VALUES.get(division.upper(), 0)
    if tier_value == 0 or div_value == 0:
        # Unranked or unknown
        return None
    numeric_rank = tier_value * 4 - (div_value - 1)
    return numeric_rank


def get_summoner_id_by_puuid(puuid, region=Config.DEFAULT_REGION_CODE):
    """
    Summoner-V4 endpoint to convert from PUUID -> Summoner ID
    GET /lol/summoner/v4/summoners/by-puuid/{puuid}
    """
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    resp = rate_limited_request(url, params={})
    if not resp:
        return None
    data = resp.json()
    return data.get('id')  # This is the Summoner ID used for League-V4 rank calls


def get_ranked_stats_by_summoner_id(summoner_id, region=Config.DEFAULT_REGION_CODE):
    """
    League-V4 endpoint to fetch rank data for a given Summoner ID
    GET /lol/league/v4/entries/by-summoner/{encryptedSummonerId}
    """
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    resp = rate_limited_request(url, params={})
    if not resp:
        return None
    return resp.json()


def fetch_flex_then_solo_rank_numeric(summoner_id, region=Config.DEFAULT_REGION):
    """
    Fetch the RANKED_FLEX_SR tier+division first. If not found, fallback to RANKED_SOLO_5x5.
    Return a numeric rank (or None if unranked in both).
    """
    rank_entries = get_ranked_stats_by_summoner_id(summoner_id, region)
    if not rank_entries:
        return None

    # 1) Try RANKED_FLEX_SR
    flex_entry = next((entry for entry in rank_entries if entry['queueType'] == 'RANKED_FLEX_SR'), None)
    if flex_entry:
        tier = flex_entry.get('tier')
        division = flex_entry.get('rank')
        numeric = rank_to_numeric(tier, division)
        if numeric is not None:
            return numeric

    # 2) Fallback to RANKED_SOLO_5x5
    solo_entry = next((entry for entry in rank_entries if entry['queueType'] == 'RANKED_SOLO_5x5'), None)
    if solo_entry:
        tier = solo_entry.get('tier')
        division = solo_entry.get('rank')
        numeric = rank_to_numeric(tier, division)
        if numeric is not None:
            return numeric

    return None
