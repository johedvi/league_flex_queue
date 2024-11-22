// frontend/src/contexts/QueueContext.js

import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import { io } from 'socket.io-client';
import { BACKEND_URL } from '../config'; // Import BACKEND_URL

// Create the QueueContext
export const QueueContext = createContext();

// Initialize Socket.IO client outside the component to ensure a single instance
const socket = io(BACKEND_URL, {
  transports: ['websocket'], // Force WebSocket transport
  secure: true,              // Ensure secure connection over HTTPS
  reconnectionAttempts: 5,   // Number of reconnection attempts
  timeout: 10000,            // Connection timeout in milliseconds
});

// Create the QueueProvider component
export const QueueProvider = ({ children }) => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch the current queue from the backend
  const fetchQueue = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/queue`);
      setQueue(response.data.queue);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching queue:', err);
      setError('Failed to fetch queue.');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Fetch the initial queue when the provider mounts
    fetchQueue();

    // Listen for 'queue_updated' events from the server
    socket.on('queue_updated', (data) => {
      console.log('Queue updated via WebSocket:', data.queue);
      setQueue(data.queue);
    });

    // Listen for successful connection
    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    // Listen for disconnection
    socket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason);
      if (reason === 'io server disconnect') {
        // The disconnection was initiated by the server, need to reconnect manually
        socket.connect();
      }
    });

    // Handle socket connection errors
    socket.on('connect_error', (err) => {
      console.error('WebSocket connection error:', err);
      setError('WebSocket connection failed.');
    });

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []); // Empty dependency array ensures this runs once on mount

  // Function to add a player to the queue
  const addPlayer = async (playerName) => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/queue`, { player_name: playerName });
      console.log('Add Player Response:', response.data);
      // The queue will update automatically via WebSocket
    } catch (err) {
      console.error('Error adding player to queue:', err);
      throw err.response?.data?.error || new Error('Failed to add player to queue.');
    }
  };

  return (
    <QueueContext.Provider value={{ queue, setQueue, fetchQueue, addPlayer, loading, error }}>
      {children}
    </QueueContext.Provider>
  );
};
