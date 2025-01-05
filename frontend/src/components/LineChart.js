// LineChart.js
import React from "react";
import { Line } from "react-chartjs-2";
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

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
);

function getRandomColor() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    // Return full opacity (alpha=1). Adjust if you want transparency.
    return `rgba(${r}, ${g}, ${b}, 1)`;
  }

function LineChart({ chartData }) {
  return (
    <div className="chart-container">
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
            legend: { 
              display: true, // Keep the legend
              labels: {
                padding: 20,
                color: 'rgb(255, 255, 255)'
                
            },
              onClick: (e, legendItem, legend) => {
                // Get the chart instance and dataset
                const chart = legend.chart;
                const datasetIndex = legendItem.datasetIndex;
                const dataset = chart.data.datasets[datasetIndex];

                // If we're already highlighting, revert; otherwise highlight
                if (dataset._highlighted) {
                  // Revert to original color/width
                  dataset.borderColor = dataset._originalColor;
                  dataset.borderWidth = dataset._originalBorderWidth;
                  dataset._highlighted = false;
                } else {
                  // Store original color/width if not stored yet
                  if (!dataset._originalColor) {
                    dataset._originalColor = dataset.borderColor;
                  }
                  if (!dataset._originalBorderWidth) {
                    dataset._originalBorderWidth = dataset.borderWidth;
                  }


                  // Apply highlight color/width
                  if (!dataset._highlightColor) {
                    dataset._highlightColor = getRandomColor();
                    
                  }
                  dataset.borderColor = dataset._highlightColor;
                  dataset.borderWidth = 4;
                  dataset._highlighted = true;
                }

                // Update the chart to reflect the change
                chart.update();
              }
            }
          },
          scales: {
            x: {
              type: "category",
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
