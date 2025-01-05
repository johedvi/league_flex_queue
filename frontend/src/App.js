import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';          // Your existing header/title component
import HeaderNav from './components/HeaderNav';    // The new navigation header
import QueueSection from './components/QueueSection';
import SearchSection from './components/SearchSection';
import WheelSection from './components/WheelSection';
import PlayerProfile from './components/PlayerProfile';
import StatsSection from './components/StatsSection';
import GraphSection from './components/GraphSection';
import { QueueProvider } from './contexts/QueueContext';
import './App.css';

function App() {
  return (
    <QueueProvider>
      <Router>
        <div className="App">
          <Header />
          <HeaderNav /> {/* The newly styled header with buttons/links */}
          <Routes>
            <Route 
              path="/" 
              element={
                <div className="container">
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
              }
            />
            <Route path="/stats" element={<StatsSection />} />
            <Route path="/graphs" element={<GraphSection/>} />

          </Routes>
        </div>
      </Router>
    </QueueProvider>
  );
}

export default App;