import React, { useRef, useEffect, useMemo } from 'react';
import { getHostname } from '../lib/utils';

const AlertFeed = ({ alerts }) => {
  const scrollRef = useRef(null);
  
  // Interleave alerts: maintain strictly chronological order, but avoid back-to-back articles from the identical source if possible.
  const interleavedAlerts = useMemo(() => {
    if (!alerts || alerts.length === 0) return [];
    
    // Sort descending by time to ensure newest is always first
    const sortedAlerts = [...alerts].sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
    
    const result = [];
    const pending = [...sortedAlerts];
    
    while(pending.length > 0) {
        // Look at the source of the last article we added to the feed
        const lastSource = result.length > 0 ? (result[result.length - 1].source || getHostname(result[result.length - 1].url)) : null;
        
        // Find the newest article whose source is DIFFERENT from the last one
        let foundIndex = -1;
        for (let i = 0; i < pending.length; i++) {
            const currentSource = pending[i].source || getHostname(pending[i].url);
            if (currentSource !== lastSource) {
                foundIndex = i;
                break;
            }
        }
        
        // If all remaining articles are from the exact same source, we just have to allow them back-to-back
        if (foundIndex === -1) {
            foundIndex = 0;
        }
        
        // Push the article to the feed and remove it from the pending pool
        result.push(pending[foundIndex]);
        pending.splice(foundIndex, 1);
    }
    
    // Safety cap to prevent browser lag if database grows infinitely
    return result.slice(0, 150);
  }, [alerts]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* Panel Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #1A1A1A', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--color-obsidian)' }}>
           <div className="font-mono" style={{ color: 'var(--color-green-teal)', fontSize: '0.85rem', letterSpacing: '1px', fontWeight: 'bold' }}>
             ● LIVE GEOPOLITICAL ALERT FEED
           </div>
           <div className="text-muted font-mono" style={{ fontSize: '0.65rem' }}>
             GMT<br/>{new Date().toLocaleTimeString('en-GB', { hour12: false })}
           </div>
        </div>

        {/* Scrolling Event List */}
        <div 
          ref={scrollRef}
          style={{ 
            flex: 1, 
            overflowY: 'auto', 
            padding: '12px', 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '8px', 
            scrollBehavior: 'auto' // Important for manual scrollTop manipulation
          }}
        >
          {interleavedAlerts.map((alert) => {
             const d = new Date(alert.created_at);
             const dayStr = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
             const timeStr = d.toLocaleTimeString('en-GB', { hour12: false });
             
             // Dynamic border based on kinetic nature
             const isKinetic = ['MISSILE', 'AIRSTRIKE', 'Casualty Report', 'DRONE'].includes(alert.event_type);
             const borderColor = isKinetic ? 'rgba(255, 0, 51, 0.4)' : '#1A1A1A';
             
             return (
              <div key={alert.id} style={{ 
                padding: '12px', 
                background: 'rgba(5, 7, 9, 0.6)', 
                border: `1px solid ${borderColor}`,
                borderRadius: '4px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                
                {/* Header Row: Country Badge, Source, Date/Time */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                   <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                     <div className="font-mono text-main" style={{ 
                       background: 'rgba(255,255,255,0.05)', 
                       padding: '2px 6px', 
                       borderRadius: '4px', 
                       fontSize: '0.65rem',
                       fontWeight: 'bold',
                       border: '1px solid #333'
                     }}>
                       🚀 {alert.country?.toUpperCase().substring(0, 10) || 'UNKNOWN'}
                     </div>
                     <a href={alert.url} target="_blank" rel="noreferrer" className="font-mono" style={{ 
                       color: 'var(--color-cyan)', 
                       fontSize: '0.8rem', 
                       fontWeight: 'bold', 
                       textDecoration: 'none' 
                     }}>
                       {alert.source || getHostname(alert.url)} ↗
                     </a>
                   </div>
                   
                   <div className="text-muted font-mono" style={{ fontSize: '0.6rem', textAlign: 'right', lineHeight: '1.2' }}>
                      {dayStr}<br/>{timeStr}
                   </div>
                </div>

                {/* Sub-tags Row */}
                <div style={{ display: 'flex', gap: '6px' }}>
                   <div className="font-mono" style={{ 
                     color: 'var(--color-cyan)',
                     fontSize: '0.55rem', 
                     padding: '2px 4px', 
                     border: '1px solid var(--color-cyan-dim)', 
                     borderRadius: '2px', 
                     letterSpacing: '0.5px' 
                   }}>
                     INT: {(alert.confidence * 100).toFixed(0)}%
                   </div>
                   <div className="font-mono text-red" style={{ 
                     fontSize: '0.55rem', 
                     padding: '2px 4px', 
                     border: '1px solid var(--color-red-dim)', 
                     borderRadius: '2px', 
                     letterSpacing: '0.5px',
                     background: 'rgba(255,0,51,0.05)'
                   }}>
                     {alert.event_type}
                   </div>
                   {alert.deaths > 0 && (
                     <div className="font-mono text-yellow" style={{ 
                       fontSize: '0.55rem', 
                       padding: '2px 4px', 
                       border: '1px solid var(--color-yellow-dim)', 
                       borderRadius: '2px'
                     }}>
                       FATALS: {alert.deaths}
                     </div>
                   )}
                </div>

                {/* Headline */}
                <div className="font-mono text-main" style={{ fontSize: '0.75rem', lineHeight: '1.5', marginTop: '4px', opacity: 0.9 }}>
                  {alert.headline}
                </div>
                
              </div>
            );
          })}
          
          {interleavedAlerts.length === 0 && (
            <div className="text-muted font-mono" style={{ textAlign: 'center', marginTop: '40px' }}>
               AWAITING INTEL DATA...
            </div>
          )}
        </div>
        
    </div>
  );
};

export default AlertFeed;
