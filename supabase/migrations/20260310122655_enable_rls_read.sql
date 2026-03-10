-- Enable Row Level Security (should already be on from Phase 1, but ensuring it)
ALTER TABLE public.security_alerts ENABLE ROW LEVEL SECURITY;

-- Allow public read access to security_alerts
CREATE POLICY "Allow public read access"
ON public.security_alerts
FOR SELECT
TO public, anon
USING (true);
