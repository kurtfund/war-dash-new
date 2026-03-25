import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { supabase } from '../lib/supabase';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function PropertyChart() {
  const [data, setData] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [trend, setTrend] = useState(0);

  useEffect(() => {
    async function fetchData() {
      // Fetch from Supabase
      const { data: dbData, error } = await supabase
        .from('dld_market_data')
        .select('*')
        .order('id', { ascending: true }); 

      if (!error && dbData && dbData.length > 0) {
        // Format data for Recharts
        const formatted = dbData.map(d => ({
          name: d.month_label,
          price: parseFloat(d.price_sqft)
        }));
        
        setData(formatted);
        
        // Calculate Trend
        if (formatted.length >= 2) {
          const latest = formatted[formatted.length - 1].price;
          const prev = formatted[formatted.length - 2].price;
          setCurrentPrice(latest);
          setTrend(((latest - prev) / prev) * 100);
        } else if (formatted.length === 1) {
          setCurrentPrice(formatted[0].price);
          setTrend(0);
        }
      } else {
        // Fallback Mock Data while backend syncs
        const mock = [
          { name: 'Aug', price: 1080 },
          { name: 'Sep', price: 1100 },
          { name: 'Oct', price: 1120 },
          { name: 'Nov', price: 1135 },
          { name: 'Dec', price: 1125 },
          { name: 'Jan', price: 1150 },
          { name: 'Feb', price: 1180 }
        ];
        setData(mock);
        setCurrentPrice(1180);
        setTrend(2.6);
      }
    }
    
    fetchData();
    const interval = setInterval(fetchData, 300000); // 5 mins
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      borderBottom: '1px solid rgba(0, 255, 255, 0.2)',
      paddingBottom: '4px',
      marginBottom: '4px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
        <div>
          <div className="font-mono" style={{ color: '#00ffff', fontSize: '0.65rem', letterSpacing: '1px', fontWeight: 'bold' }}>
            <a href="https://dubailand.gov.ae/en/open-data/real-estate-data" target="_blank" rel="noreferrer" style={{ color: 'inherit', textDecoration: 'none', cursor: 'pointer' }}>
              DUBAI REAL ESTATE TREND &nbsp;↗
            </a>
          </div>
          <div className="font-mono" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.45rem', letterSpacing: '1px' }}>
            AVERAGE PRICE PER SQFT (AED)
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="font-mono" style={{ color: '#fff', fontSize: '0.8rem', fontWeight: 'bold' }}>
            AED {currentPrice.toLocaleString()}
          </div>
          <div className="font-mono" style={{ 
            color: trend >= 0 ? '#00ff88' : '#ff3333', 
            fontSize: '0.55rem', 
            display: 'flex', 
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: '4px'
          }}>
            {trend >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {Math.abs(trend).toFixed(2)}% MoM
          </div>
        </div>
      </div>

      <div style={{ height: '40px', width: '100%', border: '1px solid rgba(0, 255, 255, 0.1)', background: 'rgba(0,0,0,0.5)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ffff" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#00ffff" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Tooltip 
              contentStyle={{ background: 'rgba(0,0,0,0.9)', border: '1px solid #00ffff', borderRadius: '4px', padding: '4px' }}
              itemStyle={{ color: '#00ffff', fontSize: '0.6rem', fontFamily: 'monospace' }}
              labelStyle={{ color: '#fff', fontSize: '0.5rem', fontFamily: 'monospace' }}
              formatter={(value) => [`AED ${value}`, 'Price/SqFt']}
            />
            <Area type="monotone" dataKey="price" stroke="#00ffff" strokeWidth={1} fillOpacity={1} fill="url(#colorPrice)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
