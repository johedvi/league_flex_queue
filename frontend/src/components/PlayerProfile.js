import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PlayerProfile.css'; // Ensure this is linked
import { BACKEND_URL } from '../config';

function PlayerProfile() {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);

  const roleIcons = {
    Top: '/toplane-removebg-preview.png',
    Mid: '/midlane-removebg-preview.png',
    Jungle: '/jungle-removebg-preview.png',
    ADC: '/botlane-removebg-preview.png',
    Support: '/support-removebg-preview.png',
    Undefined: '/smaller_question_mark.png',
  };

  useEffect(() => {
    fetchLeaderboardData();
    const interval = setInterval(() => {
      fetchLeaderboardData();
    }, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchLeaderboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/leaderboard`);
      setLeaderboardData(response.data.leaderboard);
    } catch (error) {
      console.error('Error fetching leaderboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-GB'); // Format as DD/MM/YYYY
  };

  // Reverse mapping function to display rank text from numeric value
  const formatRank = (numericRank) => {
    const rankInt = Math.round(numericRank);  
    const tierIndex = Math.floor((rankInt - 1) / 4) + 1;
    const divisionVal = 4 - ((rankInt - 1) % 4);
    const tierNames = {
      1: "Iron", 2: "Bronze", 3: "Silver", 4: "Gold",
      5: "Platinum", 6: "Diamond", 7: "Master", 8: "Grandmaster", 9: "Challenger"
    };
    const divisionNames = {1:"I", 2:"II", 3:"III", 4:"IV"};
    const tierName = tierNames[tierIndex] || "Unknown";
    const divisionName = divisionNames[divisionVal] || "";
    return `${tierName} ${divisionName}`;
  };

  if (loading) {
    return <div>Loading statistics...</div>;
  }

  return (
    <div className="player-profile">
      <h2>Leaderboard - 10 latest flex</h2>
      <ul>
        {leaderboardData.map((player, index) => (
          <li key={player.summoner_name} className="player-item">
            <div className="player-row">
            <div className="player-header">
              <span className="player-rank">{index + 1}.</span>
              <span className="player-name">{player.summoner_name}:</span>
              <span className="player-score">
                {player.average_score.toFixed(2)} points
              </span>
            <div className="player-avatar-container">
            <span className="player-average-opponent-rank">
            <strong>Avg Lane Rank:</strong>{' '}
                {player.average_opponent_rank !== null
              ? `${formatRank(player.average_opponent_rank)}`: 'N/A'}
    </span>
    <span className="player-avatar-text">Most played:</span>
    <img
      src={roleIcons[player.most_played_role] || roleIcons.Undefined}
      alt={`${player.most_played_role} icon`}
      className="player-avatar "
    />
  </div>
</div>
              <div className="player-last-updated">
                Last Updated: {formatDate(player.last_updated)}{' '}
                {formatTime(player.last_updated)}
              </div>
            </div>
            <div className="player-stats">
              <span className="player-stat player-highest-score">
                <strong>Highest Score (All-time):</strong>{' '}
                {player.highest_score ? player.highest_score.toFixed(2) : 'N/A'}
              </span>
              <span className="player-stat player-lowest-score">
                <strong>Lowest Score (All-time):</strong>{' '}
                {player.lowest_score ? player.lowest_score.toFixed(2) : 'N/A'}
              </span>
              <span className="player-stat player-tenth-game-score">
                <strong>10th Game Score:</strong>{' '}
                {player.tenth_game_score ? player.tenth_game_score.toFixed(2) : 'N/A'}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PlayerProfile;
