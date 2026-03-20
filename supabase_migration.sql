-- Migration script to create isolated tables for UI sections
-- Run this in your Supabase SQL Editor

-- 1. WAM Official Data Table
CREATE TABLE IF NOT EXISTS public.wam_official_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    url TEXT,
    headline TEXT,
    missiles INTEGER DEFAULT 0,
    cruise INTEGER DEFAULT 0,
    uavs INTEGER DEFAULT 0,
    raw_data JSONB
);

-- Enable RLS and create policy (allow read access for frontend)
ALTER TABLE public.wam_official_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read access to wam_official_data" ON public.wam_official_data FOR SELECT USING (true);
CREATE POLICY "Allow service role insert to wam_official_data" ON public.wam_official_data AS PERMISSIVE FOR INSERT TO service_role WITH CHECK (true);

-- 2. INSS Casualties Data Table
CREATE TABLE IF NOT EXISTS public.inss_casualties_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    source_url TEXT,
    stats JSONB NOT NULL
);

ALTER TABLE public.inss_casualties_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read access to inss_casualties_data" ON public.inss_casualties_data FOR SELECT USING (true);
CREATE POLICY "Allow service role insert to inss_casualties_data" ON public.inss_casualties_data AS PERMISSIVE FOR INSERT TO service_role WITH CHECK (true);

-- 3. Market Pulse Data Table
CREATE TABLE IF NOT EXISTS public.market_pulse_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    raw_data JSONB NOT NULL
);

ALTER TABLE public.market_pulse_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read access to market_pulse_data" ON public.market_pulse_data FOR SELECT USING (true);
CREATE POLICY "Allow service role insert to market_pulse_data" ON public.market_pulse_data AS PERMISSIVE FOR INSERT TO service_role WITH CHECK (true);

-- Optional: Clean up old data from security_alerts to prevent clutter (Run with caution)
-- DELETE FROM public.security_alerts WHERE event_type IN ('OFFICIAL_SUMMARY', 'INSS_STATS', 'MARKET_DATA');
