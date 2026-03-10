import React from 'react';
import '../index.css';

const Header = () => {
  return (
    <header className="header-bar">
      <div className="flex items-center gap-4 w-full">
        {/* Logo/Title Area */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            borderRadius: '50%', 
            border: '2px solid var(--color-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 10px var(--color-cyan-dim)'
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-cyan)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <circle cx="12" cy="12" r="6"></circle>
              <circle cx="12" cy="12" r="2"></circle>
            </svg>
          </div>
          <div>
            <h1 className="font-mono" style={{ fontSize: '1.2rem', letterSpacing: '2px', margin: 0 }}>WAR DASH</h1>
            <div className="text-cyan font-mono" style={{ fontSize: '0.7rem', letterSpacing: '1px' }}>GEOPOLITICAL HEAT INDEX</div>
          </div>
        </div>
        
        <div style={{ flex: 1 }}></div>
        
        {/* Global Stats Area - Placeholder for now */}
        <div className="glass-panel" style={{ display: 'flex', gap: '24px', padding: '8px 16px', borderTop: 'none', borderBottom: 'none', borderRadius: 0 }}>
           <div style={{ textAlign: 'center' }}>
             <div className="text-muted font-mono" style={{ fontSize: '0.65rem' }}>ACTIVE ALERTS (24H)</div>
             <div className="text-red font-mono glow-red" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>---</div>
           </div>
           <div style={{ width: '1px', background: 'var(--color-cyan-dim)' }}></div>
           <div style={{ textAlign: 'center' }}>
             <div className="text-muted font-mono" style={{ fontSize: '0.65rem' }}>SYSTEM STATUS</div>
             <div className="text-cyan font-mono glow-cyan" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>ONLINE</div>
           </div>
        </div>
        
         <div style={{ flex: 1 }}></div>
         
         {/* Time Area */}
         <div className="font-mono text-yellow glow-yellow" style={{ fontSize: '0.85rem', textAlign: 'right' }}>
            <div>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric'})}</div>
            <div>{new Date().toLocaleTimeString('en-US', { hour12: false })} UTC</div>
         </div>
      </div>
    </header>
  );
};

export default Header;
