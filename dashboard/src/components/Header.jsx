import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import '../index.css';

const Header = () => {
  const [mofaSummary, setMofaSummary] = useState(null);

  useEffect(() => {
    // 1. Fetch initial latest summary
    const fetchMofa = async () => {
      const { data, error } = await supabase
        .from('wam_official_data')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1);
      
      if (data && data.length > 0) {
        setMofaSummary(data[0]);
      }
    };

    fetchMofa();

    // 2. Subscribe to realtime Mofa updates
    const channel = supabase
      .channel('public:wam_official_data')
      .on('postgres_changes', { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'wam_official_data'
      }, (payload) => {
        setMofaSummary(payload.new);
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  return (
    <header className="header-bar" style={{ padding: '0 32px' }}>
      <div className="header-content w-full">
        
        {/* Left: Branding */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
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
        
        {/* Middle: OFFICIAL MOFA SUMMARY (Top Center - Hidden on Mobile, handled via CSS) */}
        <div className="mofa-header-container" style={{ flex: '0 1 auto', display: 'flex', justifyContent: 'center', position: 'relative', top: '15px', zIndex: 100 }}>
          {mofaSummary?.url ? (
            <a href={mofaSummary.url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
              <div className="glass-panel hover-glow mofa-statement-panel" style={{
                background: 'rgba(5, 7, 9, 0.85)',
                border: '1px solid rgba(0, 168, 107, 0.5)',
                borderRadius: '6px',
                padding: '8px 24px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                boxShadow: '0 0 15px rgba(0, 168, 107, 0.1)',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out'
              }}>
                <div className="font-mono text-green-teal" style={{ fontSize: '0.7rem', letterSpacing: '2px', fontWeight: 'bold', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="glow-green-teal" style={{ fontSize: '1rem' }}>✦</span>
                  OFFICIAL UAE STATEMENT
                  <span className="glow-green-teal" style={{ fontSize: '1rem' }}>✦</span>
                </div>
            
            {mofaSummary ? (
              <div className="mofa-stats-row" style={{ display: 'flex', alignItems: 'center', gap: '24px', padding: '4px 8px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div className="font-mono text-main glow-main" style={{ fontSize: '1.6rem', fontWeight: 'bold', lineHeight: '1.1' }}>
                    {mofaSummary.missiles || 0}
                  </div>
                  <div className="font-mono" style={{ fontSize: '0.55rem', letterSpacing: '1px', lineHeight: '1.4', textAlign: 'center', maxWidth: '80px', color: '#FF0033' }}>BALLISTIC MISSILES</div>
                  {mofaSummary.raw_data?.daily_ballistic > 0 && (
                    <div className="font-mono glow-main" style={{ fontSize: '0.55rem', marginTop: '4px', letterSpacing: '1px', color: '#FF0033' }}>(+{mofaSummary.raw_data.daily_ballistic} TODAY)</div>
                  )}
                </div>
                
                <div style={{ width: '1px', height: '32px', background: 'rgba(255,255,255,0.15)', flexShrink: 0 }}></div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '1.6rem', fontWeight: 'bold', lineHeight: '1.1' }}>
                    {mofaSummary.cruise || 0}
                  </div>
                  <div className="font-mono text-cyan" style={{ fontSize: '0.55rem', letterSpacing: '1px', lineHeight: '1.4', textAlign: 'center', maxWidth: '80px' }}>CRUISE MISSILES</div>
                  {mofaSummary.raw_data?.daily_cruise > 0 && (
                    <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '0.55rem', marginTop: '4px', letterSpacing: '1px' }}>(+{mofaSummary.raw_data.daily_cruise} TODAY)</div>
                  )}
                </div>

                <div style={{ width: '1px', height: '32px', background: 'rgba(255,255,255,0.15)', flexShrink: 0 }}></div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div className="font-mono text-yellow glow-yellow" style={{ fontSize: '1.6rem', fontWeight: 'bold', lineHeight: '1.1' }}>
                    {mofaSummary.uavs || 0}
                  </div>
                  <div className="font-mono text-yellow" style={{ fontSize: '0.55rem', letterSpacing: '1px', lineHeight: '1.4', textAlign: 'center', maxWidth: '80px' }}>DRONES DOWNED</div>
                  {mofaSummary.raw_data?.daily_uavs > 0 && (
                    <div className="font-mono text-yellow glow-yellow" style={{ fontSize: '0.55rem', marginTop: '4px', letterSpacing: '1px' }}>(+{mofaSummary.raw_data.daily_uavs} TODAY)</div>
                  )}
                </div>
              </div>
            ) : (
                <div className="font-mono text-muted" style={{ fontSize: '0.8rem', padding: '6px 0', fontStyle: 'italic' }}>
                  [ 🚀 Awaiting secure data transmission... ]
                </div>
            )}
            </div>
          </a>
          ) : (
            <div className="glass-panel hover-glow mofa-statement-panel" style={{
              background: 'rgba(5, 7, 9, 0.85)',
              border: '1px solid rgba(0, 168, 107, 0.5)',
              borderRadius: '6px',
              padding: '8px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 0 15px rgba(0, 168, 107, 0.1)',
            }}>
              <div className="font-mono text-green-teal" style={{ fontSize: '0.7rem', letterSpacing: '2px', fontWeight: 'bold', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="glow-green-teal" style={{ fontSize: '1rem' }}>✦</span>
                OFFICIAL UAE STATEMENT
                <span className="glow-green-teal" style={{ fontSize: '1rem' }}>✦</span>
              </div>
              <div className="font-mono text-muted" style={{ fontSize: '0.8rem', padding: '6px 0', fontStyle: 'italic' }}>
                [ 🚀 Awaiting secure data transmission... ]
              </div>
            </div>
          )}
        </div>
         
         {/* Right: Chronology */}
         <div className="header-chronology font-mono text-yellow glow-yellow" style={{ flex: 1, fontSize: '0.85rem', textAlign: 'right', fontWeight: 'bold' }}>
            <div style={{ letterSpacing: '1px' }}>
              Day {Math.floor((new Date() - new Date('2026-02-28')) / (1000 * 60 * 60 * 24)) + 1} 🚀 | Since Saturday, Feb 28, 2026
            </div>
            <div className="text-muted" style={{ fontSize: '0.65rem', marginTop: '4px', letterSpacing: '1px' }}>
              <span className="text-red glow-red">●</span> {new Date().toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })} GMT <span style={{ color: '#00F2FF', margin: '0 6px' }}>|</span> {new Date().toLocaleTimeString('en-US', { hour12: false, timeZone: 'Asia/Dubai' })} UAE 🚀
            </div>
         </div>
      </div>
    </header>
  );
};

export default Header;
