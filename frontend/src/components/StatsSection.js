// StatsSection.js
import React, { useEffect, useState } from 'react';
import './StatsSection.css'; // Make sure this file path is correct

const StatsSection = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('https://api.blackultras.com/api/stats')
      .then(response => response.json())
      .then(data => setStats(data))
      .catch(err => console.error('Failed to fetch stats:', err));
  }, []);

  if (!stats) return <div>Loading stats...</div>;

  return (
    <div className="container">
      <div className="grid-container">
        
        {/* Most Kills */}
        <div className="grid-item">
          <div className="stats-section">
            <h2>Most Kills</h2>
            <ol className="ranking-list">
              {stats.most_kills.map((player, index) => (
                <li className="ranking-item" key={index}>
                  {player.summoner_name} - {player.value} kills
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Most Deaths */}
        <div className="grid-item">
          <div className="stats-section">
            <h2>Most Deaths</h2>
            <ol className="ranking-list">
              {stats.most_deaths.map((player, index) => (
                <li className="ranking-item" key={index}>
                  {player.summoner_name} - {player.value} deaths
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Most Assists */}
        <div className="grid-item">
          <div className="stats-section">
            <h2>Most Assists</h2>
            <ol className="ranking-list">
              {stats.most_assists.map((player, index) => (
                <li className="ranking-item" key={index}>
                  {player.summoner_name} - {player.value} assists
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Most CS */}
        <div className="grid-item">
          <div className="stats-section">
            <h2>Most CS</h2>
            <ol className="ranking-list">
              {stats.most_cs.map((player, index) => (
                <li className="ranking-item" key={index}>
                  {player.summoner_name} - {player.value} CS
                </li>
              ))}
            </ol>
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default StatsSection;
