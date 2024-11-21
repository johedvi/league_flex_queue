import React from 'react';
import Header from './components/Header';
import QueueSection from './components/QueueSection';
import SearchSection from './components/SearchSection';
import WheelSection from './components/WheelSection';
import './App.css'; // Import global styles
import { QueueProvider } from './contexts/QueueContext';

function App() {
  return (
    <QueueProvider>
      <div className="App">
        <Header />
        <div className="container">
          <QueueSection />
          <SearchSection />
          <WheelSection />
        </div>
      </div>
    </QueueProvider>
  );
}

export default App;
