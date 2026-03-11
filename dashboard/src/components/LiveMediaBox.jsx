import React, { useState, useEffect } from 'react';

// YouTube Live Stream IDs for the requested channels
const CHANNELS = [
  { name: 'Associated Press', id: 'uw_liwLvfVg' },
  { name: 'Al Jazeera', id: 'gCNeDWCI0vo' },
  { name: 'Sky News', id: '9Auq9mYxFEE' },
  { name: 'Fox News', id: 's0HwD2Btoew' },
  { name: 'RT News', id: 'O3DpJVONybc' },
  { name: 'CNN (News18)', id: '4E0b60K9kWM' }
];

const LiveMediaBox = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    // Cycle exactly every 60 seconds
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % CHANNELS.length);
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const currentChannel = CHANNELS[currentIndex];

  return (
    <div style={{
      position: 'absolute',
      bottom: '16px',
      right: '16px',
      width: '320px',
      background: 'rgba(10, 14, 18, 0.9)',
      border: '1px solid var(--color-cyan-dim)',
      boxShadow: '0 0 15px rgba(0,0,0,0.8)',
      borderRadius: '4px',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <div style={{ 
        padding: '6px 12px', 
        borderBottom: '1px solid #1A1A1A', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: 'rgba(0,0,0,0.8)'
      }}>
        <div className="text-cyan font-mono" style={{ fontSize: '0.65rem', letterSpacing: '1px', fontWeight: 'bold' }}>
          ● LIVE FEED: <span style={{ color: '#FFF' }}>{currentChannel.name.toUpperCase()}</span>
        </div>
        <div className="text-red glow-red font-mono" style={{ fontSize: '0.6rem', fontWeight: 'bold' }}>
          LIVE
        </div>
      </div>
      
      {/* 
        youtube embed constraints:
        controls=1 (allows user to unmute/mute) 
        autoplay=1&mute=1 (required to auto-play when rotating feeds without user interaction blocking it)
       */}
      <div style={{ width: '100%', height: '180px', background: '#000' }}>
        <iframe
          key={currentChannel.id} // forces reload when id changes
          width="100%"
          height="100%"
          src={`https://www.youtube.com/embed/${currentChannel.id}?autoplay=1&mute=1&controls=1`}
          title={`${currentChannel.name} Live`}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      </div>
    </div>
  );
};

export default LiveMediaBox;
