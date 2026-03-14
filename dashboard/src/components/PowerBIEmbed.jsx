import React from 'react';

const PowerBIEmbed = () => {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px', height: '100%', overflow: 'hidden' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px', borderBottom: '1px solid #1A1A1A', paddingBottom: '12px' }}>
        <div className="font-mono" style={{ color: 'var(--color-cyan)', fontSize: '0.85rem', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
          <span style={{ color: 'var(--color-red)' }}>📊</span> INSS CASUALTY DATA
        </div>
        <div className="font-mono text-muted" style={{ fontSize: '0.65rem', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: '4px', letterSpacing: '1px', border: '1px solid #333' }}>
          DATA STREAM
        </div>
      </div>

      {/* Embed Container */}
      <div style={{ 
        flex: 1, 
        background: 'rgba(5, 7, 9, 0.8)', 
        border: '1px solid #1A1A1A',
        borderRadius: '4px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <iframe
          title="INSS Data Report"
          width="100%"
          height="100%"
          src="https://app.powerbi.com/view?r=eyJrIjoiYmI3MzIzMTAtMTdjNC00NTY1LWFiM2YtNjI0NTk5MWEyYTI5IiwidCI6IjgwOGNmNGIzLTFhOTYtNDEzZi1iMDZiLTlkZTZjOThmNTQ2OSJ9"
          frameBorder="0"
          allowFullScreen={true}
          style={{ background: 'transparent' }}
        ></iframe>
      </div>
      
    </div>
  );
};

export default PowerBIEmbed;
