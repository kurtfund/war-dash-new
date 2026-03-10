import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Helper to prevent crash if env vars are misconfigured on Render
const isConfigured = !!supabaseUrl && !!supabaseAnonKey

if (!isConfigured) {
  console.error("CRITICAL: Supabase credentials missing. The dashboard will not function.")
}

export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co', 
  supabaseAnonKey || 'placeholder'
)
