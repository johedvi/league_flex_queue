// App.js

import React from 'react';
import Header from './components/Header';
import QueueSection from './components/QueueSection';
import SearchSection from './components/SearchSection';
import WheelSection from './components/WheelSection';
import PlayerProfile from './components/PlayerProfile';
import { QueueProvider } from './contexts/QueueContext';
import './App.css'; // Ensure this import is present

function App() {
  return (
    <QueueProvider>
      <div className="App">
        <Header />
        <div className="container">
          {/* Add grid-container div */}
          <div className="grid-container">
            <div className="grid-item">
              <QueueSection />
            </div>
            <div className="grid-item">
              <SearchSection />
            </div>
            <div className="grid-item">
              <WheelSection />
            </div>
            <div className="grid-item">
              <PlayerProfile />
            </div>
          </div>
        </div>
      </div>
    </QueueProvider>
  );
}

export default App;
