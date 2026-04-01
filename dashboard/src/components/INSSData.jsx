import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const INSSData = () => {
  const [data, setData] = useState({
    regional_fatalities: '...',
    regional_injured: '...',
    iranian_fatalities: '...',
    irgc_operatives: '...',
    senior_officials: '...',
    launches_missiles: '...',
    launches_uavs: '...',
    iranian_missile_inventory: '...',
    iran_countries_targeted: '...',
    iran_strikes_us: '...',
    iran_strikes_israel: '...',
    iranian_injured: '...',
    israel_fatalities: '...',
    israel_injured: '...',
    lebanon_fatalities: '...',
    lebanon_injured: '...',
    us_fatalities: '...',
    us_injured: '...',
    bahrain_fatalities: '...',
    bahrain_injured: '...',
    kuwait_fatalities: '...',
    kuwait_injured: '...',
    saudi_fatalities: '...',
    saudi_injured: '...',
    qatar_fatalities: '...',
    qatar_injured: '...',
    iran_key_targets: []
  });
  const [lastUpdated, setLastUpdated] = useState('...');
  const [sourceUrl, setSourceUrl] = useState('https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9');

  useEffect(() => {
    const fetchINSSData = async () => {
      try {
        const { data: records, error } = await supabase
          .from('inss_casualties_data')
          .select('stats, created_at, source_url')
          .order('created_at', { ascending: false })
          .limit(1);

        if (error) throw error;
        
        if (records && records.length > 0) {
          const stats = typeof records[0].stats === 'string' 
            ? JSON.parse(records[0].stats) 
            : records[0].stats;
          setData({
             regional_fatalities: stats.regional_fatalities || 'N/A',
             regional_injured: stats.regional_injured || 'N/A',
             iranian_fatalities: stats.iranian_fatalities || 'N/A',
             irgc_operatives: stats.irgc_operatives || stats.targeted_killings || 'N/A',
             senior_officials: stats.senior_officials || '50',
             launches_missiles: stats.launches_missiles || 'N/A',
             launches_uavs: stats.launches_uavs || 'N/A',
             iranian_missile_inventory: stats.iranian_missile_inventory || 'N/A',
             iran_countries_targeted: stats.iran_countries_targeted || 'N/A',
             iran_strikes_us: stats.iran_strikes_us || 'N/A',
             iran_strikes_israel: stats.iran_strikes_israel || 'N/A',
             iranian_injured: stats.iranian_injured || 'N/A',
             israel_fatalities: stats.israel_fatalities || 'N/A',
             israel_injured: stats.israel_injured || 'N/A',
             lebanon_fatalities: stats.lebanon_fatalities || 'N/A',
             lebanon_injured: stats.lebanon_injured || 'N/A',
             us_fatalities: stats.us_fatalities || 'N/A',
             us_injured: stats.us_injured || 'N/A',
             bahrain_fatalities: stats.bahrain_fatalities || 'N/A',
             bahrain_injured: stats.bahrain_injured || 'N/A',
             kuwait_fatalities: stats.kuwait_fatalities || 'N/A',
             kuwait_injured: stats.kuwait_injured || 'N/A',
             saudi_fatalities: stats.saudi_fatalities || 'N/A',
             saudi_injured: stats.saudi_injured || 'N/A',
             qatar_fatalities: stats.qatar_fatalities || 'N/A',
             qatar_injured: stats.qatar_injured || 'N/A',
             iran_key_targets: stats.iran_key_targets || [
                {name: "Ships in the Red Sea", count: "24"},
                {name: "US Military Bases", count: "14"},
                {name: "Airports", count: "6"},
                {name: "Missions Foreign", count: "6"},
                {name: "Oil&Fuel facilities", count: "6"},
                {name: "Radar", count: "6"},
                {name: "Hotels", count: "4"},
                {name: "Satcom", count: "4"},
                {name: "Data Centers", count: "3"},
                {name: "Ports", count: "3"},
                {name: "Aluminum Plants", count: "2"},
                {name: "Gas Facilities", count: "2"}
             ]
          });
          
          if (records[0].source_url) setSourceUrl(records[0].source_url);

          const date = new Date(records[0].created_at);
          setLastUpdated(`${date.toLocaleDateString()} ${date.toLocaleTimeString()} UTC`);
        }
      } catch (err) {
        console.error("Error fetching INSS data: Data unavailable");
      }
    };

    fetchINSSData();
    // Refresh less frequently since this is scraped data and updates slowly
    const interval = setInterval(fetchINSSData, 300000); // Every 5 minutes
    
    return () => clearInterval(interval);
  }, []);

  const safeNum = (val) => Number(String(val).replace(/,/g, '')) || 0;
  const actRegFat = data.iranian_fatalities !== '...' ? safeNum(data.iranian_fatalities) + safeNum(data.us_fatalities) + safeNum(data.israel_fatalities) + safeNum(data.lebanon_fatalities) + safeNum(data.saudi_fatalities) + safeNum(data.kuwait_fatalities) + safeNum(data.bahrain_fatalities) + safeNum(data.qatar_fatalities) : '...';
  const actRegInj = data.iranian_injured !== '...' ? safeNum(data.iranian_injured) + safeNum(data.us_injured) + safeNum(data.israel_injured) + safeNum(data.lebanon_injured) + safeNum(data.saudi_injured) + safeNum(data.kuwait_injured) + safeNum(data.bahrain_injured) + safeNum(data.qatar_injured) : '...';

  return (
    <div className="inss-container" style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1, // Take up remaining bottom half space sharing with MarketPulse
      minHeight: 0,
      marginTop: '10px',
      padding: '0 10px' // Margin to prevent clipping
      }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '2px 0',
        borderBottom: '1px solid rgba(0, 255, 255, 0.2)',
        marginBottom: '6px',
        gap: '6px'
      }}>
        <div style={{
          padding: '2px 4px',
          background: 'rgba(0, 255, 255, 0.1)',
          border: '1px solid #00ffff',
          color: '#00ffff',
          fontSize: '0.5rem',
          fontWeight: 'bold',
          letterSpacing: '1px',
        }}>
          DATA STREAM
        </div>
        <div className="font-mono" style={{
          color: '#00ffff',
          fontSize: '0.65rem',
          fontWeight: 'bold',
          letterSpacing: '1px',
          textShadow: '0 0 10px rgba(0, 255, 255, 0.5)',
          zIndex: 10
        }}>
          <a href={sourceUrl || '#'} target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none', cursor: 'pointer', pointerEvents: 'auto', position: 'relative' }}>
            INSS MIDDLE EAST CASUALTIES ↗
          </a>
        </div>
        <div className="font-mono" style={{ marginLeft: 'auto', color: 'rgba(255,255,255,0.4)', fontSize: '0.45rem', textAlign: 'right', lineHeight: '1.2' }}>
          LAST SYNC:<br/>{lastUpdated}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'hidden' }}>
        {/* Main Grid for Native UI */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '4px',
          alignContent: 'start'
        }}>
          
          {/* ROW 1: Regional & Iranian Casualties */}
          <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '2px 4px' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px', marginBottom: '2px'}}>M.E. CASUALTIES</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1px' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Fatalities:</span>
              <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.65rem', fontWeight: 'bold' }}>{actRegFat.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Injured:</span>
              <span className="font-mono" style={{ color: '#ffb333', fontSize: '0.65rem', fontWeight: 'bold' }}>{actRegInj.toLocaleString()}</span>
            </div>
          </div>

          <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '2px 4px', display: 'flex', flexDirection: 'column' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px', marginBottom: '2px'}}>IRANIAN CASUALTIES</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Fatalities:</span>
              <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.7rem', fontWeight: 'bold' }}>{data.iranian_fatalities}</span>
            </div>
            <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '2px', paddingTop: '4px', borderTop: '1px solid rgba(255, 51, 51, 0.2)' }}>
              <div className="font-mono" style={{ color: '#ff3333', fontSize: '0.45rem', fontWeight: 'bold' }}>Elimination of IRGC Operatives</div>
              <div className="font-mono" style={{ color: '#ff3333', fontSize: '0.65rem', fontWeight: 'bold', lineHeight: '1' }}>
                ~{data.irgc_operatives} <span style={{fontSize: '0.45rem', fontWeight: 'normal', color: 'rgba(255,255,255,0.7)'}}>(~{data.senior_officials} senior officials)</span>
              </div>
              <div className="font-mono" style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.35rem' }}>The data are based on IDF reports</div>
            </div>
          </div>
          
          {/* ROW 2: Military Activity & Iranian Inventory */}
          <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '2px 4px' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px', marginBottom: '1px'}}>LAUNCHES TOWARD MIDDLE EAST</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0px' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Missiles:</span>
              <span className="font-mono" style={{ color: '#ffb333', fontSize: '0.7rem', fontWeight: 'bold' }}>{data.launches_missiles}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>UAVs:</span>
              <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.7rem', fontWeight: 'bold' }}>{data.launches_uavs}</span>
            </div>
          </div>

          <div style={{ border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '2px 4px' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px', marginBottom: '1px'}}>IRANIAN THREAT VECTOR</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0px' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Missile Inventory:</span>
              <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.7rem', fontWeight: 'bold' }}>{data.iranian_missile_inventory}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Countries Targeted:</span>
              <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.7rem', fontWeight: 'bold' }}>{data.iran_countries_targeted}</span>
            </div>
          </div>

          {/* Card: Operations */}
          <div style={{ gridColumn: 'span 2', border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)', padding: '2px 4px' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.4rem', letterSpacing: '1px', marginBottom: '1px'}}>STRIKES IN IRAN</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px', textAlign: 'center' }}>
              <div>
                  <div className="font-mono" style={{ color: '#fff', fontSize: '0.4rem', margin: '0' }}>American Strikes</div>
                  <div className="font-mono" style={{ color: '#00ffff', fontSize: '0.55rem', fontWeight: 'bold' }}>{data.iran_strikes_us}</div>
              </div>
              <div>
                  <div className="font-mono" style={{ color: '#fff', fontSize: '0.4rem', margin: '0' }}>Israeli Strikes</div>
                  <div className="font-mono" style={{ color: '#00ffff', fontSize: '0.55rem', fontWeight: 'bold' }}>{data.iran_strikes_israel}</div>
              </div>
            </div>
          </div>

        </div>

        {/* Country Casualties Table */}
        <div style={{
          marginTop: '6px',
          paddingTop: '6px',
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.55rem', color: '#FFF' }} className="font-mono">
            <thead>
              <tr style={{ color: 'rgba(255,255,255,0.5)', borderBottom: '1px solid rgba(0,255,255,0.2)', textAlign: 'left' }}>
                <th style={{ padding: '4px', fontWeight: 'bold' }}>COUNTRY</th>
                <th style={{ padding: '4px', fontWeight: 'bold', textAlign: 'right' }}>FATALITIES</th>
                <th style={{ padding: '4px', fontWeight: 'bold', textAlign: 'right' }}>INJURED</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'IRAN', f: data.iranian_fatalities, i: data.iranian_injured },
                { name: 'US', f: data.us_fatalities, i: data.us_injured },
                { name: 'ISRAEL', f: data.israel_fatalities, i: data.israel_injured },
                { name: 'LEBANON', f: data.lebanon_fatalities, i: data.lebanon_injured },
                { name: 'SAUDI AR', f: data.saudi_fatalities, i: data.saudi_injured },
                { name: 'KUWAIT', f: data.kuwait_fatalities, i: data.kuwait_injured },
                { name: 'BAHRAIN', f: data.bahrain_fatalities, i: data.bahrain_injured },
                { name: 'QATAR', f: data.qatar_fatalities, i: data.qatar_injured }
              ].map(country => (
                <tr key={country.name} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0, 20, 20, 0.4)' }}>
                  <td style={{ padding: '4px 6px', fontWeight: 'bold', letterSpacing: '1px' }}>{country.name}</td>
                  <td style={{ padding: '4px 6px', color: '#ff3333', textAlign: 'right', fontWeight: 'bold' }}>{country.f}</td>
                  <td style={{ padding: '4px 6px', color: '#ffb333', textAlign: 'right', fontWeight: 'bold' }}>{country.i}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Key Targets Table */}
        {data.iran_key_targets && data.iran_key_targets.length > 0 && (
          <div style={{ marginTop: '6px', paddingTop: '4px', borderTop: '1px solid rgba(0, 255, 255, 0.2)' }}>
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px', marginBottom: '2px'}}>
              KEY TARGETS STRUCK BY IRAN
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', columnGap: '8px', rowGap: '1px' }}>
              {data.iran_key_targets.map((target, idx) => (
                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <span className="font-mono" style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.45rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {target.name}
                  </span>
                  <span className="font-mono" style={{ color: '#00ffff', fontSize: '0.55rem', fontWeight: 'bold' }}>
                    {target.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default INSSData;
