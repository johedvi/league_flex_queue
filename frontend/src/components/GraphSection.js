// components/GraphSection.js
import React, { useState, useEffect } from "react";
import LineChart from "./LineChart";
import './GraphSection.css'; // Optional: For styling purposes

const GraphSection = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // Fetch data from the API endpoint
    fetch("https://api.blackultras.com/api/scores")
      .then((response) => response.json())
      .then((data) => {
        // Process the fetched data to prepare the chart
        const playerScores = data.player_scores; // This is the data from your API

        const labels = Array.from({ length: 10 }, (_, i) => `Game ${i + 1}`); // X-axis: 1 to 10
        const datasets = []; // To store player-specific score datasets

        Object.entries(playerScores).forEach(([playerName, games]) => {
          // Create a dataset for each player
          datasets.push({
            label: playerName, // Player's name
            data: games, // Player's scores
            borderColor: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`,
            backgroundColor: "rgba(0, 0, 0, 0)", // Transparent background
            borderWidth: 2
          });
        });

        // Prepare the chart data
        const chartData = {
          labels, // X-axis labels (1 to 10 for game numbers)
          datasets // Y-axis datasets (scores for each player)
        };

        setChartData(chartData);
      })
      .catch((err) => console.error("Failed to fetch data:", err));
  }, []); // Empty dependency array to ensure the effect runs only once on component mount

  if (!chartData) return <div>Loading chart...</div>;

  return (
    <div className="graph-section">
      <LineChart chartData={chartData} />
    </div>
  );
};

export default GraphSection;
