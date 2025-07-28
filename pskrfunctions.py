# User configuration and common functions for the PSKR-Plotter scripts.

from cartopy import crs as ccrs
from cartopy import feature as cfeature
from cartopy.feature.nightshade import Nightshade as cnightshade
from matplotlib import pyplot as plt
import requests
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from numpy import interp
import maidenhead as mh
from matplotlib.offsetbox import AnchoredText


### USER CONFIGURATION, THIS IS REQUIRED ###

# Set your callsign here
myCallsign = 'KE7BUA'

# Set your locator here (optional, can be derived from callsign) Note: Not currently used in this script
myLocator = 'DM26ic' # Supports 6 character Maidenhead locator, possibly up to 8

# Set the time resolution here (in NEGATIVE seconds) for the PSK Reporter query, default is -300 seconds (5 minutes)
requestTime = -300

# User defined map options
# You do not need to change these unless you want to customize the map appearance.
coastlineBorderResolution = '10m'  # Options: '10m', '50m', '110m'
coastlineBorderWidth = 0.5
countrylineBorderWidth = 0.5

# Cartopy Map Projection
# You can set the map projection to something else if you prefer, e.g., PlateCarree(), Mercator(), etc. See Cartopy documentation for more options.
def set_map_projection():
    
    # You can set the map projection to something else if you prefer, e.g., PlateCarree(), Mercator(), etc. See Cartopy documentation for more options.
    projection = ccrs.Robinson()
    #projection = ccrs.PlateCarree()  # Example of using PlateCarree projection
    #projection = ccrs.Mercator()  # Example of using Mercator projection

    return projection

# Check if the above user configuration is set

def check_user_config():
    if myCallsign == 'YOUR_CALLSIGN' or myLocator == 'YOUR_GRIDSQUARE_LOCATOR':
        print("Please set your callsign in pskrfunctions.py before running this script.")
        exit(1)

def setup_plot(coastlinesResolution, coastlinesLineWidth, bordersLineWidth):
    global ax, fig
    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = fig.add_subplot(1, 1, 1, projection=set_map_projection())
    ax.set_global()
    #ax.stock_img()
    ax.coastlines(resolution=coastlinesResolution, linewidth=coastlinesLineWidth)
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black', linewidth=bordersLineWidth)
    return ax

def setup_nightshade(date, alpha=0.2, facecolor='black'):
    return cnightshade(date=date, alpha=alpha, facecolor=facecolor)

# Function to fetch signal reports from PSK Reporter directly from the API
def getSignalReports():
    url = f"https://retrieve.pskreporter.info/query?receiverCallsign={myCallsign}&statistics=1&noactive=1&nolocator=0&flowStartSeconds={requestTime}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    xml_data = response.content

    root = ET.fromstring(xml_data)
    return root 

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
    
# This function returns a hex color with alpha transparency based on frequency and SNR
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

def get_report_attributes(thisReport):
    try:
        callsign = thisReport.attrib['senderCallsign'] if thisReport.attrib['senderCallsign'] is not None else 'N/A'
        frequency = int(thisReport.attrib['frequency'])
        senderLocator = thisReport.attrib['senderLocator'] if thisReport.attrib['senderLocator'] is not None else 'N/A'
        receiverLocator = thisReport.attrib['receiverLocator'] if thisReport.attrib['receiverLocator'] is not None else 'N/A'
        signal_strength = int(thisReport.attrib['sNR']) if thisReport.attrib['sNR'] is not None else 0
    except KeyError as e:
        print(f"Missing attribute in report: {e}, result discarded.")
        return None, None, None, None, None
    else:
        return callsign, frequency, senderLocator, receiverLocator, signal_strength

def get_lat_lon_from_locator(locator):
    if len(locator) < 4 or locator is None:
        print(f"Invalid locator: {locator}. Locator must be at least 4 characters long.")
        return None, None
    else:
        # Reverse latitude and longitude order for Cartopy/Matplotlib compatibility which requires longitude first
        coords = mh.to_location(locator, center=True)
        return coords[1], coords[0]
    
def plot_signal_path(ax, coords, QTHcoords, frequency, signal_strength):
    if coords is None or QTHcoords is None:
        print("Invalid coordinates for plotting signal path.")
        return
    
    ax.plot([coords[0], QTHcoords[0]], [coords[1], QTHcoords[1]], 
            marker='o', color=getLineColor(frequency), markersize=3, linewidth=0.7, markeredgecolor='black', 
            markerfacecolor=get_marker_transparency(frequency, signal_strength), transform=ccrs.Geodetic(), 
            label='Signal Path')

def plot_qth_locator(ax, QTHcoords):
    if QTHcoords is None:
        print("Invalid QTH coordinates for plotting.")
        return
    
    ax.plot(QTHcoords[0], QTHcoords[1], '^', color='blue', markersize=3, transform=ccrs.Geodetic(), label='QTH Locator')

def add_title_and_text(plt, ax, current_date):
    plt.title('PSK Reporter Signal Reports')
    textbox = AnchoredText(f"Data from PSK Reporter  Date: {current_date.strftime('%Y-%m-%d %H:%M:%S UTC')}", loc="lower center", prop=dict(alpha=0.8, size=8))
    ax.add_artist(textbox)