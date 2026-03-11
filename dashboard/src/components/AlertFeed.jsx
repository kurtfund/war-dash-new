import React from 'react';
import { getHostname } from '../lib/utils';

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
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* Panel Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #1A1A1A', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--color-obsidian)' }}>
           <div className="text-cyan font-mono" style={{ fontSize: '0.85rem', letterSpacing: '1px', fontWeight: 'bold' }}>
             ● LIVE GEOPOLITICAL ALERT FEED
           </div>
           <div className="text-muted font-mono" style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
             SYS: NOMINAL
           </div>
        </div>

        {/* Scrolling Event List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {alerts.map((alert) => (
            <div key={alert.id} className="glass-panel" style={{ padding: '16px', background: 'rgba(10, 14, 18, 0.6)', border: '1px solid #1A1A1A', borderLeft: '3px solid var(--color-cyan)', borderRadius: '4px' }}>
              
              {/* Card Meta Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                 <div>
                   <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                     <span style={{ 
                       background: 'rgba(255,255,255,0.1)', 
                       padding: '2px 6px', 
                       borderRadius: '2px', 
                       fontSize: '0.65rem',
                       color: 'white'
                     }}>{alert.country?.toUpperCase() || 'UNKNOWN'}</span>
                     <span className={`font-mono font-bold ${getGlowClass(alert.event_type)}`} style={{ fontSize: '0.75rem', letterSpacing: '1px' }}>
                        {icons[alert.event_type] || icons['Other']} {alert.event_type}
                     </span>
                   </div>
                 </div>
                 
                 <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                    <div className="text-muted font-mono" style={{ fontSize: '0.7rem' }}>
                      {getTimeAgo(alert.created_at)}
                    </div>
                    {/* Implemented Source Integrity per article */}
                    <div className="text-cyan font-mono" style={{ fontSize: '0.65rem', padding: '2px 6px', border: '1px solid var(--color-cyan-dim)', borderRadius: '4px', background: 'rgba(0,242,255,0.05)' }}>
                       INTEGRITY: {(alert.confidence * 100).toFixed(0)}%
                    </div>
                 </div>
              </div>

              {/* Headline */}
              <div className="font-mono" style={{ fontSize: '0.9rem', lineHeight: '1.5', marginBottom: '16px', color: '#FFF' }}>
                {alert.headline}
              </div>

              {/* Footer Links & Casualties */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px dashed #1A1A1A', paddingTop: '12px' }}>
                <a href={alert.url} target="_blank" rel="noreferrer" className="text-muted font-mono" style={{ fontSize: '0.75rem', textDecoration: 'none' }}>
                  SOURCE: <span style={{ color: 'var(--color-cyan)' }}>{alert.source || getHostname(alert.url)}</span>
                </a>
                
                {alert.deaths > 0 && (
                  <div className="text-red font-mono glow-red" style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>
                    💀 FATALS: {alert.deaths}
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
  );
};

export default AlertFeed;
