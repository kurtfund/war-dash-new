import React, { useState, useEffect } from 'react';

import { supabase } from '../lib/supabase';

const Tickers = [
  { symbol: 'AED=X', name: '$AED', type: 'CURRENCY', format: 'number', prefix: '$' },
  { symbol: 'CL=F', name: 'Crude Oil', type: 'ENERGY', format: 'number', prefix: '$' },
  { symbol: 'GC=F', name: 'Gold', type: 'SAFE HAVEN', prefix: '$' },
  { symbol: '^TASI.SR', name: 'Tadawul', type: 'MIDDLE EAST', format: 'number' },
  { symbol: '^GSPC', name: 'S&P 500', type: 'US MARKETS', format: 'number' },
  { symbol: 'AAPL', name: 'Apple', type: 'TECH', prefix: '$' },
  { symbol: '2222.SR', name: 'Saudi Aramco', type: 'ENERGY', format: 'number' }
];

const MarketPulse = () => {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const { data, error } = await supabase
          .from('security_alerts')
          .select('*')
          .eq('event_type', 'MARKET_DATA')
          .order('created_at', { ascending: false })
          .limit(1);

        if (error) throw error;
        
        let liveResults = {};
        if (data && data.length > 0) {
          try {
            liveResults = typeof data[0].raw_data === 'string' 
                          ? JSON.parse(data[0].raw_data) 
                          : data[0].raw_data || {};
          } catch (e) {
            console.error("Failed to parse market data JSON", e);
            liveResults = {};
          }
        }

        const results = Tickers.map((ticker) => {
          let fallbackPrice = '---';
          let fallbackChange = '---';
          let isPositive = true;

          // Default fallback data if live fetch fails
          if (ticker.name === '$AED') { fallbackPrice = '3.67'; fallbackChange = '0.00%'; isPositive = true; }
          else if (ticker.name === 'Crude Oil') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }
          else if (ticker.name === 'Gold') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }
          else if (ticker.name === 'Tadawul') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }
          else if (ticker.name === 'S&P 500') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }
          else if (ticker.name === 'Apple') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }
          else if (ticker.name === 'Saudi Aramco') { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }

          const liveData = liveResults[ticker.symbol];
          if (liveData) {
             const price = liveData.price;
             const change = liveData.change;

             if (ticker.prefix === '$') {
                 fallbackPrice = `$${price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
             } else {
                 fallbackPrice = price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
             }
             fallbackChange = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
             isPositive = change >= 0;
          }

          return { ...ticker, price: fallbackPrice, change: fallbackChange, isPositive: isPositive };
        });
        
        setMarketData(results);
      } catch (err) {
        console.error("Critical failure resolving market data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
    const interval = setInterval(fetchMarketData, 60000); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, minHeight: 0, overflowY: 'auto' }}>
      

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', borderBottom: '1px solid #1A1A1A', paddingBottom: '12px' }}>
        <div className="font-mono" style={{ color: '#D4AF37', fontSize: '0.85rem', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
          <span style={{ color: '#00FF41' }}>📈</span> STOCK WATCHLIST
        </div>
        <div className="font-mono text-muted" style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px', letterSpacing: '1px', border: '1px solid #333' }}>
          LIVE
        </div>
      </div>

      {loading ? (
        <div className="text-cyan font-mono" style={{ fontSize: '0.8rem', textAlign: 'center', padding: '20px' }}>
          INITIALIZING MARKET DATAFEED...
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {marketData.map((asset, index) => (
            <a 
              key={index} 
              href={`https://finance.yahoo.com/quote/${asset.symbol}`} 
              target="_blank" 
              rel="noreferrer"
              style={{ textDecoration: 'none' }}
            >
              <div style={{ 
                padding: '12px 16px', 
                background: 'rgba(5, 7, 9, 0.8)', 
                border: '1px solid #1A1A1A',
                borderRadius: '4px',
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                transition: 'border 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--color-cyan-dim)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#1A1A1A'}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#E0E0E0' }}>
                    {asset.name} <span style={{ color: '#666', fontSize: '0.7rem' }}>↗</span>
                  </span>
                  <span className="font-mono" style={{ fontSize: '0.6rem', letterSpacing: '1px', color: '#666' }}>
                    {asset.type}
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <span className="font-mono" style={{ fontSize: '1.0rem', fontWeight: 'bold', color: '#FFF' }}>
                    {asset.price}
                  </span>
                  <span className="font-mono" style={{ fontSize: '0.7rem', fontWeight: 'bold', color: asset.isPositive ? '#00FF41' : '#FF0033' }}>
                    {asset.change}
                  </span>
                </div>
              </div>
            </a>
          ))}
          
          {/* Add Watchlist Ticker Button */}
          <div style={{ 
            marginTop: '8px',
            padding: '16px', 
            border: '1px dashed #333',
            borderRadius: '4px',
            textAlign: 'center',
            cursor: 'pointer'
          }}>
            <span className="font-mono" style={{ color: '#666', fontSize: '0.75rem', letterSpacing: '1px' }}>
              + ADD WATCHLIST TICKER
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketPulse;
