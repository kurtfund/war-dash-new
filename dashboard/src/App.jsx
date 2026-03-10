import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import AlertFeed from './components/AlertFeed'
import Indicators from './components/Indicators'
import MapView from './components/MapView'
import { supabase } from './lib/supabase'

function App() {
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    // 1. Fetch initial data (last 250 events)
    const fetchAlerts = async () => {
      const { data, error } = await supabase
        .from('security_alerts')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(250)
      
      if (error) {
        console.error('Error fetching alerts:', error)
      } else {
        setAlerts(data || [])
      }
    }

    fetchAlerts()

    // 2. Subscribe to realtime inserts
    const channel = supabase
      .channel('public:security_alerts')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'security_alerts' }, (payload) => {
        console.log('New Alert Received:', payload.new)
        setAlerts((current) => [payload.new, ...current].slice(0, 250))
      })
      .subscribe((status, err) => {
        console.log('Realtime Subscription Status:', status);
        if (err) console.error('Realtime Error:', err);
      })

    return () => {
      supabase.removeChannel(channel)
    }
  }, [])

  return (
    <>
      <Header />
      <div className="dashboard-container">
        
        {/* Layer 1: The Map */}
        <MapView alerts={alerts} />
        
        {/* Layer 2: Left Panel (Feed) */}
        <AlertFeed alerts={alerts} />
        
        {/* Layer 3: Right Panel (Indicators) */}
        <Indicators alerts={alerts} />

      </div>
    </>
  )
}

export default App
