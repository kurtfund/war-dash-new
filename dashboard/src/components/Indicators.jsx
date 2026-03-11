import React from 'react';

const Indicators = ({ alerts }) => {
  
  // Dynamic Calculation for the "HEARTBEAT" score based on active alerts
  const baseHeartbeat = 90.0;
  const recentKinetic = alerts.filter(a => ['MISSILE', 'AIRSTRIKE', 'DRONE'].includes(a.event_type)).length;
  // Cap at 99.9
  const heartbeatScore = Math.min(99.9, baseHeartbeat + (recentKinetic * 0.5)).toFixed(1);

  return (
    <div style={{ 
      position: 'absolute', 
      bottom: '10px', 
      left: '0', 
      width: '100%', 
      height: '100%',
      zIndex: 1000, 
      pointerEvents: 'none',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-end',
      padding: '0 20px 20px 20px'
    }}>
      
      {/* Top section of the overlay: Telemetry Table on left, Map is behind */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flex: 1 }}>
         
         {/* REGIONAL TELEMETRY Box (Left Side) */}
         <div className="glass-panel" style={{ 
           pointerEvents: 'auto', 
           width: '320px', 
           background: 'rgba(5, 7, 9, 0.85)',
           border: '1px solid var(--color-green-teal)',
           borderRadius: '4px',
           marginBottom: '10px'
         }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid rgba(0, 168, 107, 0.3)' }}>
              <div className="font-mono" style={{ color: 'var(--color-green-teal)', fontSize: '0.8rem', fontWeight: 'bold', letterSpacing: '1px' }}>
                REGIONAL TELEMETRY
              </div>
              <div className="font-mono text-red glow-red" style={{ fontSize: '0.65rem', fontWeight: 'bold', letterSpacing: '1px' }}>
                LIVE
              </div>
            </div>
            
            <div style={{ padding: '12px 16px' }}>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div className="font-mono text-muted" style={{ fontSize: '0.55rem', width: '40%' }}>ORIGIN</div>
                  <div className="font-mono" style={{ color: '#FF0033', fontSize: '0.55rem', width: '30%', textAlign: 'right' }}>LAUNCHED</div>
                  <div className="font-mono" style={{ color: 'var(--color-cyan)', fontSize: '0.55rem', width: '30%', textAlign: 'right' }}>INTERCEPTED</div>
               </div>
               
               {/* Telemetry Rows */}
               <TelemetryRow origin="IRAN (TEHRAN)" launched={4210} intercepted={955} originColor="#FF0033" />
               <TelemetryRow origin="QATAR (DOHA)" launched={177} intercepted={174} originColor="#D4AF37" />
               <TelemetryRow origin="YEMEN (HOUTHI)" launched={130} intercepted={100} originColor="#D4AF37" />
               <TelemetryRow origin="USA (CENTCOM)" launched={110} intercepted={110} originColor="var(--color-cyan)" />
               <TelemetryRow origin="SAUDI" launched={32} intercepted={32} originColor="var(--color-cyan)" />
               <TelemetryRow origin="BAHRAIN" launched={2} intercepted={2} originColor="var(--color-cyan)" />
               <TelemetryRow origin="UAE (DUBAI)" launched={147} intercepted={147} originColor="var(--color-cyan)" />
            </div>
         </div>

         {/* HEARTBEAT ARC (Bottom Center) - We position this absolutely to ensure perfect centering */}
         <div style={{
           position: 'absolute',
           bottom: '90px',
           left: '50%',
           transform: 'translateX(-50%)',
           display: 'flex',
           flexDirection: 'column',
           alignItems: 'center',
           pointerEvents: 'none'
         }}>
            <div className="font-mono" style={{ color: 'var(--color-green-teal)', fontSize: '0.8rem', letterSpacing: '2px', fontWeight: 'bold', marginBottom: '8px' }}>
              GEOPOLITICAL HEAT INDEX
            </div>
            
            <div style={{ 
              width: '180px', 
              height: '180px', 
              borderRadius: '50%', 
              border: '12px solid rgba(0, 229, 255, 0.1)',
              borderTopColor: 'var(--color-cyan)',
              borderRightColor: 'var(--color-cyan)',
              boxShadow: '0 0 30px rgba(0, 229, 255, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              background: 'rgba(5, 7, 9, 0.9)'
            }}>
              <div className="font-mono text-cyan" style={{ fontSize: '0.65rem', letterSpacing: '2px', opacity: 0.8 }}>HEARTBEAT</div>
              <div className="font-mono text-main glow-cyan" style={{ fontSize: '3.5rem', fontWeight: 'bold', lineHeight: '1' }}>{heartbeatScore}</div>
              <div className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>CONFLICT SCORE</div>
              <div className="text-cyan" style={{ fontSize: '1.2rem', marginTop: '4px' }}>〰️〰️</div>
            </div>
            
            {heartbeatScore > 95 && (
              <div className="font-mono glow-red" style={{ 
                color: '#FF0033', 
                fontSize: '0.65rem', 
                letterSpacing: '2px', 
                marginTop: '12px',
                border: '1px solid rgba(255,0,51,0.5)',
                padding: '4px 12px',
                background: 'rgba(255,0,51,0.1)'
              }}>
                CRITICAL IMMINENT THREAT 
              </div>
            )}
         </div>
      </div>

      {/* PREDICTIVE AI INTEL Box (Stretches across bottom) */}
      <div className="glass-panel" style={{ 
        width: '100%', 
        padding: '16px 24px',
        background: 'rgba(5, 7, 9, 0.85)',
        border: '1px solid rgba(0, 229, 255, 0.2)',
        pointerEvents: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="font-mono" style={{ color: 'var(--color-cyan)', fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1rem' }}>●</span> PREDICTIVE AI INTEL
            </div>
            <div className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>
              MODEL: GPT-4O-V2 // GEOPOL-SYNC
            </div>
         </div>
         
         <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <div className="font-mono text-muted" style={{ fontSize: '0.65rem', letterSpacing: '1px', marginBottom: '4px' }}>AVG MISSILES / 24H</div>
              <div className="font-mono text-main" style={{ fontSize: '1.8rem', fontWeight: 'bold', display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                452.5 <span className="text-red glow-red" style={{ fontSize: '0.7rem' }}>↑ 12.4%</span>
              </div>
            </div>
            
            <div style={{ flex: 1, margin: '0 40px', position: 'relative', top: '-8px' }}>
               <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', display: 'flex', position: 'relative' }}>
                 <div style={{ width: '40%', height: '100%', background: 'var(--color-cyan)', borderRadius: '2px 0 0 2px', boxShadow: '0 0 10px var(--color-cyan)' }}></div>
                 <div style={{ width: '15%', height: '100%', background: '#FF0033', boxShadow: '0 0 10px #FF0033' }}></div>
               </div>
               <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
                 <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>INCEPTION</span>
                 <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>PEAK ESCALATION</span>
                 <span className="font-mono text-muted" style={{ fontSize: '0.5rem', letterSpacing: '1px' }}>DE-ESCALATION ARCH</span>
               </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div className="font-mono text-muted" style={{ fontSize: '0.65rem', letterSpacing: '1px', marginBottom: '4px' }}>PREDICTIVE CONFLICT ARCH</div>
              <div className="font-mono text-cyan glow-cyan" style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>
                14.2 Days <span className="text-muted" style={{ fontSize: '0.7rem' }}>REM.</span>
              </div>
            </div>
         </div>

      </div>
    </div>
  );
};

const TelemetryRow = ({ origin, launched, intercepted, originColor }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
     <div className="font-mono" style={{ color: originColor, fontSize: '0.65rem', width: '40%', fontWeight: 'bold' }}>{origin}</div>
     <div className="font-mono" style={{ color: '#E0E0E0', fontSize: '0.75rem', width: '30%', textAlign: 'right' }}>{launched.toLocaleString()}</div>
     <div className="font-mono" style={{ color: 'var(--color-cyan)', fontSize: '0.75rem', width: '30%', textAlign: 'right' }}>{intercepted.toLocaleString()}</div>
  </div>
);

export default Indicators;
