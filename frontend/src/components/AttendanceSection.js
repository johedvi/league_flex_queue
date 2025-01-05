// components/GraphSection.js
import React, { useState, useEffect } from "react";
import { Bar } from 'react-chartjs-2';
import Chart from 'chart.js/auto'; // Importing Chart.js

const EventAttendanceHistogram = () => {
  const attendees = [
    { name: 'John Doe', event: 'Football Match' },
    { name: 'Jane Smith', event: 'Football Match' },
    { name: 'Alex Johnson', event: 'Concert' },
    { name: 'Mary Lee', event: 'Concert' },
    { name: 'Robert Brown', event: 'Wedding' },
    { name: 'Lucy Davis', event: 'Wedding' },
    { name: 'Michael White', event: 'Art Exhibit' },
    { name: 'Emma Clark', event: 'Art Exhibit' },
    { name: 'James Wilson', event: 'Workshop' },
    { name: 'Olivia Martinez', event: 'Workshop' },
    { name: 'John Doe', event: 'Wedding' }, // John attends multiple events
    { name: 'Alex Johnson', event: 'Workshop' } // Alex attends multiple events
  ];

  // Count how many events each person attended
  const eventCounts = attendees.reduce((acc, { name }) => {
    acc[name] = (acc[name] || 0) + 1;
    return acc;
  }, {});

  // Prepare data for the chart
  const data = {
    labels: Object.keys(eventCounts), // Names of the attendees
    datasets: [
      {
        label: 'Number of Events Attended',
        data: Object.values(eventCounts), // The number of events each person attended
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }
    ]
  };

  return (
    <div>
      <h1>Event Attendance Histogram</h1>
      <Bar data={data} />
    </div>
  );
};

export default EventAttendanceHistogram;

