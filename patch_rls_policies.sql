-- Patches the isolated tables to allow inserts from your publishable (anon/authenticated) key
-- Run this in your Supabase SQL Editor

-- 1. Fix wam_official_data
DROP POLICY IF EXISTS "Allow service role insert to wam_official_data" ON public.wam_official_data;
CREATE POLICY "Allow all inserts to wam_official_data" ON public.wam_official_data AS PERMISSIVE FOR INSERT WITH CHECK (true);

-- 2. Fix inss_casualties_data
DROP POLICY IF EXISTS "Allow service role insert to inss_casualties_data" ON public.inss_casualties_data;
CREATE POLICY "Allow all inserts to inss_casualties_data" ON public.inss_casualties_data AS PERMISSIVE FOR INSERT WITH CHECK (true);

-- 3. Fix market_pulse_data
DROP POLICY IF EXISTS "Allow service role insert to market_pulse_data" ON public.market_pulse_data;
CREATE POLICY "Allow all inserts to market_pulse_data" ON public.market_pulse_data AS PERMISSIVE FOR INSERT WITH CHECK (true);
