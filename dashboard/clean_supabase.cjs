const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '/Users/kirkspencer/Documents/war-dash-new/dashboard/.env' });

const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_SERVICE_ROLE_KEY || process.env.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error("Missing Supabase credentials in environment");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function clean() {
  console.log("Fetching existing OFFICIAL_SUMMARY entries...");
  const { data, error } = await supabase
    .from('security_alerts')
    .delete()
    .eq('event_type', 'OFFICIAL_SUMMARY')
    .select();

  if (error) {
    console.error("Error deleting from Supabase:", error);
  } else {
    console.log(`Successfully deleted ${data.length} old OFFICIAL_SUMMARY entries.`);
    data.forEach(row => {
      console.log(` - Deleted: ${row.headline} (Original created_at: ${row.created_at})`);
    });
    console.log("\nThe worker will fetch and insert the correct chronological data on its next pass.");
  }
}

clean();
