import React, { useRef, useEffect, useMemo } from 'react';
import { getHostname } from '../lib/utils';

const AlertFeed = ({ alerts }) => {
  const scrollRef = useRef(null);
  
  // Dynamically interleave articles from different sources so one outlet doesn't dominate
  const interleavedAlerts = useMemo(() => {
    if (!alerts || alerts.length === 0) return [];
    
    // 1. Group alerts by their source name
    const sourceGroups = {};
    alerts.forEach(alert => {
      const source = alert.source || getHostname(alert.url);
      if (!sourceGroups[source]) sourceGroups[source] = [];
      sourceGroups[source].push(alert);
    });

    const result = [];
    const groupKeys = Object.keys(sourceGroups);
    let itemsRemaining = alerts.length;

    // 2. Round-robin draw one article from each source group until all are depleted
    let roundIndex = 0;
    while (itemsRemaining > 0) {
      let drawnInRound = false;
      for (const key of groupKeys) {
        if (sourceGroups[key].length > 0) {
          result.push(sourceGroups[key].shift()); // take the top (newest) item from this source
          itemsRemaining--;
          drawnInRound = true;
        }
      }
      
      // If we somehow infinite loop or drew nothing but have items left (sanity check)
      if (!drawnInRound) break; 
      roundIndex++;
      if (roundIndex > 250) break; // safety
    }
    
    return result;
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
