-- First, clear out the conflicting policy name if it exists
DROP POLICY IF EXISTS "Enable read access for all users" ON "public"."security_alerts";
DROP POLICY IF EXISTS "Enable all access for all users" ON "public"."security_alerts";

-- Create a single global policy that allows ALL operations for anon/public
-- This allows our worker (using the anon key) to DELETE and UPDATE
CREATE POLICY "Enable all access for all users" ON "public"."security_alerts" 
FOR ALL 
TO anon, public, authenticated
USING (true) 
WITH CHECK (true);
