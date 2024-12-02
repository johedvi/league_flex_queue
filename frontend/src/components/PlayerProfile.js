// src/components/PlayerProfile.js

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PlayerProfile.css'; // Optional: For styling purposes
import { BACKEND_URL } from '../config'; // Ensure this is set

function PlayerProfile() {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div>Loading statistics...</div>;
  }

  return (
    <div className="player-profile">
      <h2>(Snitt 10 senaste flex games)</h2>
      <ul>
        {leaderboardData.map((player, index) => (
          <li key={player.puuid}>
            {index + 1}. {player.summoner_name}: {player.average_score.toFixed(2)} points
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PlayerProfile;
