# pskr-plot-xmldata.py

# PSK Reporter Signal Reports Plotter
# This script fetches signal reports from PSK Reporter and plots them on a world map using Cartopy and Matplotlib.
# It visualizes the signal paths and reception reports based on frequency bands.
# Requires the 'requests', 'maidenhead', 'matplotlib', and 'cartopy' libraries.

# This is the single run version of the script, it retrieves signal reports from the PSK Reporter API directly. 
# DO NOT RUN THIS SCRIPT MORE THAN ONCE EVERY 5 MINUTES TO AVOID RATE LIMITS!
# The script requires the directory './plots/' to be created in the same directory as this script to save the output plot.

# Todo: Add either SNR labels over plot markers, or alpha transparency to the markers based on SNR values.

import maidenhead as mh
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnchoredText
from cartopy import crs as ccrs
from cartopy.feature.nightshade import Nightshade as cnightshade
from cartopy import feature as cfeature
from datetime import datetime, timezone
from pathlib import Path
from numpy import interp

# Get current date and time in UTC
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
# Moved down to For loop to ensure the time is correct from the XML file used in Nightshade.
#nightshade = cnightshade(date=current_date, alpha=0.2, facecolor='black')

#Plot Setup and Options

def setup_plot():
    global ax, fig
    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax.set_global()
    #ax.stock_img()
    ax.coastlines(resolution='10m', linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black', linewidth=0.5)
    return ax

fig = plt.figure(figsize=(12, 8), dpi=100)
ax = fig.add_subplot(1, 1, 1, projection=projection)
ax.set_global()
#ax.stock_img()
ax.coastlines(resolution='10m', linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black', linewidth=0.5)

def get_xml_files():
    target_dir = Path('./pskr-xmldata/')
    files = list(target_dir.glob('*.xml'))
    return files

def parse_xml_file(xml_file):
    xml_string = ""
    with open(xml_file, 'r') as file:
        xml_string = file.read()
    return ET.fromstring(xml_string)

def get_time_from_xml(xml_file):
    xml_datetime = xml_file.stem.split('pskr-retrievedata-')[1]
    return datetime.strptime(xml_datetime, '%Y-%m-%dT%H-%M-%Sz')


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

    # Map SNR to alpha transparency in 8 bits (0-255) using numpy's interp function
    alpha = interp(snr, [-23, 10], [0, 255])
    # Convert from float to int
    alpha = int(alpha)
    # Convert alpha to hex format
    alphaHex = hex(int(alpha))[2:].zfill(2)  # Ensure it's a 2-digit hex value
    
    # Combine base color with alpha transparency
    return f"{base_color}{alphaHex}"

xmlFiles = get_xml_files()

# For each XML file found, parse it and extract the reception reports and plot them
if not xmlFiles:
    print("No XML files found in the './pskr-xmldata/' directory. Please ensure the directory exists and contains XML files.")
    exit(1)
else:
    for xml_file in xmlFiles:
        xml_datetime = get_time_from_xml(xml_file)
        print("XML Datetime: " + xml_datetime.strftime('%Y-%m-%d %H:%M:%S'))
        file_datetime = xml_datetime.strftime('%Y-%m-%dT%H-%M-%SZ')
        label_datetime = xml_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')
        # Set the day/night shading based on the XML file's datetime
        nightshade = cnightshade(date=xml_datetime, alpha=0.2, facecolor='black')
        ax.add_feature(nightshade)
        print(f"Parsing XML file: {xml_file}")
        reports = parse_xml_file(xml_file)
        receptionReport = reports.findall('.//receptionReport')

        #print(receptionReports)
        for report in receptionReport:
            callsign = report.attrib['senderCallsign'] if report.attrib['senderCallsign'] is not None else 'N/A'
            frequency = int(report.attrib['frequency']) if 'frequency' in report.attrib else 0
            if 'senderLocator' not in report.attrib:
                continue
            locator = report.attrib['senderLocator']
            coords = mh.to_location(locator, center=True) if locator != 'N/A' else (None, None)
            QTHcoords = mh.to_location(report.attrib['receiverLocator'], center=True) if report.attrib['receiverLocator'] else (None, None)
            signal_strength = report.attrib['sNR'] if report.attrib['sNR'] is not None else 'N/A'
            print(f"Callsign: {callsign}, Locator: {locator}, Coordinates: {coords}, SNR: {signal_strength}")
            print("Adding to map...")
            robinsonQTHCoords = QTHcoords[1], QTHcoords[0]
            robinsonRXCoords = coords[1], coords[0]
            ax.plot([robinsonRXCoords[0], robinsonQTHCoords[0]], [robinsonRXCoords[1], robinsonQTHCoords[1]], marker='o', color=getLineColor(frequency), markersize=3, linewidth=0.7, markeredgecolor='black', markerfacecolor=get_marker_transparency(frequency, signal_strength), markeredgewidth=0.5, transform=ccrs.Geodetic(), label='Signal Path')
            #ax.text(robinsonRXCoords[0], robinsonRXCoords[1], signal_strength, fontsize=4, ha='center', va='center', color='red', transform=ccrs.Geodetic())
            ax.plot(robinsonQTHCoords[0], robinsonQTHCoords[1] , '^', color='blue', markersize=3,  transform=ccrs.Geodetic(), label='QTH Locator')
    

        plt.title('PSK Reporter Signal Reports')
        #plt.legend(loc='lower left', fontsize='small')
        textbox = AnchoredText(f"Data from PSK Reporter  Date: {label_datetime}", loc="lower center", prop=dict(alpha=0.8, size=8))
        ax.add_artist(textbox)
        plt.savefig(f"./plots/psk_reporter_signal_reports.{file_datetime}.png", bbox_inches='tight', dpi=300)
        print(f"Plot saved as psk_reporter_signal_reports.{file_datetime}.png")

        # Close and restart plot or the plots start accumulating picture by picture
        plt.close()
        setup_plot()
        #plt.show()

print("All XML files processed and plots generated.")