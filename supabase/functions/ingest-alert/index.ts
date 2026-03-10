import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const KEYWORDS = {
  "event_types": {
    "Airstrike": ["airstrike", "air strike", "bombing", "missile", "rocket", "drone strike", "shelling"],
    "Military Activity": ["clashes", "gunfire", "infantry", "tank", "armored", "convoy", "skirmish", "raid"],
    "Naval Incident": ["warship", "frigate", "destroyer", "naval", "maritime", "hijack", "vessel", "cargo ship"],
    "Protest": ["protest", "demonstration", "riot", "rally", "uprising", "clash with police"],
    "Disaster": ["earthquake", "flood", "fire", "explosion", "collapse", "emergency"],
    "Casualty Report": ["killed", "dead", "fatalities", "casualties", "wounded", "injured"],
    "Aircraft Movement": ["fighter jet", "reconnaissance", "cargo plane", "helicopter", "airspace violation"]
  },
  "countries": {
    "Israel": ["israel", "tel aviv", "haifa", "jerusalem"],
    "Palestine": ["gaza", "west bank", "ramallah", "rafah", "khan yunis"],
    "Lebanon": ["lebanon", "beirut", "tyre", "sidon", "hezbollah"],
    "Syria": ["syria", "damascus", "aleppo", "idlib"],
    "Yemen": ["yemen", "sanaa", "hodeidah", "aden", "houthis"],
    "Iran": ["iran", "tehran", "isfahan"],
    "Iraq": ["iraq", "baghdad", "erbil"]
  }
}

// Example geocoding map (for Phase 1/2 demo purposes)
const CITY_COORDS: Record<string, [number, number]> = {
  "Beirut": [35.5018, 33.8938],
  "Gaza": [34.4668, 31.5017],
  "Tel Aviv": [34.7818, 32.0853],
  "Tehran": [51.3890, 35.6892],
  "Sanaa": [44.2062, 15.3547],
  "Baghdad": [44.3661, 33.3152],
  "Damascus": [36.2765, 33.5138]
}

serve(async (req) => {
  try {
    const { headline, source, raw_data, location_name } = await req.json()

    if (!headline) {
      return new Response(JSON.stringify({ error: "Headline is required" }), { status: 400 })
    }

    const text = headline.toLowerCase()
    
    // 1. Detect Event Type
    let eventType = "Other"
    for (const [type, keywords] of Object.entries(KEYWORDS.event_types)) {
      if (keywords.some(k => text.includes(k))) {
        eventType = type
        break
      }
    }

    // 2. Detect Country
    let detectedCountry = "Unknown"
    for (const [country, keywords] of Object.entries(KEYWORDS.countries)) {
      if (keywords.some(k => text.includes(k))) {
        detectedCountry = country
        break
      }
    }

    // 3. Basic Geocoding
    let coords = null
    if (location_name && CITY_COORDS[location_name]) {
        const [lng, lat] = CITY_COORDS[location_name]
        coords = `POINT(${lng} ${lat})`
    }

    // 4. Initialize Supabase Client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // 5. Insert into DB
    const { data, error } = await supabase
      .from('security_alerts')
      .insert({
        headline,
        source,
        event_type: eventType,
        country: detectedCountry,
        location_name,
        coordinates: coords,
        raw_data: raw_data || {},
        confidence: 0.8 // Default for rule-based
      })
      .select()

    if (error) throw error

    return new Response(JSON.stringify({ success: true, data }), {
      headers: { "Content-Type": "application/json" },
    })
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })
  }
})
