import React from 'react';
import { getHostname } from '../lib/utils';

const Indicators = ({ alerts }) => {
  // Calculate basic stats
  const stats = alerts.reduce((acc, curr) => {
    if (curr.event_type === 'MISSILE' || curr.event_type === 'AIRSTRIKE') acc.kinetic++;
    if (curr.deaths > 0) acc.casualties += curr.deaths;
    if (curr.event_type === 'PROTEST') acc.unrest++;
    if (curr.event_type === 'NAVAL') acc.naval++;
    return acc;
  }, { kinetic: 0, casualties: 0, unrest: 0, naval: 0 });

  return (
    <div style={{ 
      position: 'absolute', 
      bottom: '20px', 
      left: '50%', 
      transform: 'translateX(-50%)', 
      width: '280px', 
      zIndex: 1000, 
      pointerEvents: 'none' 
    }}>
      <div className="glass-panel" style={{ padding: '0', pointerEvents: 'auto' }}>
         <div style={{ padding: '8px 12px', background: 'rgba(255,0,51,0.1)', borderBottom: '1px solid var(--color-red-dim)' }}>
           <div className="text-red font-mono" style={{ fontSize: '0.7rem', letterSpacing: '1px', textAlign: 'center' }}>
             ● THREAT LEVEL METRICS (24H)
           </div>
         </div>
         
         <div style={{ padding: '10px 14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <IndicatorRow label="KINETIC STRIKES" value={stats.kinetic} color="red" />
            <IndicatorRow label="CONFIRMED CASUALTIES" value={stats.casualties} color="red" />
            <IndicatorRow label="CIVIL UNREST" value={stats.unrest} color="yellow" />
            <IndicatorRow label="NAVAL INCIDENTS" value={stats.naval} color="cyan" />
         </div>
      </div>
    </div>
  );
};

const IndicatorRow = ({ label, value, color }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div className="text-muted font-mono" style={{ fontSize: '0.75rem' }}>{label}</div>
    <div className={`font-mono text-${color} glow-${color}`} style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
      {value.toLocaleString()}
    </div>
  </div>
);

export default Indicators;
