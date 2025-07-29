# pskr-plot-xmldata.py

# PSK Reporter Signal Reports Plotter
# This script fetches signal reports from PSK Reporter and plots them on a world map using Cartopy and Matplotlib.
# It visualizes the signal paths and reception reports based on frequency bands.
# Requires the 'requests', 'maidenhead', 'matplotlib', and 'cartopy' libraries.

# This 'batch' version that handles several XML files at once, it saves one plot per XML file.
# Using the animation helper script, you can convert the individual plots into an animated GIF/video.

# The script requires the directory './plots/' to be created in the same directory as this script to save the output plot.

from matplotlib import pyplot as plt
import pskrfunctions as pskr

# Get current date and time in UTC
# current_date = datetime.now(timezone.utc) #Not used in this script, the date is derived from the XML file name.

# Check if the required user configuration is set
pskr.check_user_config()

# Cartopy Map Options
projection = pskr.set_map_projection() # You can set the map projection to something else if you prefer in pskrfunctions.py


# Initialize the plot
ax = pskr.setup_plot()

xmlFiles = pskr.get_xml_files()

# For each XML file found, parse it and extract the reception reports and plot them
if not xmlFiles:
    print("No XML files found in the './pskr-xmldata/' directory. Please ensure the directory exists and contains XML files.")
    exit(1)
else:
    for xml_file in xmlFiles:
        xml_datetime = pskr.get_time_from_xml(xml_file)

        print("XML Datetime: " + pskr.format_datetime(xml_datetime, 'console'))
        file_datetime = pskr.format_datetime(xml_datetime, 'file')
        label_datetime = pskr.format_datetime(xml_datetime, 'label')

        # Set the day/night shading based on the XML file's datetime
        nightshade = pskr.setup_nightshade(xml_datetime)
        ax.add_feature(nightshade)
        print(f"Parsing XML file: {xml_file}")
        reports = pskr.parse_xml_file(xml_file)
        receptionReport = reports.findall('.//receptionReport')

        #print(receptionReports)
        for report in receptionReport:
            # Get the attributes from the a single reception report
            callsign, frequency, senderLocator, receiverLocator, signal_strength = pskr.get_report_attributes(report)
            
            if not (callsign and frequency and senderLocator and receiverLocator and signal_strength):
                print("Skipping incomplete report.") # Print an exclamation mark if any of the attributes are missing
                continue # If any atributes are missing, skip plotting this report
            else: 
                # Convert Maidenhead locator to longitude and latitude (This order is important for plotting)
                coords = pskr.get_lat_lon_from_locator(senderLocator)
                QTHcoords = pskr.get_lat_lon_from_locator(receiverLocator)

                # Convert Maidenhead locator to longitude and latitude (This order is imprortant for plotting)
                coords = pskr.get_lat_lon_from_locator(senderLocator)
                # Convert configured QTH locator to latitude and longitude
                QTHcoords = pskr.get_lat_lon_from_locator(receiverLocator)

                print(f"Callsign: {callsign}, Locator: {senderLocator}, Coordinates: {coords}, SNR: {signal_strength}")
                print("Adding to map...")

                # Plot the signal path and QTH locator on the map
                pskr.plot_signal_path(ax, coords, QTHcoords, frequency, signal_strength)
                pskr.plot_qth_locator(ax, QTHcoords)

        # Add title and text to the plot
        pskr.add_title_and_text(plt, ax, xml_datetime)
        
        # Save the plot to the './plots/' directory with a timestamp
        plt.savefig(f"./plots/psk_reporter_signal_reports.{file_datetime}.png", bbox_inches='tight', dpi=300)
        print(f"Plot saved as psk_reporter_signal_reports.{file_datetime}.png")

        # Close and restart plot or the plots start accumulating picture by picture
        plt.close()
        ax = pskr.setup_plot()
        #plt.show()

print("All XML files processed and plots generated.")