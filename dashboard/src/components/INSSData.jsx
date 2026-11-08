import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const INSSData = () => {
  const [data, setData] = useState({
    regional_fatalities: '85',
    regional_injured: '1,110',
    iranian_fatalities: '3,536',
    iranian_injured: '26,578',
    israel_fatalities: '64',
    israel_injured: '9,365',
    uae_fatalities: '13',
    uae_injured: '233',
    kurdistan_fatalities: '20',
    kurdistan_injured: '121',
    us_fatalities: '13',
    us_injured: '370',
    kuwait_fatalities: '8',
    kuwait_injured: '187',
    qatar_fatalities: '8',
    qatar_injured: '35',
    oman_fatalities: '7',
    oman_injured: '18',
    syria_fatalities: '5',
    syria_injured: '15',
    pa_fatalities: '4',
    pa_injured: '7',
    bahrain_fatalities: '3',
    bahrain_injured: '60',
    saudi_fatalities: '3',
    saudi_injured: '29',
    french_fatalities: '1',
    french_injured: '6',
    jordan_fatalities: '0',
    jordan_injured: '29',
    irgc_operatives: '2,000',
    senior_officials: '50',
    launches_missiles: '1,527',
    launches_uavs: '4,816',
    iranian_missile_inventory: '2,500',
    iran_countries_targeted: '14',
    iran_strikes_us: '13,000',
    iran_strikes_israel: '10,800',
    iran_key_targets: [
      {name: "Ships in the Red Sea", count: "24"},
      {name: "US Military Bases", count: "16"},
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
             regional_fatalities: stats.regional_fatalities || '85',
             regional_injured: stats.regional_injured || '1,110',
             iranian_fatalities: stats.iranian_fatalities || '3,536',
             iranian_injured: stats.iranian_injured || '26,578',
             israel_fatalities: stats.israel_fatalities || '64',
             israel_injured: stats.israel_injured || '9,365',
             uae_fatalities: stats.uae_fatalities || '13',
             uae_injured: stats.uae_injured || '233',
             kurdistan_fatalities: stats.kurdistan_fatalities || '20',
             kurdistan_injured: stats.kurdistan_injured || '121',
             us_fatalities: stats.us_fatalities || '13',
             us_injured: stats.us_injured || '370',
             kuwait_fatalities: stats.kuwait_fatalities || '8',
             kuwait_injured: stats.kuwait_injured || '187',
             qatar_fatalities: stats.qatar_fatalities || '8',
             qatar_injured: stats.qatar_injured || '35',
             oman_fatalities: stats.oman_fatalities || '7',
             oman_injured: stats.oman_injured || '18',
             syria_fatalities: stats.syria_fatalities || '5',
             syria_injured: stats.syria_injured || '15',
             pa_fatalities: stats.pa_fatalities || '4',
             pa_injured: stats.pa_injured || '7',
             bahrain_fatalities: stats.bahrain_fatalities || '3',
             bahrain_injured: stats.bahrain_injured || '60',
             saudi_fatalities: stats.saudi_fatalities || '3',
             saudi_injured: stats.saudi_injured || '29',
             french_fatalities: stats.french_fatalities || '1',
             french_injured: stats.french_injured || '6',
             jordan_fatalities: stats.jordan_fatalities || '0',
             jordan_injured: stats.jordan_injured || '29',
             irgc_operatives: stats.irgc_operatives || stats.targeted_killings || '2,000',
             senior_officials: stats.senior_officials || '50',
             launches_missiles: stats.launches_missiles || '1,527',
             launches_uavs: stats.launches_uavs || '4,816',
             iranian_missile_inventory: stats.iranian_missile_inventory || '2,500',
             iran_countries_targeted: stats.iran_countries_targeted || '14',
             iran_strikes_us: stats.iran_strikes_us || '13,000',
             iran_strikes_israel: stats.iran_strikes_israel || '10,800',
             iran_key_targets: (stats.iran_key_targets && stats.iran_key_targets.length > 0) ? stats.iran_key_targets : [
                {name: "Ships in the Red Sea", count: "24"},
                {name: "US Military Bases", count: "16"},
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
  const actRegFat = data.regional_fatalities && data.regional_fatalities !== '...' ? safeNum(data.regional_fatalities).toLocaleString() : '85';
  const actRegInj = data.regional_injured && data.regional_injured !== '...' ? safeNum(data.regional_injured).toLocaleString() : '1,110';

  return (
    <div className="inss-container" style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1, // Take up remaining bottom half space sharing with MarketPulse
      minHeight: 0,
      marginTop: '10px',
      padding: '0 20px', // Increased margin to prevent clipping
      boxSizing: 'border-box'
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
            <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.42rem', letterSpacing: '0.5px', marginBottom: '2px'}}>M.E. CASUALTIES (EXCL. IRAN/ISR)</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1px' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Fatalities:</span>
              <span className="font-mono" style={{ color: '#ff3333', fontSize: '0.65rem', fontWeight: 'bold' }}>{actRegFat}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="font-mono" style={{ color: '#fff', fontSize: '0.55rem' }}>Injured:</span>
              <span className="font-mono" style={{ color: '#ffb333', fontSize: '0.65rem', fontWeight: 'bold' }}>{actRegInj}</span>
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
          paddingTop: '4px',
          maxHeight: '140px',
          overflowY: 'auto'
        }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.52rem', color: '#FFF' }} className="font-mono">
            <thead style={{ position: 'sticky', top: 0, background: 'rgba(5, 7, 9, 0.95)', zIndex: 1 }}>
              <tr style={{ color: 'rgba(255,255,255,0.5)', borderBottom: '1px solid rgba(0,255,255,0.2)', textAlign: 'left' }}>
                <th style={{ padding: '3px 4px', fontWeight: 'bold' }}>COUNTRY / THEATER</th>
                <th style={{ padding: '3px 4px', fontWeight: 'bold', textAlign: 'right' }}>FATALITIES</th>
                <th style={{ padding: '3px 4px', fontWeight: 'bold', textAlign: 'right' }}>INJURED</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'IRAN', f: data.iranian_fatalities, i: data.iranian_injured },
                { name: 'ISRAEL', f: data.israel_fatalities, i: data.israel_injured },
                { name: 'KURDISTAN', f: data.kurdistan_fatalities, i: data.kurdistan_injured },
                { name: 'UAE', f: data.uae_fatalities, i: data.uae_injured },
                { name: 'US MILITARY', f: data.us_fatalities, i: data.us_injured },
                { name: 'KUWAIT', f: data.kuwait_fatalities, i: data.kuwait_injured },
                { name: 'QATAR', f: data.qatar_fatalities, i: data.qatar_injured },
                { name: 'OMAN', f: data.oman_fatalities, i: data.oman_injured },
                { name: 'SYRIA', f: data.syria_fatalities, i: data.syria_injured },
                { name: 'PALESTINIAN AUT.', f: data.pa_fatalities, i: data.pa_injured },
                { name: 'BAHRAIN', f: data.bahrain_fatalities, i: data.bahrain_injured },
                { name: 'SAUDI ARABIA', f: data.saudi_fatalities, i: data.saudi_injured },
                { name: 'FRENCH FORCES', f: data.french_fatalities, i: data.french_injured },
                { name: 'JORDAN', f: data.jordan_fatalities, i: data.jordan_injured }
              ].map(country => (
                <tr key={country.name} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0, 20, 20, 0.4)' }}>
                  <td style={{ padding: '3px 4px', fontWeight: 'bold', letterSpacing: '0.5px' }}>{country.name}</td>
                  <td style={{ padding: '3px 4px', color: '#ff3333', textAlign: 'right', fontWeight: 'bold' }}>{country.f}</td>
                  <td style={{ padding: '3px 4px', color: '#ffb333', textAlign: 'right', fontWeight: 'bold' }}>{country.i}</td>
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
                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', padding: '1px 0' }}>
                  <span className="font-mono" style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.45rem', paddingRight: '4px', wordBreak: 'break-word', whiteSpace: 'normal' }}>
                    {target.name.replace('Rradar', 'Radar').replace(/^Ships in the\s*$/, 'Ships in the Red Sea')}
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
