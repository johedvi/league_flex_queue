import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import HeaderNav from './components/HeaderNav';
import QueueSection from './components/QueueSection';
import SearchSection from './components/SearchSection';
import WheelSection from './components/WheelSection';
import PlayerProfile from './components/PlayerProfile';
import StatsSection from './components/StatsSection';
import GraphSection from './components/GraphSection';
import AttendanceSection from './components/AttendanceSection';
import { QueueProvider } from './contexts/QueueContext';
import './App.css';

function App() {
  useEffect(() => {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      console.error('Adsense error', e);
    }
  }, []);

  return (
    <QueueProvider>
      <Router>
        <div className="App">
          <Header />
          <HeaderNav />
          {/* Ad Unit at the top */}
          <div className="ad-container">
            <ins
              className="adsbygoogle"
              style={{ display: 'block' }}
              data-ad-client="ca-pub-2416565727603168"
              data-ad-slot="1234567890" /* Replace with your Ad Slot ID */
              data-ad-format="auto"
              data-full-width-responsive="true"
            ></ins>
          </div>
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
            <Route path="/graphs" element={<GraphSection />} />
            <Route path="/attendance" element={<AttendanceSection />} />
          </Routes>
        </div>
      </Router>
    </QueueProvider>
  );
}

export default App;
