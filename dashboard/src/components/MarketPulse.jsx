import React, { useState, useEffect } from 'react';

import { supabase } from '../lib/supabase';

const Tickers = [
  // Line 1: Crude Oil, Natural Gas
  { symbol: 'CL=F', name: 'Crude Oil', type: 'ENERGY', format: 'number', prefix: '$' },
  { symbol: 'NG=F', name: 'Nat Gas', type: 'ENERGY', format: 'number', prefix: '$' },
  // Line 2: Gold, USD Index
  { symbol: 'GC=F', name: 'Gold', type: 'SAFE HAVEN', prefix: '$' },
  { symbol: 'DX-Y.NYB', name: 'USD Index', type: 'CURRENCY', format: 'number', prefix: '' },
  // Line 3: VIX, S&P 500
  { symbol: '^VIX', name: 'VIX Vol.', type: 'INDEX', format: 'number' },
  { symbol: '^GSPC', name: 'S&P 500', type: 'US MARKETS', format: 'number' },
  // Line 4: Saudi Aramco, Tadawul
  { symbol: '2222.SR', name: 'Aramco', type: 'ENERGY', format: 'number' },
  { symbol: '^TASI.SR', name: 'Tadawul', type: 'MIDDLE EAST', format: 'number' },
  // Line 5: UAE DFM, AED
  { symbol: 'DFMGI.AE', name: 'DFM Index', type: 'UAE MARKETS', format: 'number' },
  { symbol: 'AED=X', name: '$AED', type: 'CURRENCY', format: 'number', prefix: '$' }
];

const MarketPulse = () => {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const { data, error } = await supabase
          .from('market_pulse_data')
          .select('*')
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
            console.error("Failed to parse market data JSON: Data unavailable");
            liveResults = {};
          }
        }

        const results = Tickers.map((ticker) => {
          let fallbackPrice = '---';
          let fallbackChange = '---';
          let isPositive = true;

          // Default fallback data if live fetch fails
          if (ticker.name === '$AED') { fallbackPrice = '3.67'; fallbackChange = '0.00%'; isPositive = true; }
          else { fallbackPrice = '---'; fallbackChange = '---'; isPositive = true; }

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
        console.error("Critical failure resolving market data: Data unavailable");
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
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {marketData.map((asset, index) => (
            <a 
              key={index} 
              href={`https://finance.yahoo.com/quote/${asset.symbol}`} 
              target="_blank" 
              rel="noreferrer"
              style={{ textDecoration: 'none' }}
            >
              <div style={{ 
                padding: '12px 14px', 
                background: 'rgba(5, 7, 9, 0.8)', 
                border: '1px solid #1A1A1A',
                borderRadius: '4px',
                display: 'flex', 
                flexDirection: 'column',
                justifyContent: 'space-between', 
                alignItems: 'flex-start',
                transition: 'border 0.2s',
                cursor: 'pointer',
                gap: '8px',
                height: '100%'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--color-cyan-dim)'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#1A1A1A'}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', width: '100%' }}>
                  <span className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#E0E0E0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {asset.name} <span style={{ color: '#666', fontSize: '0.6rem' }}>↗</span>
                  </span>
                  <span className="font-mono" style={{ fontSize: '0.6rem', letterSpacing: '0.5px', color: '#666', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {asset.type}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', width: '100%' }}>
                  <span className="font-mono" style={{ fontSize: '1.15rem', fontWeight: 'bold', color: '#FFF' }}>
                    {asset.price}
                  </span>
                  <span className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 'bold', color: asset.isPositive ? '#00FF41' : '#FF0033' }}>
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
