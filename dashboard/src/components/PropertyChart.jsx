import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

export default function PropertyChart() {
  const [dxbPrice, setDxbPrice] = useState('---');
  const [dxbChange, setDxbChange] = useState('---');
  const [dxbPositive, setDxbPositive] = useState(true);

  useEffect(() => {
    async function fetchData() {
      // Dubai data
      const { data: dbData, error } = await supabase
        .from('dld_market_data')
        .select('*')
        .order('id', { ascending: true }); 

      if (!error && dbData && dbData.length >= 2) {
        const latest = parseFloat(dbData[dbData.length - 1].price_sqft);
        const prev = parseFloat(dbData[dbData.length - 2].price_sqft);
        const trend = ((latest - prev) / prev) * 100;
        setDxbPrice(`AED ${latest.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}`);
        setDxbChange(`${trend > 0 ? '+' : ''}${trend.toFixed(2)}%`);
        setDxbPositive(trend >= 0);
      } else {
        // Fallback
        setDxbPrice(`AED 1,180`);
        setDxbChange(`+2.60%`);
        setDxbPositive(true);
      }
    }
    
    fetchData();
    const interval = setInterval(fetchData, 300000); // 5 mins
    return () => clearInterval(interval);
  }, []);

  const Card = ({ name, type, price, change, isPositive, url }) => (
    <a href={url} target="_blank" rel="noreferrer" style={{ textDecoration: 'none' }}>
      <div style={{ 
        padding: '4px 8px', 
        background: 'rgba(5, 7, 9, 0.8)', 
        border: '1px solid #1A1A1A',
        borderRadius: '3px',
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        transition: 'border 0.2s',
        cursor: 'pointer',
        gap: '2px',
        height: 'auto'
      }}
      onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--color-cyan-dim)'}
      onMouseLeave={(e) => e.currentTarget.style.borderColor = '#1A1A1A'}
      >
        <div style={{ display: 'flex', flexDirection: 'row', gap: '4px', alignItems: 'baseline', width: '100%', justifyContent: 'space-between' }}>
          <span className="font-mono" style={{ fontSize: '0.7rem', fontWeight: 'bold', color: '#E0E0E0' }}>
            {name} <span style={{ color: '#666', fontSize: '0.55rem' }}>↗</span>
          </span>
          <span className="font-mono" style={{ fontSize: '0.45rem', color: '#666' }}>
            {type}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', width: '100%', justifyContent: 'space-between', marginTop: '2px' }}>
          <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#FFF' }}>
            {price}
          </span>
          <span className="font-mono" style={{ fontSize: '0.65rem', fontWeight: 'bold', color: change === 'N/A' ? '#666' : (isPositive ? '#00FF41' : '#FF0033') }}>
            {change}
          </span>
        </div>
      </div>
    </a>
  );

  return (
    <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'minmax(0, 1fr)', 
        gap: '6px', 
        padding: '0 10px',
        marginBottom: '10px'
    }}>
      <Card 
        name="Dubai RE" 
        type="REAL ESTATE" 
        price={dxbPrice} 
        change={dxbChange} 
        isPositive={dxbPositive} 
        url="https://dubailand.gov.ae/en/open-data/real-estate-data" 
      />
    </div>
  );
}
