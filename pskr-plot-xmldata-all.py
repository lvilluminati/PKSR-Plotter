# pskr-plot-xmldata.py

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
from pathlib import Path
import pskrfunctions as pskr

# Get current date and time in UTC
current_date = datetime.now(timezone.utc)

# Check if the required user configuration is set
pskr.check_user_config()

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
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black', linewidth=0.5)
ax.add_feature(nightshade)

def get_xml_files():
    target_dir = Path('./pskr-xmldata/')
    files = list(target_dir.glob('*.xml'))
    return files

def parse_xml_files():
    xml_string = ""
    xml_files = get_xml_files()
    if not xml_files:
        print("No XML files found in the './pskr-xmldata/' directory. Please ensure the directory exists and contains XML files.")
        exit(1)
    for xml_file in xml_files:
        with open(xml_file, 'r') as file:
            xml_string += file.read()
    return ET.fromstring(xml_string)

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

# Function to fetch signal reports from PSK Reporter directly from the API
def getSignalReports():
    url = f"https://retrieve.pskreporter.info/query?receiverCallsign={pskr.myCallsign}&statistics=1&noactive=1&nolocator=1&flowStartSeconds={pskr.requestTime}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    xml_data = response.content

    root = ET.fromstring(xml_data)
    return root 

# Get signal reports from PSK Reporter
reports = getSignalReports()
#print(ET.tostring(reports, encoding='unicode'))

# Declare empty string for XML data

xmlFiles = get_xml_files()
if not xmlFiles:
    print("No XML files found in the './pskr-xmldata/' directory. Please ensure the directory exists and contains XML files.")
    exit(1)
else:
    reports = parse_xml_files()

receptionReports = reports.findall('.//receptionReport')
#print(receptionReports)
for report in receptionReports:
    callsign = report.attrib['senderCallsign'] if report.attrib['senderCallsign'] is not None else 'N/A'
    locator = report.attrib['senderLocator'] if report.attrib['senderLocator'] is not None else 'N/A'
    coords = mh.to_location(locator, center=True) if locator != 'N/A' else (None, None)
    QTHcoords = mh.to_location(report.attrib['receiverLocator'], center=True) if report.attrib['receiverLocator'] else (None, None)
    signal_strength = report.attrib['sNR'] if report.attrib['sNR'] is not None else 'N/A'
    print(f"Callsign: {callsign}, Locator: {locator}, Coordinates: {coords}, SNR: {signal_strength}")
    print("Adding to map...")
    robinsonQTHCoords = QTHcoords[1], QTHcoords[0]
    robinsonRXCoords = coords[1], coords[0]
    ax.plot([robinsonRXCoords[0], robinsonQTHCoords[0]], [robinsonRXCoords[1], robinsonQTHCoords[1]], marker='o', color=getLineColor(int(report.attrib['frequency'])), markersize=3, linewidth=1.2, markeredgecolor='black', transform=ccrs.Geodetic(), label='Signal Path')
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
