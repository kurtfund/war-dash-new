#!/bin/bash

# ==========================================
# WAR DASH: MANUAL INSS POWERBI SCRAPER
# ==========================================
# This script extracts the latest casualty
# statistics from the INSS PowerBI dashboard
# and uploads them directly to Supabase.
# ==========================================

echo "==> Starting War Dash INSS Updates..."

cd "$(dirname "$0")"

# Activate the local virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Python virtual environment (.venv) not found. Please run 'python3 -m venv .venv' first."
    exit 1
fi

# Load keys directly if they exist, or prompt the user for them
if [ ! -f ".env_inss" ]; then
    echo "=========================================="
    echo "FIRST TIME SETUP: MISSING API CREDENTIALS"
    echo "=========================================="
    echo "Your Supabase production keys are hidden on Render."
    echo "To push data from your MacBook, please provide them here once:"
    read -p "Enter your Supabase URL (https://...): " SUPA_URL
    read -p "Enter your Supabase Service Role Key (eyJ...): " SUPA_KEY
    echo "SUPABASE_URL=\"$SUPA_URL\"" > .env_inss
    echo "SUPABASE_SERVICE_ROLE_KEY=\"$SUPA_KEY\"" >> .env_inss
    echo "Saved to .env_inss!"
    echo "------------------------------------------"
fi

export set -a
source .env_inss
export set +a

# Ensure playwright is installed globally in the environment
echo "==> Verifying Playwright installation..."
playwright install chromium > /dev/null 2>&1

echo "==> Launching Headless Browser to scrape INSS PowerBI..."
echo "==> This may take ~15 seconds to load the dashboard graphics."
python3 ingestion/scrape_powerbi.py

if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "SUCCESS: The live War Dash dashboard has "
    echo "been updated with the latest INSS figures!"
    echo "=========================================="
else
    echo "=========================================="
    echo "ERROR: Failed to update INSS metrics."
    echo "Please check your network and API keys."
    echo "=========================================="
fi
