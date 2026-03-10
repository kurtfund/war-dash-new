import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { supabase } from '../lib/supabase';
import { getHostname } from '../lib/utils';

// Disable default icon loading to use our custom svgs
delete L.Icon.Default.prototype._getIconUrl;

const getCustomIcon = (type) => {
  let color = '#00F2FF'; // Cyan default
  let iconHtml = '🔘'; 
  
  if (type === 'MISSILE' || type === 'AIRSTRIKE' || type === 'Casualty Report') {
    color = '#FF0033';
    iconHtml = type === 'MISSILE' ? '🚀' : type === 'AIRSTRIKE' ? '💥' : '💀';
  } else if (type === 'Disaster' || type === 'PROTEST') {
    color = '#FFD500';
    iconHtml = type === 'PROTEST' ? '🚩' : '⚠️';
  } else if (type === 'NAVAL') {
    iconHtml = '⚓';
  } else if (type === 'DRONE') {
    iconHtml = '🛩️';
    color = '#FF0033';
  }

  return L.divIcon({
    html: `
      <div style="
        background: rgba(10, 14, 18, 0.9);
        border: 2px solid ${color};
        box-shadow: 0 0 10px ${color};
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
      ">
        ${iconHtml}
      </div>
    `,
    className: 'custom-leaflet-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

const MapView = ({ alerts }) => {
  // Center on Middle East
  const center = [31.5, 45.0];
  const zoom = 5;

  return (
    <div className="map-container">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ width: '100%', height: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {alerts.map((alert, index) => {
          let lat, lon;

          // Priority 1: Raw decoupled floats from the JSONB (solves the Realtime WebSocket Hex issue)
          if (alert.raw_data && (alert.raw_data.lat !== undefined) && (alert.raw_data.lon !== undefined)) {
            lat = parseFloat(alert.raw_data.lat);
            lon = parseFloat(alert.raw_data.lon);
          } 
          // Priority 2: Standard PostGIS String (works for initial REST API fetches)
          else if (alert.coordinates && typeof alert.coordinates === 'string') {
            const match = alert.coordinates.match(/POINT\(([^ ]+) ([^ ]+)\)/);
            if (match) {
              lon = parseFloat(match[1]);
              lat = parseFloat(match[2]);
            }
          }

          if (isNaN(lat) || isNaN(lon)) return null;

          // Add a tiny random jitter to prevent perfect overlap
          // This ensures that if multiple alerts geocode to the same center-point, 
          // they are all visible/clickable on the map.
          const jitterLat = (Math.sin(index * 12.345) * 0.05);
          const jitterLon = (Math.cos(index * 54.321) * 0.05); 
          const displayLat = lat + jitterLat;
          const displayLon = lon + jitterLon;

          return (
            <Marker 
              key={alert.id} 
              position={[displayLat, displayLon]}
              icon={getCustomIcon(alert.event_type)}
            >
              <Popup className="dark-popup">
                <div style={{ fontFamily: 'var(--font-mono)' }}>
                  <div style={{ color: 'var(--color-cyan)', fontSize: '0.7rem', marginBottom: '8px' }}>
                    [{alert.event_type}] • {alert.country}
                  </div>
                  <a 
                    href={alert.url} 
                    target="_blank" 
                    rel="noreferrer" 
                    style={{ color: '#FFF', fontSize: '0.9rem', marginBottom: '12px', fontWeight: 'bold', textDecoration: 'none', display: 'block' }}
                  >
                    {alert.headline} 🔗
                  </a>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                    <span>{getHostname(alert.url)}</span>
                    {alert.deaths > 0 && <span className="text-red glow-red">💀 {alert.deaths}</span>}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapView;
