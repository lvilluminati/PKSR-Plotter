# pskr-plot-singlerun.py

# PSK Reporter Signal Reports Plotter
# This script fetches signal reports from PSK Reporter and plots them on a world map using Cartopy and Matplotlib.
# It visualizes the signal paths and reception reports based on frequency bands.
# Requires the 'requests', 'maidenhead', 'matplotlib', and 'cartopy' libraries.

# This is the single run version of the script, it retrieves signal reports from the PSK Reporter API directly. 
# DO NOT RUN THIS SCRIPT MORE THAN ONCE EVERY 5 MINUTES TO AVOID RATE LIMITS!
# The script requires the directory './plots/' to be created in the same directory as this script to save the output plot.

# Todo: Add either SNR labels over plot markers, or alpha transparency to the markers based on SNR values.

import requests
import maidenhead as mh
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnchoredText
from cartopy import crs as ccrs
from cartopy.feature.nightshade import Nightshade as cnightshade
from cartopy import feature as cfeature
from datetime import datetime, timezone
from numpy import interp

current_date = datetime.now(timezone.utc)

# USER CONFIGURATION
# Set your callsign here
myCallsign = 'YOUR_CALLSIGN'
# Set your locator here (optional, can be derived from callsign) Note: Not currently used in this script
myLocator = 'YOUR_GRIDSQUARE_LOCATOR' # Supports 6 character Maidenhead locator, possibly up to 8
# Set the time resolution here (in NEGATIVE seconds) for the PSK Reporter query, default is -300 seconds (5 minutes)
requestTime = -300

#Cartopy Map Options
# You can set the map projection to something else if you prefer, e.g., PlateCarree(), Mercator(), etc. See Cartopy documentation for more options.
projection = ccrs.Robinson()
nightshade = cnightshade(date=current_date, alpha=0.2, facecolor='black')

#Plot Setup and Options
fig = plt.figure(figsize=(12, 8), dpi=100)
ax = fig.add_subplot(1, 1, 1, projection=projection)
ax.set_global()
#ax.stock_img()
ax.coastlines(resolution='10m', linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black')
ax.add_feature(nightshade)

# Returns a Hex color based on PSK Reporter band colors
def getLineColor(frequency):
    if frequency >= 56000000: # 6m band
        return '#FF0000'
    if frequency >= 28000000: # 10m band
        return '#ff69b4'
    elif frequency >= 24890000: # 12m band
        return '#b22222'
    elif frequency >= 21000000: # 15m band
        return '#cca166'
    elif frequency >= 18068000: # 17m band
        return '#f2f261'
    elif frequency >= 14000000: # 20m band
        return '#f2c40c'
    elif frequency >= 10100000: # 30m band
        return '#62d962'
    elif frequency >= 7000000: # 40m band
        return "#5959ff"
    elif frequency >= 3500000: # 80m band
        return '#e550e5'
    elif frequency >= 1800000: # 160m band
        return '#7cfc00'
    else:
        return 'grey' # Default color for other frequencies

# Tihs function returns a hex color with alpha transparency based on frequency and SNR
# Using the range of SNR values from -23 to 10 dB to map to alpha transparency
def get_marker_transparency(frequency, snr):
    # Get base color based on frequency
    base_color = getLineColor(frequency)

    # Map SNR to alpha transparency in 8 bits (0-255)
    alpha = interp(snr, [-23, 10], [0, 255])
    # Convert from float to int
    alpha = int(alpha)
    # Convert alpha to hex format, with leading zeroes if necessary
    alphaHex = hex(int(alpha))[2:].zfill(2)
    
    # Combine base color with alpha transparency
    return f"{base_color}{alphaHex}"

# Function to fetch signal reports from PSK Reporter directly from the API
def getSignalReports():
    url = f"https://retrieve.pskreporter.info/query?receiverCallsign={myCallsign}&statistics=1&noactive=1&nolocator=0&flowStartSeconds={requestTime}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    xml_data = response.content

    root = ET.fromstring(xml_data)
    return root 

# Get signal reports from PSK Reporter
reports = getSignalReports()
#print(ET.tostring(reports, encoding='unicode'))

receptionReports = reports.findall('.//receptionReport')
#print(receptionReports)
for report in receptionReports:
    callsign = report.attrib['senderCallsign'] if report.attrib['senderCallsign'] is not None else 'N/A'
    frequency = int(report.attrib['frequency'])
    locator = report.attrib['senderLocator'] if report.attrib['senderLocator'] is not None else 'N/A'
    coords = mh.to_location(locator, center=True) if locator != 'N/A' else (None, None)
    QTHcoords = mh.to_location(report.attrib['receiverLocator'], center=True) if report.attrib['receiverLocator'] else (None, None)
    signal_strength = report.attrib['sNR'] if report.attrib['sNR'] is not None else 'N/A'
    print(f"Callsign: {callsign}, Locator: {locator}, Coordinates: {coords}, SNR: {signal_strength}")
    print("Adding to map...")
    robinsonQTHCoords = QTHcoords[1], QTHcoords[0]
    robinsonRXCoords = coords[1], coords[0]
    ax.plot([robinsonRXCoords[0], robinsonQTHCoords[0]], [robinsonRXCoords[1], robinsonQTHCoords[1]], marker='o', color=getLineColor(frequency), markersize=3, linewidth=1.2, markeredgecolor='black', markerfacecolor=get_marker_transparency(frequency, signal_strength), transform=ccrs.Geodetic(), label='Signal Path')
    #ax.text(robinsonRXCoords[0], robinsonRXCoords[1], signal_strength, fontsize=4, ha='center', va='center', color='red', transform=ccrs.Geodetic())
    ax.plot(robinsonQTHCoords[0], robinsonQTHCoords[1] , '^', color='blue', markersize=5,  transform=ccrs.Geodetic(), label='QTH Locator')
    
# Show the plot
plt.title('PSK Reporter Signal Reports')
#plt.legend(loc='lower left', fontsize='small')
textbox = AnchoredText(f"Data from PSK Reporter  Date: {current_date.strftime('%Y-%m-%d %H:%M:%S UTC')}", loc="lower center", prop=dict(alpha=0.8, size=8))
ax.add_artist(textbox)
plt.savefig(f"./plots/psk_reporter_signal_reports.{current_date.strftime('%Y-%m-%d-%H-%M-%Sz')}.png", bbox_inches='tight', dpi=300)
print(f"Plot saved as psk_reporter_signal_reports.{current_date.strftime('%Y-%m-%d-%H-%M-%Sz')}.png")
#plt.show()
