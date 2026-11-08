#!/usr/bin/env bash
set -e

# ==========================================
# War Dash - 100% Free Local Ingestion Runner
# ==========================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=================================================="
echo "⚡ Starting War Dash Local Ingestion Worker"
echo "=================================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env_inss" ]; then
        cp .env_inss .env
    elif [ -f "dashboard/.env" ]; then
        cp dashboard/.env .env
    else
        echo "⚠️  No .env file found!"
        echo "👉 Please copy .env.example to .env and fill in your Supabase credentials:"
        echo "   cp .env.example .env"
        exit 1
    fi
fi

# Run with uv if installed, else fallback to python3
if command -v uv &> /dev/null; then
    echo "Using uv to run worker..."
    uv run --with requests --with feedparser --with beautifulsoup4 --with tenacity --with yfinance --with supabase --with python-dotenv python ingestion/worker.py "$@"
elif [ -d "venv" ]; then
    echo "Using local venv..."
    source venv/bin/activate
    python ingestion/worker.py "$@"
else
    echo "Running with system python3..."
    python3 ingestion/worker.py "$@"
fi
