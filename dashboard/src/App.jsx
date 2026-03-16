import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import AlertFeed from './components/AlertFeed'
import Indicators from './components/Indicators'
import MarketPulse from './components/MarketPulse'
import MapView from './components/MapView'
import LiveMediaBox from './components/LiveMediaBox'
import INSSData from './components/INSSData'
import { supabase } from './lib/supabase'

function App() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [isConfigured, setIsConfigured] = useState(true)

  useEffect(() => {
    // Check if we are using the placeholders from supabase.js
    const url = import.meta.env.VITE_SUPABASE_URL
    const key = import.meta.env.VITE_SUPABASE_ANON_KEY
    if (!url || !key || url.includes('placeholder')) {
      setIsConfigured(false)
      setLoading(false)
      return
    }

    // 1. Fetch initial data (last 250 events)
    const fetchAlerts = async () => {
      try {
        const { data, error } = await supabase
          .from('security_alerts')
          .select('*')
          .neq('event_type', 'MARKET_DATA')
          .order('created_at', { ascending: false })
          .limit(250)
        
        if (error) {
          console.error('Error fetching alerts:', error)
        } else {
          setAlerts(data || [])
        }
      } catch (err) {
        console.error('Fatal fetch error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()

    // 2. Subscribe to realtime inserts
    const channel = supabase
      .channel('public:security_alerts')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'security_alerts' }, (payload) => {
        setAlerts((current) => {
          if (payload.new.event_type === 'MARKET_DATA') return current;
          return [payload.new, ...current].slice(0, 250);
        })
      })
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  if (!isConfigured) {
    return (
      <div style={{ background: '#000', color: '#FF0033', height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px', textAlign: 'center', fontFamily: 'monospace' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>⚠️ CREDENTIALS MISSING</h1>
        <p style={{ fontSize: '1.2rem', maxWidth: '600px', lineHeight: '1.6' }}>
          The Dashboard cannot connect to Supabase. <br/><br/>
          Go to your <b>Render Static Site Settings</b> &rarr; <b>Environment</b> and add:<br/><br/>
          <code style={{ background: '#222', padding: '4px 8px', borderRadius: '4px', margin: '5px' }}>VITE_SUPABASE_URL</code><br/>
          <code style={{ background: '#222', padding: '4px 8px', borderRadius: '4px', margin: '5px' }}>VITE_SUPABASE_ANON_KEY</code>
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div style={{ background: '#000', color: '#00F2FF', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'monospace' }}>
        <div style={{ border: '2px dashed #00F2FF', padding: '20px', letterSpacing: '2px' }}>
          ESTABLISHING SECURE CONNECTION...
        </div>
      </div>
    )
  }

  return (
    <>
      <Header />
      <div className="dashboard-container">
        
        {/* Column 1: Left Panel (Feed) 25% */}
        <div className="dashboard-panel">
          <AlertFeed alerts={alerts} />
        </div>

        {/* Column 2: The Map 50% */}
        <div className="dashboard-panel map-container">
          <MapView alerts={alerts} />
          <Indicators alerts={alerts} />
        </div>
        {/* Column 3: Right Panel (Market Pulse + Data) 25% */}
        <div className="dashboard-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <MarketPulse />
          <div style={{ borderTop: '1px solid #1A1A1A', flex: 1, minHeight: 0, display: 'flex' }}>
            <INSSData />
          </div>
          {/* Render INTEL FEED button naturally at the bottom of this column */}
          <LiveMediaBox />
        </div>

      </div>
    </>
  )
}

export default App
// Trigger Render Build
