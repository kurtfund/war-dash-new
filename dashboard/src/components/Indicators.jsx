import React from 'react';

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
    <div className="side-panel" style={{ width: '320px', position: 'absolute', right: 0, top: 0 }}>
      
      {/* Overview Block */}
      <div className="glass-panel" style={{ padding: '0' }}>
         <div style={{ padding: '12px 16px', background: 'rgba(255,0,51,0.1)', borderBottom: '1px solid var(--color-red-dim)' }}>
           <div className="text-red font-mono" style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>
             ● THREAT LEVEL METRICS (24H)
           </div>
         </div>
         
         <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <IndicatorRow label="KINETIC STRIKES" value={stats.kinetic} color="red" />
            <IndicatorRow label="CONFIRMED CASUALTIES" value={stats.casualties} color="red" />
            <IndicatorRow label="CIVIL UNREST" value={stats.unrest} color="yellow" />
            <IndicatorRow label="NAVAL INCIDENTS" value={stats.naval} color="cyan" />
         </div>
      </div>
      
      {/* Source Reliability Block */}
      <div className="glass-panel" style={{ flex: 1, padding: '0' }}>
         <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-cyan-dim)' }}>
           <div className="text-cyan font-mono" style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>
             ● SOURCE INTEGRITY
           </div>
         </div>
         <div style={{ padding: '16px' }} className="text-muted font-mono">
            <div style={{ fontSize: '0.75rem', marginBottom: '8px' }}>AVG CONFIDENCE SCORE</div>
            <div className="text-cyan glow-cyan" style={{ fontSize: '2rem' }}>
              {(alerts.length > 0 ? (alerts.reduce((a, b) => a + (b.confidence || 0.6), 0) / alerts.length * 100).toFixed(1) : 0)}%
            </div>
            <div style={{ marginTop: '16px', borderTop: '1px dashed rgba(255,255,255,0.2)', paddingTop: '16px', fontSize: '0.75rem', lineHeight: '1.6' }}>
               INTELLIGENCE SOURCES: {new Set(alerts.map(a => new URL(a.url).hostname)).size}<br/>
               VERIFIED LOCATIONS: {alerts.filter(a => a.coordinates).length}
            </div>
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
