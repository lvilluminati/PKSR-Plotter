#!/bin/bash

# This script retrieves data from PSK Reporter's API for a specific callsign and time range.
# The script is meant to be invoked via cron at a rate of 5 minutes or longer.

# Example 5 minute cron job:
# */5 * * * * /bin/bash /path/to/pskr-plot-retrievedata.sh

# Example 1 hour cron job:
# 0 * * * * /bin/bash /path/to/pskr-plot-retrievedata.sh

# User-defined variables
# Set your callsign here
callsign="YOUR_CALLSIGN"

# Set the time resolution here (in NEGATIVE seconds) for the PSK Reporter query, default is -300 seconds (5 minutes)
requestTime=-300

# Current date and time in UTC
currentTime=$(date -u +"%Y-%m-%dT%H-%M-%Sz")

# Create the output directory if it doesn't exist
outputDir="./pskr-xmldata"
mkdir -p "$outputDir"

# Construct the output file name
outputFile="$outputDir/pskr-retrievedata-$currentTime.xml"

# Make the API request to PSK Reporter
curl -s "https://retrieve.pskreporter.info/query?receiverCallsign=$callsign&statistics=1&noactive=1&nolocator=0&flowStartSeconds=$requestTime" -o "$outputFile"