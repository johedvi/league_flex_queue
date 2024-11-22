// frontend/src/components/SearchSection.js

import React, { useState, useContext } from 'react';
import axios from 'axios';
import { QueueContext } from '../contexts/QueueContext';
import './SearchSection.css'; // Optional: For styling purposes
import { BACKEND_URL } from '../config'; // Import BACKEND_URL

const SearchSection = () => {
  const [summonerName, setSummonerName] = useState('');
  const [summonerTagline, setSummonerTagline] = useState('');
  const [error, setError] = useState(null);
  const [scores, setScores] = useState([]);
  const [playerToRemove, setPlayerToRemove] = useState(null);
  const [newPlayerAdded, setNewPlayerAdded] = useState(null);

  const { fetchQueue } = useContext(QueueContext); // Access the fetchQueue function

  const handleSearch = async (e) => {
    e.preventDefault();
    setError(null);
    setScores([]);
    setPlayerToRemove(null);
    setNewPlayerAdded(null);

    if (!summonerName.trim() || !summonerTagline.trim()) {
      setError('Both Summoner Name and Tagline are required.');
      return;
    }

    try {
      const response = await axios.get(`${BACKEND_URL}/api/search`, {
        params: {
          summoner_name: summonerName.trim(),
          summoner_tagline: summonerTagline.trim(),
        },
      });

      const data = response.data;
      setScores(data.scores);
      setPlayerToRemove(data.player_to_remove);
      setNewPlayerAdded(data.new_player_added);

      // The queue updates automatically via WebSocket
      // Optionally, you can call fetchQueue() to ensure immediate consistency
      // fetchQueue();
    } catch (err) {
      console.error('Error searching player:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <div className="search-section">
      <h2>Search for a Player</h2>
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={summonerName}
          onChange={(e) => setSummonerName(e.target.value)}
          placeholder="Enter Summoner Name"
          required
        />
        <input
          type="text"
          value={summonerTagline}
          onChange={(e) => setSummonerTagline(e.target.value)}
          placeholder="Enter Summoner Tagline"
          required
        />
        <button type="submit">Search</button>
      </form>

      {/* Display Error Message */}
      {error && <p className="error">{error}</p>}

      {/* Display Scores */}
      {scores.length > 0 && (
        <div className="scores-section">
          <h3>Team Members' Scores</h3>
          <ul className="scores-list">
            {scores.map((score, index) => (
              <li key={index}>
                <strong>{score.summonerName}</strong>: {score.score}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Display Player to Remove */}
      {playerToRemove && (
        <div className="player-remove">
          <h4>
            Player to Remove: {playerToRemove.summonerName} with a score of {playerToRemove.score}
          </h4>
        </div>
      )}

      {/* Display New Player Added */}
      {newPlayerAdded && (
        <div className="new-player-added">
          <h4>New Player Added: {newPlayerAdded}</h4>
        </div>
      )}
    </div>
  );
};

export default SearchSection;
