import React, { useState, useEffect } from 'react';
import '../index.css';

const Header = () => {
  // Using static reference values now to avoid the 0/0 error from broken frontend scraping.
  // Real WAM data is being piped into the MOFA Summary box via the backend.
  const [wamMetrics, setWamMetrics] = useState({ stat1: 4313, stat2: 1628, label1: 'TOTAL IRAN SALVOS', label2: 'DEFENSE INTERCEPTS' });

  return (
    <header className="header-bar" style={{ padding: '0 32px' }}>
      <div className="flex items-center w-full" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
        
        {/* Left: Branding */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ 
            width: '56px', 
            height: '56px', 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <img src="/logo.png" alt="War Dash Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </div>
          <div>
            <h1 className="font-mono" style={{ fontSize: '1.4rem', letterSpacing: '3px', margin: 0, fontWeight: 'bold', color: '#FFF' }}>WAR DASH</h1>
            <div className="text-cyan font-mono glow-cyan" style={{ fontSize: '0.65rem', letterSpacing: '2px', fontWeight: 'bold' }}>GEOPOLITICAL HEAT INDEX</div>
          </div>
        </div>
        
        {/* Middle: Data Dashboard */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ 
            display: 'flex', 
            border: '1px solid rgba(255, 0, 51, 0.3)', 
            background: 'rgba(255,0,51,0.02)',
            padding: '8px 32px',
            borderRadius: '4px',
            gap: '40px'
          }}>
             <div style={{ textAlign: 'center' }}>
               <div className="font-mono text-muted" style={{ fontSize: '0.65rem', letterSpacing: '2px', marginBottom: '6px' }}>TOTAL IRAN SALVOS *</div>
               <div className="font-mono text-main glow-red" style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
                  <span style={{ color: '#FF0033', fontSize: '1rem', marginRight: '6px' }}>🚀</span> 
                  {wamMetrics.stat1.toLocaleString()}
               </div>
             </div>
             
             <div style={{ width: '1px', background: 'rgba(255, 0, 51, 0.2)' }}></div>
             
             <div style={{ textAlign: 'center' }}>
               <div className="font-mono text-muted" style={{ fontSize: '0.65rem', letterSpacing: '2px', marginBottom: '6px' }}>DEFENSE INTERCEPTS</div>
               <div className="font-mono text-main glow-green" style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
                  <span style={{ color: '#00FF41', fontSize: '1rem', marginRight: '6px' }}>⭕</span> 
                  {wamMetrics.stat2.toLocaleString()}
               </div>
             </div>
          </div>
          <div className="font-mono text-muted" style={{ fontSize: '0.5rem', marginTop: '6px', letterSpacing: '2px' }}>
            * INCLUDES BALLISTIC, CRUISE, AND DRONES
          </div>
        </div>
         
         {/* Right: Chronology */}
         <div className="font-mono text-yellow glow-yellow" style={{ fontSize: '0.85rem', textAlign: 'right', fontWeight: 'bold' }}>
            <div style={{ letterSpacing: '1px' }}>
              Day 12 | Since Saturday, Feb 28, 2026
            </div>
            <div className="text-muted" style={{ fontSize: '0.7rem', marginTop: '4px', letterSpacing: '2px' }}>
              <span className="text-red glow-red">●</span> {new Date().toLocaleTimeString('en-US', { hour12: false })} UTC
            </div>
         </div>
      </div>
    </header>
  );
};

export default Header;
