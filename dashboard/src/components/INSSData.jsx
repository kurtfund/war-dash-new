import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const INSSData = () => {
  const [data, setData] = useState({
    regional_fatalities: '...',
    regional_injured: '...',
    iranian_fatalities: '...',
    targeted_killings: '...',
    launches_missiles: '...',
    launches_uavs: '...',
    iranian_missile_inventory: '...',
    iran_countries_targeted: '...',
    iran_strikes_us: '...',
    iran_strikes_israel: '...'
  });
  const [lastUpdated, setLastUpdated] = useState('...');
  const [sourceUrl, setSourceUrl] = useState('https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9');

  useEffect(() => {
    const fetchINSSData = async () => {
      try {
        const { data: records, error } = await supabase
          .from('security_alerts')
          .select('headline, created_at, url')
          .eq('event_type', 'INSS_STATS')
          .order('created_at', { ascending: false })
          .limit(1);

        if (error) throw error;
        
        if (records && records.length > 0) {
          const stats = JSON.parse(records[0].headline);
          // Set to parsed data but stringified with commas if needed
          setData({
             regional_fatalities: stats.regional_fatalities || 'N/A',
             regional_injured: stats.regional_injured || 'N/A',
             iranian_fatalities: stats.iranian_fatalities || 'N/A',
             targeted_killings: stats.targeted_killings || 'N/A',
             launches_missiles: stats.launches_missiles || 'N/A',
             launches_uavs: stats.launches_uavs || 'N/A',
             iranian_missile_inventory: stats.iranian_missile_inventory || 'N/A',
             iran_countries_targeted: stats.iran_countries_targeted || 'N/A',
             iran_strikes_us: stats.iran_strikes_us || 'N/A',
             iran_strikes_israel: stats.iran_strikes_israel || 'N/A'
          });
          
          if (records[0].url) setSourceUrl(records[0].url);

          const date = new Date(records[0].created_at);
          setLastUpdated(`${date.toLocaleDateString()} ${date.toLocaleTimeString()} UTC`);
        }
      } catch (err) {
        console.error("Error fetching INSS data:", err);
      }
    };

    fetchINSSData();
    // Refresh less frequently since this is scraped data and updates slowly
    const interval = setInterval(fetchINSSData, 300000); // Every 5 minutes
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1, // Take up remaining bottom half space sharing with MarketPulse
      minHeight: 0,
      marginTop: '20px'
      }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '10px 0',
        borderBottom: '1px solid rgba(0, 255, 255, 0.2)',
        marginBottom: '10px',
        gap: '10px'
      }}>
        <div style={{
          padding: '2px 6px',
          background: 'rgba(0, 255, 255, 0.1)',
          border: '1px solid #00ffff',
          color: '#00ffff',
          fontSize: '0.65rem',
          fontWeight: 'bold',
          letterSpacing: '1px',
        }}>
          DATA STREAM
        </div>
        <div className="font-mono" style={{
          color: '#00ffff',
          fontSize: '0.9rem',
          fontWeight: 'bold',
          letterSpacing: '2px',
          textShadow: '0 0 10px rgba(0, 255, 255, 0.5)'
        }}>
          <a href={sourceUrl} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none', cursor: 'pointer' }}>
            INSS REGIONAL CASUALTIES ↗
          </a>
        </div>
        <div className="font-mono" style={{ marginLeft: 'auto', color: 'rgba(255,255,255,0.4)', fontSize: '0.7rem' }}>
          LAST SYNC: {lastUpdated}
        </div>
      </div>

      {/* Main Grid for Native UI */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '15px'
      }} className="hide-scrollbar">
        
        {/* ROW 1: Regional & Iranian Casualties */}
        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '8px 10px' }}>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '6px'}}>REGIONAL CASUALTIES</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Fatalities:</span>
            <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.regional_fatalities}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Injured:</span>
            <span className="font-mono" style={{ color: '#ffb333', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.regional_injured}</span>
          </div>
        </div>

        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '8px 10px' }}>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '6px'}}>IRANIAN CASUALTIES</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Fatalities:</span>
            <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.iranian_fatalities}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Targeted Killings:</span>
            <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.95rem', fontWeight: 'bold' }}>~{data.targeted_killings}</span>
          </div>
        </div>
        
        {/* ROW 2: Military Activity & Iranian Inventory */}
        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '8px 10px' }}>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '6px'}}>LAUNCHES TOWARD M.E.</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Missiles:</span>
            <span className="font-mono" style={{ color: '#ffb333', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.launches_missiles}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>UAVs:</span>
            <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.launches_uavs}</span>
          </div>
        </div>

        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '8px 10px' }}>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.6rem', letterSpacing: '1px', marginBottom: '6px'}}>IRANIAN THREAT VECTOR</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Missile Inventory:</span>
            <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.iranian_missile_inventory}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span className="font-mono" style={{ color: '#fff', fontSize: '0.75rem' }}>Countries Targeted:</span>
            <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.95rem', fontWeight: 'bold' }}>{data.iran_countries_targeted}</span>
          </div>
        </div>

        {/* Card: Operations */}
         <div style={{ gridColumn: 'span 2', border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '6px 8px' }}>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.55rem', letterSpacing: '1px', marginBottom: '4px'}}>STRIKES IN IRAN</div>
           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', textAlign: 'center' }}>
             <div>
                <div className="font-mono" style={{ color: '#fff', fontSize: '0.55rem', marginBottom: '1px' }}>American Strikes</div>
                <div className="font-mono" style={{ color: '#00ffff', fontSize: '0.8rem', fontWeight: 'bold' }}>{data.iran_strikes_us}</div>
             </div>
             <div>
                <div className="font-mono" style={{ color: '#fff', fontSize: '0.55rem', marginBottom: '1px' }}>Israeli Strikes</div>
                <div className="font-mono" style={{ color: '#00ffff', fontSize: '0.8rem', fontWeight: 'bold' }}>{data.iran_strikes_israel}</div>
             </div>
           </div>
        </div>

      </div>
    </div>
  );
};

export default INSSData;
