import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const Indicators = ({ alerts }) => {
  
  // Dynamic Calculation for the "HEARTBEAT" score based on active alerts
  const baseHeartbeat = 90.0;
  const recentKinetic = alerts.filter(a => ['MISSILE', 'AIRSTRIKE', 'DRONE'].includes(a.event_type)).length;
  // Cap at 99.9
  const heartbeatScore = Math.min(99.9, baseHeartbeat + (recentKinetic * 0.5)).toFixed(1);

  const [mofaSummary, setMofaSummary] = useState(null);

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
      <div className="indicators-wrapper" style={{ pointerEvents: 'auto', justifyContent: 'center' }}>
        
        {/* PREDICTIVE AI INTEL Box */}
        <div className="glass-panel indicators-panel" style={{  
          flex: 0.8, 
          padding: '12px 16px',
          background: 'rgba(5, 7, 9, 0.85)',
          border: '1px solid rgba(0, 229, 255, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          maxWidth: '450px'
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
              <div>
                <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '4px' }}>AVG MISSILES / 24H 🚀</div>
                <div className="font-mono text-main" style={{ fontSize: '1.4rem', fontWeight: 'bold', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                  452.5 <span className="text-red glow-red" style={{ fontSize: '0.6rem' }}>↑ 12.4%</span>
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
      </div>
    </div>
  );
};

export default Indicators;
