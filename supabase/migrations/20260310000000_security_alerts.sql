-- Enable PostGIS early for geospatial capabilities
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;

-- Create the primary security_alerts table
CREATE TABLE IF NOT EXISTS public.security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT,
    headline TEXT,
    event_type TEXT,
    country TEXT,
    location_name TEXT,
    coordinates GEOGRAPHY(Point,4326),
    deaths INTEGER DEFAULT 0,
    url TEXT,
    confidence FLOAT,
    raw_data JSONB
);

-- Establish Indexes for rapid geopolitical dashboard queries
CREATE INDEX IF NOT EXISTS idx_security_alerts_created_at ON public.security_alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_alerts_event_type ON public.security_alerts(event_type);

-- PostGIS GiST index for efficient spatial bounding box queries map side
CREATE INDEX IF NOT EXISTS idx_security_alerts_coordinates ON public.security_alerts USING GIST (coordinates);

-- Enable Supabase Realtime for the security_alerts table
-- By adding this table to the supabase_realtime publication, clients will receive live push events
begin;
  -- Remove the supabase_realtime publication if it exists to recreate it cleanly (optional step, but ensures safety)
  drop publication if exists supabase_realtime;
  create publication supabase_realtime;
commit;

alter publication supabase_realtime add table public.security_alerts;
