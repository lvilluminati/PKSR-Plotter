# pskr-plot-singlerun.py

# PSK Reporter Signal Reports Plotter
# This script fetches signal reports from PSK Reporter and plots them on a world map using Cartopy and Matplotlib.
# It visualizes the signal paths and reception reports based on frequency bands.
# Requires the 'requests', 'maidenhead', 'matplotlib', and 'cartopy' libraries.

# This is the single run version of the script, it retrieves signal reports from the PSK Reporter API directly. 
# DO NOT RUN THIS SCRIPT MORE THAN ONCE EVERY 5 MINUTES TO AVOID RATE LIMITS!
# The script requires the directory './plots/' to be created in the same directory as this script to save the output plot.


from matplotlib import pyplot as plt
from datetime import datetime, timezone
import pskrfunctions as pskr

current_date = datetime.now(timezone.utc)

# Check if the required user configuration is set
pskr.check_user_config()

### Set up Cartopy Map Options ###

projection = pskr.set_map_projection() # You can set the map projection to something else if you prefer in pskrfunctions.py
# Nightshade parameters, current_date is required. alpha and facecolor override the defaults.
nightshade = pskr.cnightshade(date=current_date, alpha=0.2, facecolor='black')

# Set up plot, you can customize these in pskrfunctions.py
ax = pskr.setup_plot(pskr.coastlineBorderResolution, pskr.coastlineBorderWidth, pskr.countrylineBorderWidth)

# Add nightshade to the plot
ax.add_feature(nightshade)

# Get signal reports from PSK Reporter

reports = pskr.getSignalReports()
#print(ET.tostring(reports, encoding='unicode')) # For debugging

receptionReports = reports.findall('.//receptionReport')
#print(receptionReports) # For debugging

# Main plotting loop, plots each reception report on the map
for report in receptionReports:

    # Get the attributes from the a single reception report
    callsign, frequency, senderLocator, receiverLocator, signal_strength = pskr.get_report_attributes(report)
    
    # Convert Maidenhead locator to longitude and latitude (This order is imprortant for plotting)
    coords = pskr.get_lat_lon_from_locator(senderLocator)
    # Convert configured QTH locator to latitude and longitude
    QTHcoords = pskr.get_lat_lon_from_locator(receiverLocator)

    # Status output
    print(f"Callsign: {callsign}, Locator: {senderLocator}, Coordinates: {coords}, SNR: {signal_strength}")
    print("Adding to map...")
 
    # Plot the signal path and QTH locator on the map
    pskr.plot_signal_path(ax, coords, QTHcoords, frequency, signal_strength)
    pskr.plot_qth_locator(ax, QTHcoords)
    
# Add title and text to the plot
pskr.add_title_and_text(plt, ax, current_date)

# Save the plot to the './plots/' directory with a timestamp
plt.savefig(f"./plots/psk_reporter_signal_reports.{pskr.format_datetime(current_date,'file')}.png", bbox_inches='tight', dpi=300)
print(f"Plot saved as psk_reporter_signal_reports.{pskr.format_datetime(current_date,'file')}.png")

# If you want to show the plot, uncomment the next line however this will block the script until you close the plot window.
#plt.show()
