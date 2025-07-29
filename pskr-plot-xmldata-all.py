# pskr-plot-xmldata-all.py

# PSK Reporter Signal Reports Plotter
# This script fetches signal reports from PSK Reporter and plots them on a world map using Cartopy and Matplotlib.
# It visualizes the signal paths and reception reports based on frequency bands.
# Requires the 'requests', 'maidenhead', 'matplotlib', and 'cartopy' libraries.

# This is the 'batch' version of the script, however it plots ALL of the XML files in the './pskr-xmldata/' directory at once.
# Note: This uses the last XML file's datetime for the nightshade shading, so it is recommended to run this script after the XML files have been updated.
# If you would like to disable this, comment out the line: ax.add_feature(nightshade)

# DO NOT RUN THIS SCRIPT MORE THAN ONCE EVERY 5 MINUTES TO AVOID RATE LIMITS!
# The script requires the directory './plots/' to be created in the same directory as this script to save the output plot.


from matplotlib import pyplot as plt
import pskrfunctions as pskr

# Get current date and time in UTC
#current_date = datetime.now(timezone.utc) #Not used in future version of this script, the date is derived from the XML file name.

# Check if the required user configuration is set
pskr.check_user_config()

#Cartopy Map Options
# You can set the map projection to something else if you prefer, e.g., PlateCarree(), Mercator(), etc. See Cartopy documentation for more options.
projection = pskr.set_map_projection()


# Initialize the plot
ax = pskr.setup_plot()

# Get signal reports from PSK Reporter
#reports = pskr.getSignalReports()
#print(ET.tostring(reports, encoding='unicode')) # For debugging

# Get XML file names
xmlFiles = pskr.get_xml_files()

# Get the last XML file's datetime
xml_datetime = pskr.get_time_from_xml(xmlFiles[-1])

if not xmlFiles:
    print("No XML files found in the './pskr-xmldata/' directory. Please ensure the directory exists and contains XML files.")
    exit(1)
else:
    reports = pskr.parse_xml_files(xmlFiles)

receptionReports = reports.findall('.//receptionReport')
#print(receptionReports)
for report in receptionReports:
    
    callsign, frequency, senderLocator, receiverLocator, signal_strength = pskr.get_report_attributes(report)
    
    if not (callsign and frequency and senderLocator and receiverLocator and signal_strength):
        print("!", end='') # Print an exclamation mark if any of the attributes are missing
        continue # If any atributes are missing, skip plotting this report
    else: 
        # Convert Maidenhead locator to longitude and latitude (This order is important for plotting)
        coords = pskr.get_lat_lon_from_locator(senderLocator)
        QTHcoords = pskr.get_lat_lon_from_locator(receiverLocator)

        print(".", end='') # Prints a dot for each valid report processed

        # More verbose status output
        #print(f"Callsign: {callsign}, Locator: {senderLocator}, Coordinates: {coords}, SNR: {signal_strength}")
        #print("Adding to map...")

    
        # Plot the signal path and QTH locator on the map making sure that the attributes are not None
        pskr.plot_signal_path(ax, coords, QTHcoords, frequency, signal_strength)
        pskr.plot_qth_locator(ax, QTHcoords)

print('\n')

nightshade = pskr.setup_nightshade(xml_datetime)
ax.add_feature(nightshade)

# Add title and text to the plot
# TODO: Add the last XML file date and time to the text box instead of the current date.
pskr.add_title_and_text(plt, ax, xml_datetime)

plt.savefig(f"./plots/psk_reporter_signal_reports.{pskr.format_datetime(xml_datetime, 'file')}.png", bbox_inches='tight', dpi=300)
print(f"Plot saved as psk_reporter_signal_reports.{pskr.format_datetime(xml_datetime, 'file')}.png")
#plt.show()
