// components/GraphSection.js
import React, { useState, useEffect } from "react";
import { Bar } from 'react-chartjs-2';
import Chart from 'chart.js/auto'; // Importing Chart.js
import './AttendanceSection.css'; // Importing the CSS file



const EventAttendanceHistogram = () => {
  const attendees = {
    '20-12-2024': [
      { name: 'Johan', role: 'Player' },
      { name: 'Ola', role: 'Spectator' },
      { name: 'Barto', role: 'Spectator' },
      { name: 'Pide', role: 'Spectator' },
      { name: 'Fille', role: 'Spectator' },
      { name: 'Päron', role: 'Spectator' },
      { name: 'Alex', role: 'Spectator' },
      { name: 'Bajsveck', role: 'Spectator' },
      { name: 'Jonte', role: 'Spectator' },
      { name: 'Viking', role: 'Spectator' },
      { name: 'Chubbe', role: 'Spectator' }
    ],
    '25-12-2024': [
      { name: 'Barto', role: 'Spectator' },
      { name: 'Viking', role: 'Spectator' },
      { name: 'Kisse', role: 'Spectator' },
      { name: 'Gurra', role: 'Spectator' },
      { name: 'Alex', role: 'Spectator' },
      { name: 'Bajsveck', role: 'Spectator' },
      { name: 'Johan', role: 'Player' },
      { name: 'Jonte', role: 'Spectator' },
      { name: 'Päron', role: 'Spectator' },
      { name: 'Ola', role: 'Spectator' },
    ]
  };


  // Count the number of events each person attended
  const attendeeCount = {};
  Object.values(attendees).forEach(eventAttendees => {
    eventAttendees.forEach(attendee => {
      if (attendeeCount[attendee.name]) {
        attendeeCount[attendee.name]++;
      } else {
        attendeeCount[attendee.name] = 1;
      }
    });
  });

  // Prepare the data for the histogram
  const names = Object.keys(attendeeCount);
  const counts = names.map(name => attendeeCount[name]);

  // Sort the names alphabetically
  const sortedNames = names.sort();

  // Create the chart data with sorted names
  const sortedCounts = sortedNames.map(name => attendeeCount[name]);

  const data = {
    labels: sortedNames, // Sorted names on the X-axis
    datasets: [
      {
        data: sortedCounts, // Number of events attended per person
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }
    ]
  };

  const options = {
    scales: {
      y: {
        ticks: {
          stepSize: 1, // Force the y-axis to increment by 1
          beginAtZero: true, // Start the y-axis at 0
        },
      },
    },
    plugins: {
      legend: {
        display: false, // Hides the legend
      },
    },
  };

  return (
    <div className="Attendance-wrapper">
      <div className="Attendance-container">
        <h1>Event Attendance</h1>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default EventAttendanceHistogram;
