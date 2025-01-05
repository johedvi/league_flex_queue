// components/GraphSection.js
import React, { useState, useEffect } from "react";
import LineChart from "./LineChart";
import './GraphSection.css'; // Optional: For styling purposes

const GraphSection = () => {
  // 1) Keep the raw player scores here once fetched
  const [allPlayerScores, setAllPlayerScores] = useState({});
  // 2) Build the chart data separately
  const [chartData, setChartData] = useState(null);

  // 3) This state tracks which players are selected
  const [selectedPlayers, setSelectedPlayers] = useState([]);

  // Fetch data ONCE
  useEffect(() => {
    fetch("https://api.blackultras.com/api/scores")
      .then((response) => response.json())
      .then((data) => {
        // `data.player_scores` is presumably an object: { playerName: [scores...] }
        setAllPlayerScores(data.player_scores);
      })
      .catch((err) => console.error("Failed to fetch data:", err));
  }, []);

  // Whenever `allPlayerScores` or `selectedPlayers` changes, build fresh chartData
  useEffect(() => {
    if (!allPlayerScores || Object.keys(allPlayerScores).length === 0) {
      return;
    }

    // For x-axis labels "Game 1" through "Game 10"
    const labels = Array.from({ length: 10 }, (_, i) => `Game ${i + 1}`);

    // Build the datasets array
    const datasets = Object.entries(allPlayerScores).map(([playerName, scores]) => {
      const isSelected = selectedPlayers.includes(playerName);
      return {
        label: playerName,
        data: scores,
        borderColor: isSelected ? 'rgba(255,99,132,1)' : 'rgba(169,169,169,1)',
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderWidth: isSelected ? 3 : 1,
        fill: false,
      };
    });

    setChartData({
      labels,
      datasets
    });
  }, [allPlayerScores, selectedPlayers]);

  // Toggle player selection
  const handlePlayerSelection = (playerName) => {
    setSelectedPlayers((prevSelectedPlayers) =>
      prevSelectedPlayers.includes(playerName)
        ? prevSelectedPlayers.filter((name) => name !== playerName)
        : [...prevSelectedPlayers, playerName]
    );
  };

  if (!chartData) return <div>Loading chart...</div>;

  // 4) We can safely map over chartData.datasets to create buttons
  return (
    <div className="graph-section">

      <LineChart chartData={chartData} />
    </div>
  );
};

export default GraphSection;
