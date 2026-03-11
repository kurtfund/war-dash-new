import React, { useState, useEffect, useRef } from 'react';

// YouTube Live Stream Channel IDs for the requested networks
// Using permanent Channel IDs instead of volatile Video IDs ensures the stream never breaks.
const CHANNELS = [
  { name: 'AL JAZEERA', id: 'UCfiwzLy-8yKzIbsmZTzxDWA' },
  { name: 'SKY NEWS', id: 'UCoMdktPbSTqxWQVHs7BpYTg' },
  { name: 'CNN NEWS18', id: 'UC8X6_v8-1GIP9B3T-Lh-45Q' },
  { name: 'FOX (LNOW)', id: 'sIv6YmBeO3Q' },
  { name: 'DW NEWS', id: 'LuKwFajn37U' },
  { name: 'ASSOCIATED PRESS', id: 'uw_liwLvfVg' }
];

const LiveMediaBox = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const timerRef = useRef(null);

  const startAutoCycle = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % CHANNELS.length);
    }, 60000);
  };

  useEffect(() => {
    startAutoCycle();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const handleManualCycle = (direction) => {
    if (direction === 'next') {
      setCurrentIndex((prev) => (prev + 1) % CHANNELS.length);
    } else {
      setCurrentIndex((prev) => (prev === 0 ? CHANNELS.length - 1 : prev - 1));
    }
    // Restart the 60s timer when user manually interacts
    startAutoCycle();
  };

  const currentChannel = CHANNELS[currentIndex];

  return (
    <>
      {/* The Floating Toggle Button */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          background: 'rgba(5, 7, 9, 0.9)',
          border: '2px solid #0A4A8B',
          borderRadius: '4px',
          padding: '8px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          cursor: 'pointer',
          zIndex: 1001,
          boxShadow: '0 0 10px rgba(0,0,0,0.8)',
          transition: 'all 0.2s ease-in-out',
        }}
      >
        <span style={{ color: '#00FF41', fontSize: '0.8rem' }}>●</span>
        <span className="font-mono" style={{ color: '#00F2FF', fontWeight: 'bold', fontSize: '0.85rem', letterSpacing: '1px' }}>INTEL FEED</span>
        <span style={{ color: '#00F2FF' }}>📺</span>
      </div>

      {/* The Modal Window */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '70px',
          right: '16px',
          width: '380px',
          background: 'rgba(10, 14, 18, 0.95)',
          border: '1px solid #00A86B',
          boxShadow: '0 0 20px rgba(0, 168, 107, 0.15)',
          borderRadius: '2px',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          
          {/* Top Header */}
          <div style={{ 
            padding: '10px 16px', 
            borderBottom: '1px solid #1A1A1A', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            background: 'rgba(5, 7, 9, 1)'
          }}>
            <div className="font-mono text-green glow-green" style={{ fontSize: '0.85rem', letterSpacing: '1px', fontWeight: 'bold', color: '#00FF41' }}>
              ● LIVE GEOPOLITICAL FEED
            </div>
            <div className="font-mono" style={{ fontSize: '0.65rem', border: '1px solid #333', padding: '2px 8px', color: '#666', cursor: 'pointer' }}>
              SYNC OFF
            </div>
          </div>

          {/* TX-NODE Navigation Bar */}
          <div style={{
            padding: '8px 16px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(0, 0, 0, 0.8)'
          }}>
            <div 
              style={{ color: '#00FF41', cursor: 'pointer', padding: '0 8px', fontSize: '1.2rem', fontWeight: 'bold' }}
              onClick={() => handleManualCycle('prev')}
            >
              &lt;
            </div>
            <div className="font-mono" style={{ color: '#E0E0E0', fontSize: '0.8rem', letterSpacing: '2px' }}>
              <span style={{ color: '#00A86B' }}>TX-NODE:</span> {currentChannel.name}
            </div>
            <div 
              style={{ color: '#00FF41', cursor: 'pointer', padding: '0 8px', fontSize: '1.2rem', fontWeight: 'bold' }}
              onClick={() => handleManualCycle('next')}
            >
              &gt;
            </div>
          </div>
          
          {/* Video Player */}
          <div style={{ width: '100%', height: '214px', background: '#000', borderTop: '1px solid #00A86B', borderBottom: '1px solid #00A86B' }}>
            <iframe
              key={currentChannel.id}
              width="100%"
              height="100%"
              src={currentChannel.id.length > 15 
                ? `https://www.youtube.com/embed/live_stream?channel=${currentChannel.id}&autoplay=1&mute=1&controls=1`
                : `https://www.youtube.com/embed/${currentChannel.id}?autoplay=1&mute=1&controls=1`}
              title={`${currentChannel.name} Live`}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>

          {/* Footer Bar */}
          <div style={{ 
            padding: '8px 16px', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            background: 'rgba(5, 7, 9, 1)'
          }}>
            <div className="font-mono" style={{ fontSize: '0.65rem', color: '#00A86B', letterSpacing: '1px' }}>
              〽 SIGNAL LINK ACTIVE
            </div>
            <div className="font-mono" style={{ fontSize: '0.65rem', color: '#666', letterSpacing: '2px' }}>
              [{currentIndex + 1}/{CHANNELS.length}]
            </div>
          </div>

        </div>
      )}
    </>
  );
};

export default LiveMediaBox;
