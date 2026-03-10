#!/bin/bash

# Test Script for WAR DASH Ingestion
# Usage: ./test_ingestion.sh "Your headline here" "Source" "LocationName"

HEADLINE=${1:-"Rocket fire reported near Tel Aviv following airstrikes in Gaza"}
SOURCE=${2:-"LiveNews"}
LOCATION=${3:-"Tel Aviv"}

URL="http://localhost:54321/functions/v1/ingest-alert"
# Note: In production or remote, use the project URL

echo "Testing ingestion for: $HEADLINE"

curl -i --request POST "$URL" \
  --header "Content-Type: application/json" \
  --data "{
    \"headline\": \"$HEADLINE\",
    \"source\": \"$SOURCE\",
    \"location_name\": \"$LOCATION\"
  }"
