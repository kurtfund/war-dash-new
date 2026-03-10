import React from 'react';

const icons = {
  MISSILE: "🚀",
  AIRSTRIKE: "💥",
  DRONE: "🛩️",
  NAVAL: "⚓",
  PROTEST: "🚩",
  "Military Activity": "⚔️",
  "Disaster": "⚠️",
  "Casualty Report": "💀",
  "Other": "🔘"
};

const getGlowClass = (type) => {
  if (type === 'MISSILE' || type === 'AIRSTRIKE' || type === 'Casualty Report') return 'text-red glow-red';
  if (type === 'Disaster' || type === 'PROTEST') return 'text-yellow glow-yellow';
  return 'text-cyan glow-cyan';
};

const getTimeAgo = (dateString) => {
  const diff = new Date() - new Date(dateString);
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs/24)}d ago`;
};

const AlertFeed = ({ alerts }) => {
  return (
    <div className="side-panel" style={{ width: '380px' }}>
      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* Panel Header */}
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-cyan-dim)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
           <div className="text-cyan font-mono" style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>
             ● LIVE GEOPOLITICAL ALERT FEED
           </div>
           <div className="text-muted font-mono" style={{ fontSize: '0.7rem' }}>
             SYS: NOMINAL
           </div>
        </div>

        {/* Scrolling Event List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {alerts.map((alert) => (
            <div key={alert.id} className="glass-panel" style={{ padding: '16px', background: 'rgba(5, 8, 12, 0.9)', borderLeft: '3px solid var(--color-cyan)', borderRadius: '4px' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                 <div>
                   <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                     <span style={{ 
                       background: 'rgba(255,255,255,0.1)', 
                       padding: '2px 6px', 
                       borderRadius: '2px', 
                       fontSize: '0.65rem',
                       color: 'white'
                     }}>{alert.country?.toUpperCase() || 'UNKNOWN'}</span>
                     <span className={`font-mono font-bold ${getGlowClass(alert.event_type)}`} style={{ fontSize: '0.8rem', letterSpacing: '1px' }}>
                        {icons[alert.event_type] || icons['Other']} {alert.event_type}
                     </span>
                   </div>
                   <div className="text-muted font-mono" style={{ fontSize: '0.7rem' }}>
                     {alert.location_name || 'Coordinates Only'}
                   </div>
                 </div>
                 
                 <div className="text-muted font-mono" style={{ fontSize: '0.7rem', textAlign: 'right' }}>
                   {getTimeAgo(alert.created_at)}
                 </div>
              </div>

              <div style={{ fontSize: '0.9rem', lineHeight: '1.4', marginBottom: '12px', color: '#FFF' }}>
                {alert.headline}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '12px' }}>
                <a href={alert.url} target="_blank" rel="noreferrer" className="text-muted" style={{ fontSize: '0.75rem', textDecoration: 'none', borderBottom: '1px solid var(--color-text-muted)' }}>
                  SOURCE: {(new URL(alert.url)).hostname.replace('www.', '')}
                </a>
                
                {alert.deaths > 0 && (
                  <div className="text-red font-mono glow-red" style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>
                    💀 FATALITIES: {alert.deaths}
                  </div>
                )}
              </div>
              
            </div>
          ))}
          {alerts.length === 0 && (
            <div className="text-muted font-mono" style={{ textAlign: 'center', marginTop: '40px' }}>
               AWAITING INTEL DATA...
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
};

export default AlertFeed;
