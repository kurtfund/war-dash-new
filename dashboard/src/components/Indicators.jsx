import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const Indicators = ({ alerts }) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [mofaSummary, setMofaSummary] = useState(null);

  // Default Base Score
  let heartbeatScore = 65.0;

  // Enhance the score using Real UAE WAM Interception Integer Data
  if (mofaSummary && mofaSummary.raw_data) {
    const missiles = mofaSummary.raw_data.missiles || 0;
    const drones = mofaSummary.raw_data.drones || 0;
    heartbeatScore += (missiles * 3.0) + (drones * 1.5);
  } else {
    // Fallback: Use standard alerts count if WAM data isn't loaded yet
    const recentKinetic = alerts.filter(a => ['MISSILE', 'AIRSTRIKE', 'DRONE'].includes(a.event_type)).length;
    heartbeatScore += (recentKinetic * 0.5);
  }

  // Strictly cap the maximum conflict score at 99.9 (DEFCON 1 approaching)
  heartbeatScore = Math.min(99.9, heartbeatScore).toFixed(1);

  useEffect(() => {
    const fetchMofa = async () => {
      const { data, error } = await supabase
        .from('security_alerts')
        .select('*')
        .eq('event_type', 'OFFICIAL_SUMMARY')
        .order('created_at', { ascending: false })
        .limit(1);
      
      if (data && data.length > 0) {
        setMofaSummary(data[0]);
      }
    };

    fetchMofa();
    const interval = setInterval(fetchMofa, 300000); // 5 minutes
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="indicators-overlay">
      {/* Bottom Interface Split */}
      <div className="indicators-wrapper" style={{ 
        pointerEvents: 'auto', 
        justifyContent: 'flex-end', 
        alignItems: 'flex-end', 
        gap: '40px', 
        paddingBottom: '20px',
        paddingRight: '20px'
      }}>
        
        {/* PREDICTIVE AI INTEL Box (Left Aligned Now) */}
        <div className="glass-panel indicators-panel" style={{  
          flex: '0 1 450px', 
          padding: '12px 16px',
          background: 'rgba(5, 7, 9, 0.85)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
        }}>
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="font-mono" style={{ color: 'var(--color-cyan)', fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1rem' }}>●</span> PREDICTIVE AI INTEL 🚀
              </div>
              <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>
                MODEL: GPT-4O-V2 // GEOPOL-SYNC
              </div>
           </div>
           
           <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div style={{ display: 'flex', gap: '20px' }}>
                <div>
                  <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '4px' }}>BALLISTIC 🚀</div>
                  <div className="font-mono text-main" style={{ fontSize: '1.4rem', fontWeight: 'bold', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    {mofaSummary?.raw_data?.ballistic || mofaSummary?.raw_data?.missiles || 0}
                  </div>
                </div>
                <div>
                  <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '4px' }}>CRUISE 🚀</div>
                  <div className="font-mono text-main" style={{ fontSize: '1.4rem', fontWeight: 'bold', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    {mofaSummary?.raw_data?.cruise || 0}
                  </div>
                </div>
                <div>
                  <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '4px' }}>UAVS 🚁</div>
                  <div className="font-mono text-main" style={{ fontSize: '1.4rem', fontWeight: 'bold', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    {mofaSummary?.raw_data?.uavs || mofaSummary?.raw_data?.drones || 0}
                  </div>
                </div>
              </div>
              
              <div style={{ flex: 1, margin: '0 40px', position: 'relative', top: '-8px' }}>
                 <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', display: 'flex', position: 'relative' }}>
                   <div style={{ width: '40%', height: '100%', background: 'var(--color-cyan)', borderRadius: '2px 0 0 2px', boxShadow: '0 0 10px var(--color-cyan)' }}></div>
                   <div style={{ width: '15%', height: '100%', background: '#FF0033', boxShadow: '0 0 10px #FF0033' }}></div>
                 </div>
                 <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
                   <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>INCEPTION</span>
                   <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>PEAK 🚀</span>
                   <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>ARCH</span>
                 </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '4px' }}>CONFLICT ARCH 🚀</div>
                <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>
                  14.2 Days <span className="text-muted" style={{ fontSize: '0.6rem' }}>REM.</span>
                </div>
              </div>
           </div>
        </div>

        {/* Center Iron Man Reactor / Heat Index */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }} onClick={() => setIsRevealed(!isRevealed)}>
            <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '0.7rem', letterSpacing: '2px', marginBottom: '10px' }}>
              GEOPOLITICAL HEAT INDEX 🚀
            </div>
            
            <div style={{ position: 'relative', width: '220px', height: '220px' }}>
                {/* Visual Dial Rings */}
                <div style={{
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                  borderRadius: '50%',
                  border: '4px solid rgba(0, 229, 255, 0.1)',
                  boxShadow: '0 0 30px rgba(0, 229, 255, 0.2), inset 0 0 30px rgba(0, 229, 255, 0.1)',
                  animation: 'pulse 4s infinite alternate'
                }}></div>
                <div style={{
                  position: 'absolute', top: '10px', left: '10px', right: '10px', bottom: '10px',
                  borderRadius: '50%',
                  border: '2px solid rgba(255, 0, 51, 0.3)',
                  borderTopColor: 'rgba(255, 0, 51, 0.8)',
                  animation: 'spin 12s linear infinite'
                }}></div>
                <div style={{
                  position: 'absolute', top: '20px', left: '20px', right: '20px', bottom: '20px',
                  borderRadius: '50%',
                  border: '2px dashed rgba(0, 229, 255, 0.4)',
                  animation: 'spin 25s linear infinite reverse'
                }}></div>
                
                {/* Inside Score / Reactor State */}
                <div style={{
                  position: 'absolute', top: '30px', left: '30px', right: '30px', bottom: '30px',
                  backgroundColor: 'rgba(5, 7, 9, 0.9)',
                  borderRadius: '50%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.8), 0 0 15px rgba(0,229,255,0.4)',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
                }}>
                  {!isRevealed ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', position: 'absolute' }}>
                      <img 
                         src="/logo.png" 
                         alt="War Dash Logo" 
                         style={{ maxWidth: '65%', maxHeight: '65%', objectFit: 'contain', zIndex: 1, marginBottom: '15px' }} 
                      />
                      <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '0.45rem', letterSpacing: '1px', textAlign: 'center', position: 'absolute', bottom: '25px', zIndex: 2 }}>
                        CLICK TO REVEAL<br/>DAILY SCORE
                      </div>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '2px', marginTop: '-10px' }}>HEARTBEAT</div>
                      <div className="font-mono text-main" style={{ fontSize: '3.5rem', fontWeight: 'bold', textShadow: '0 0 20px rgba(255,255,255,0.8)' }}>
                        {heartbeatScore}
                      </div>
                      <div className="font-mono text-cyan" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>CONFLICT SCORE</div>
                    </div>
                  )}
                </div>
            </div>
            
            <div className="font-mono text-red glow-red" style={{ fontSize: '0.6rem', letterSpacing: '2px', marginTop: '10px' }}>
              -- CRITICAL IMMINENT THREAT --
            </div>
        </div>
        
      </div>
    </div>
  );
};

export default Indicators;
