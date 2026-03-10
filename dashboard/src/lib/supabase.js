import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Helper to prevent crash if env vars are misconfigured on Render
const isConfigured = !!supabaseUrl && !!supabaseAnonKey

if (!isConfigured) {
  console.error("CRITICAL: Supabase credentials missing.")
  console.warn("REASON: Vite requires environment variables to start with 'VITE_'.")
  console.warn("FIX: Rename 'SUPABASE_URL' to 'VITE_SUPABASE_URL' in Render settings.")
}

export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co', 
  supabaseAnonKey || 'placeholder'
)
