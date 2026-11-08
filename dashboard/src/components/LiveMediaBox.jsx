import React, { useState, useEffect, useRef } from 'react';

// Media Sources (Mixed Platforms to bypass blocks & verified 24/7 active streams)
const CHANNELS = [
  { name: 'AL JAZEERA', id: 'gCNeDWCI0vo', type: 'youtube' },
  { name: 'SKY NEWS', id: 'umLWFz4izTM', type: 'youtube' },
  { name: 'FRANCE 24', id: 'HvZt-nh9sGg', type: 'youtube' },
  { name: 'DW NEWS', id: 'LuKwFajn37U', type: 'youtube' },
  { name: 'ABC NEWS', id: 'l2CF4rOllmU', type: 'youtube' },
  { name: 'NBC NEWS NOW', id: '4a4IWlRVth0', type: 'youtube' },
  { name: 'BLOOMBERG', id: 'QB5BNdBFujE', type: 'youtube' },
  { name: 'IRAN INTERNATIONAL', id: '5JDxjsAVaGk', type: 'youtube' },
  { name: 'AL JAZEERA ARABIC', id: 'FelGGahCbS8', type: 'youtube' }
];

const LiveMediaBox = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const timerRef = useRef(null);

  // Dragging State
  const [pos, setPos] = useState({ 
    x: typeof window !== 'undefined' ? window.innerWidth - 420 : 0, 
    y: typeof window !== 'undefined' ? window.innerHeight - 440 : 0 
  });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

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

  const handlePointerDown = (e) => {
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - pos.x,
      y: e.clientY - pos.y
    });
    e.target.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e) => {
    if (isDragging) {
      setPos({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      });
    }
  };

  const handlePointerUp = (e) => {
    setIsDragging(false);
    e.target.releasePointerCapture(e.pointerId);
  };
  
  // Resolve source URL based on platform type. Mute is set to 0 to enable sound per user request.
  const getEmbedUrl = (channel) => {
    if (channel.type === 'dailymotion') {
      return `https://geo.dailymotion.com/player.html?video=${channel.id}&autoplay=1&mute=0`;
    }
    if (channel.type === 'youtube_channel') {
      return `https://www.youtube.com/embed/live_stream?channel=${channel.id}&autoplay=1&mute=0&controls=1`;
    }
    return `https://www.youtube.com/embed/${channel.id}?autoplay=1&mute=0&controls=1`;
  };

  return (
    <>
      {/* The Toggle Button (Now relative to its container to avoid text overlap) */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: 'rgba(5, 7, 9, 0.9)',
          borderTop: '2px solid #0A4A8B',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          cursor: 'pointer',
          marginTop: 'auto', // Push to the very bottom of the flex column
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
          top: `${pos.y}px`,
          left: `${pos.x}px`,
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
          
          {/* Top Header - DRAG HANDLE */}
          <div 
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
            style={{ 
            padding: '10px 16px', 
            borderBottom: '1px solid #1A1A1A', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            background: 'rgba(5, 7, 9, 1)',
            cursor: isDragging ? 'grabbing' : 'grab',
            userSelect: 'none',
            touchAction: 'none'
          }}>
            <div className="font-mono text-green glow-green" style={{ fontSize: '0.85rem', letterSpacing: '1px', fontWeight: 'bold', color: '#00FF41' }}>
              ● LIVE GEOPOLITICAL FEED
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div 
                className="font-mono" 
                style={{ fontSize: '0.65rem', border: '1px solid #ff3333', padding: '2px 8px', color: '#ff3333', cursor: 'pointer', background: 'rgba(255, 51, 51, 0.1)' }}
                onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                title="Close Feed"
              >
                ✕ CLOSE
              </div>
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
              src={getEmbedUrl(currentChannel)}
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
              <a 
                href={`https://www.youtube.com/watch?v=${currentChannel.id}`} 
                target="_blank" 
                rel="noreferrer" 
                style={{ color: '#00A86B', textDecoration: 'none' }}
              >
                〽 SIGNAL LINK ACTIVE ↗
              </a>
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
