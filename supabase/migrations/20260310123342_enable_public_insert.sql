-- Allow anyone (even unauthenticated) to insert alerts during development
-- This is necessary because the environment only has an anon/publishable key
CREATE POLICY "Allow public insert access"
ON public.security_alerts
FOR INSERT
TO public, anon
WITH CHECK (true);
