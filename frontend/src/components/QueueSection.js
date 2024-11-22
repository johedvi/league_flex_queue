// frontend/src/components/QueueSection.js

import React, { useContext, useState } from 'react';
import { QueueContext } from '../contexts/QueueContext';
import axios from 'axios';
import './QueueSection.css'; // Optional: For styling purposes
import { BACKEND_URL } from '../config'; // Import BACKEND_URL

const QueueSection = () => {
  // Access queue state and functions from QueueContext
  const { queue, loading, error } = useContext(QueueContext);

  // Local state for the add player form
  const [playerName, setPlayerName] = useState('');
  const [addError, setAddError] = useState(null);
  const [addSuccess, setAddSuccess] = useState(null);

  // Handler for adding a player to the queue
  const handleAddPlayer = async (e) => {
    e.preventDefault();
    setAddError(null);
    setAddSuccess(null);

    if (!playerName.trim()) {
      setAddError('Player name cannot be empty.');
      return;
    }

    try {
      const response = await axios.post(`${BACKEND_URL}/api/queue`, { player_name: playerName.trim() });
      console.log('Add Player Response:', response.data);
      setAddSuccess(response.data.message);
      setPlayerName(''); // Clear the input field
      // The queue will update automatically via WebSocket
    } catch (err) {
      console.error('Error adding player to queue:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setAddError(err.response.data.error);
      } else {
        setAddError('Failed to add player to the queue.');
      }
    }
  };

  return (
    <div className="queue-section">
      <h2>Queue</h2>

      {/* Add Player Form */}
      <form onSubmit={handleAddPlayer} className="add-player-form">
        <input
          type="text"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="Enter Your Name"
          required
        />
        <button type="submit">Join Queue</button>
      </form>

      {/* Display Success or Error Messages */}
      {addSuccess && <p className="success">{addSuccess}</p>}
      {addError && <p className="error">{addError}</p>}

      {/* Display Loading State */}
      {loading ? (
        <p>Loading queue...</p>
      ) : error ? (
        <p className="error">Error: {error}</p>
      ) : (
        <>
          {/* Display the Current Queue */}
          {queue.length > 0 ? (
            <ul className="queue-list">
              {queue.map((player, index) => (
                <li key={index} className="queue-item">
                  {index + 1}. {player}
                </li>
              ))}
            </ul>
          ) : (
            <p>No players in the queue.</p>
          )}
        </>
      )}
    </div>
  );
};

export default QueueSection;
