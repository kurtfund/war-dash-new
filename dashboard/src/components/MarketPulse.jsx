import React, { useState, useEffect } from 'react';

const Tickers = [
  { symbol: 'CL=F', name: 'WTI Crude', type: 'ENERGY' },
  { symbol: 'NG=F', name: 'NatGas', type: 'ENERGY' },
  { symbol: 'GC=F', name: 'Gold', type: 'SAFE HAVEN' },
  { symbol: 'BTC-USD', name: 'BITCOIN', type: 'CRYPTO' },
  { symbol: '^GSPC', name: 'S&P 500', type: 'EQUITY' }
];

const MarketPulse = () => {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const results = await Promise.all(Tickers.map(async (ticker) => {
          const targetUrl = encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${ticker.symbol}?interval=1d&range=1d`);
          // Using allorigins as a reliable public CORS proxy for frontend fetching
          const proxyUrl = `https://api.allorigins.win/get?url=${targetUrl}`;
          
          const response = await fetch(proxyUrl);
          if (!response.ok) throw new Error("Proxy fetch failed");
          
          const proxyData = await response.json();
          const data = JSON.parse(proxyData.contents);
          
          if (data.chart.result && data.chart.result.length > 0) {
            const meta = data.chart.result[0].meta;
            const currentPrice = meta.regularMarketPrice;
            const prevClose = meta.previousClose;
            const changeRaw = currentPrice - prevClose;
            const changePercent = (changeRaw / prevClose) * 100;
            
            return {
              ...ticker,
              price: currentPrice.toFixed(2),
              change: changePercent.toFixed(2),
              isPositive: changePercent >= 0
            };
          }
          return { ...ticker, price: '---', change: '---', isPositive: true };
        }));
        
        setMarketData(results);
      } catch (err) {
        console.error("Failed to fetch market data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
    const interval = setInterval(fetchMarketData, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', borderBottom: '1px solid #1A1A1A', paddingBottom: '12px' }}>
        <div className="text-yellow font-mono" style={{ fontSize: '0.85rem', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>📈</span> MARKET PULSE
        </div>
        <div style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.1)', padding: '2px 6px', borderRadius: '4px', letterSpacing: '1px' }}>
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
            <div key={index} className="glass-panel" style={{ padding: '12px 16px', background: 'rgba(10, 14, 18, 0.6)', border: '1px solid #1A1A1A' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span className="font-mono text-main" style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{asset.name} ↗</span>
                  <span className="font-mono text-muted" style={{ fontSize: '0.6rem', letterSpacing: '1px' }}>{asset.type}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <span className="font-mono text-main" style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{asset.price}</span>
                  <span className={`font-mono ${asset.isPositive ? 'text-cyan' : 'text-red'}`} style={{ fontSize: '0.75rem', fontWeight: 'bold' }}>
                    {asset.isPositive ? '+' : ''}{asset.change}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MarketPulse;
