# User configuration and common functions for the PSKR-Plotter scripts.

from cartopy import crs as ccrs

### USER CONFIGURATION, THIS IS REQUIRED ###

# Set your callsign here
myCallsign = 'YOUR_CALLSIGN'

# Set your locator here (optional, can be derived from callsign) Note: Not currently used in this script
myLocator = 'YOUR_GRIDSQUARE_LOCATOR' # Supports 6 character Maidenhead locator, possibly up to 8

# Set the time resolution here (in NEGATIVE seconds) for the PSK Reporter query, default is -300 seconds (5 minutes)
requestTime = -300

# Check if the above user configuration is set

def check_user_config():
    if myCallsign == 'YOUR_CALLSIGN' or myLocator == 'YOUR_GRIDSQUARE_LOCATOR':
        print("Please set your callsign in pskrfunctions.py before running this script.")
        exit(1)

# Cartopy Map Options

def set_map_options():
    
    # You can set the map projection to something else if you prefer, e.g., PlateCarree(), Mercator(), etc. See Cartopy documentation for more options.
    projection = ccrs.Robinson()
    #projection = ccrs.PlateCarree()  # Example of using PlateCarree projection
    #projection = ccrs.Mercator()  # Example of using Mercator projection

    