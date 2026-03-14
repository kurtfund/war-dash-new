import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const INSSData = () => {
  const [data, setData] = useState({
    israel_fatalities: '...',
    israel_injured: '...',
    lebanon_fatalities: '...',
    lebanon_injured: '...',
    displaced_israel: '...',
    displaced_lebanon: '...',
    iran_strikes_us: '...',
    iran_strikes_israel: '...',
    targeted_killings: '...'
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
             israel_fatalities: stats.israel_fatalities || 'N/A',
             israel_injured: stats.israel_injured || 'N/A',
             lebanon_fatalities: stats.lebanon_fatalities || 'N/A',
             lebanon_injured: stats.lebanon_injured || 'N/A',
             displaced_israel: stats.displaced_israel || 'N/A',
             displaced_lebanon: stats.displaced_lebanon || 'N/A',
             iran_strikes_us: stats.iran_strikes_us || 'N/A',
             iran_strikes_israel: stats.iran_strikes_israel || 'N/A',
             targeted_killings: stats.targeted_killings || 'N/A'
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
        <div style={{
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
        <div style={{ marginLeft: 'auto', color: 'rgba(255,255,255,0.4)', fontSize: '0.7rem' }}>
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
        
        {/* Card: Israel */}
        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '15px' }}>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem', letterSpacing: '2px', marginBottom: '10px'}}>ISRAEL TOTALS</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Fatalities:</span>
            <span style={{ color: '#ff3333', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.israel_fatalities}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Injured:</span>
            <span style={{ color: '#ffb333', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.israel_injured}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Displaced:</span>
            <span style={{ color: '#00ffff', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.displaced_israel}</span>
          </div>
        </div>

        {/* Card: Lebanon */}
        <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '15px' }}>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem', letterSpacing: '2px', marginBottom: '10px'}}>LEBANON TOTALS</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Fatalities:</span>
            <span style={{ color: '#ff3333', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.lebanon_fatalities}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Injured:</span>
            <span style={{ color: '#ffb333', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.lebanon_injured}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#fff', fontSize: '0.9rem' }}>Displaced:</span>
            <span style={{ color: '#00ffff', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.displaced_lebanon}</span>
          </div>
        </div>
        
        {/* Card: Operations */}
         <div style={{ gridColumn: 'span 2', border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '15px' }}>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem', letterSpacing: '2px', marginBottom: '10px'}}>OPERATIONAL METRICS</div>
           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', textAlign: 'center' }}>
             <div>
                <div style={{ color: '#fff', fontSize: '0.8rem', marginBottom: '5px' }}>US Strikes (Iran)</div>
                <div style={{ color: '#00ffff', fontSize: '1.5rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.iran_strikes_us}</div>
             </div>
             <div>
                <div style={{ color: '#fff', fontSize: '0.8rem', marginBottom: '5px' }}>IDF Strikes (Iran)</div>
                <div style={{ color: '#00ffff', fontSize: '1.5rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.iran_strikes_israel}</div>
             </div>
             <div>
                <div style={{ color: '#fff', fontSize: '0.8rem', marginBottom: '5px' }}>Targeted Killings</div>
                <div style={{ color: '#ff3333', fontSize: '1.5rem', fontFamily: 'monospace', fontWeight: 'bold' }}>{data.targeted_killings}</div>
             </div>
           </div>
        </div>

      </div>
    </div>
  );
};

export default INSSData;
