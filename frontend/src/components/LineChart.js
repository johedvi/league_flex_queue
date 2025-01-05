import React from "react";
import { Line } from "react-chartjs-2";
import './GraphSection.css'; // Optional: For styling purposes
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from "chart.js";

// Register the necessary Chart.js components
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
);

function LineChart({ chartData }) {
  return (
    <div className="chart-container">
      <h2 style={{ textAlign: "center" }}>Player Scores Over 10 Games</h2>
      <Line
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: "Player Scores Over 10 Games",
              font: { size: 18 }
            },
            legend: { display: true }
          },
          layout: {
            padding: {
              top: 20, // Increased padding to avoid clipping
              left: 20,
              right: 20,
              bottom: 20
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: "Game Number",
                font: { size: 14 }
              }
            },
            y: {
              title: {
                display: true,
                text: "Score",
                font: { size: 14 }
              },
              beginAtZero: true
            }
          }
        }}
      />
    </div>
  );
}

export default LineChart;
