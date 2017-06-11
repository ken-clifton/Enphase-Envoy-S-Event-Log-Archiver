# Enphase-Envoy-S-Event-Log-Archiver
Python v3 script to retrieve Enphase Envoy-S Event log events and archive them with a unique date-time name in CSV format.

Please note that this script is NOT a product of Enphase Energy. If it doesn't work, please contact me, not Enphase. Enphase Energy is a company which primarily manufactures microinverters for solar PV arrays. Enphase Energy has an API for their Enlighten monitoring service. Enphase Enlighten (TM) provides access to current and historical solar production data and status informaton.

Events are saved with the name:  envoy-eventlog-yyyymmdd-hhmmss.csv (where yyyy is the four-digit year, mm is the two-digit month, and dd is the two-digit day, followed by the hhmmss timestamp).

I chose this naming convention to allow sorting of the event log files.  The .csv files open into nicely formatted columns with named headings in Libre Office Calc or Microsoft Excel.

The script requires one argument when run, the IP address of the Envoy. In the following examples an address of 192.168.1.100 for the Envoy is used.

Here is a sample command on Linux to run the script (notice Python3 and quotes):
Python3 save-events-s.py ‘192.168.1.100’

On Windows the command to run this script is:
python save-events-s.py 192.168.1.100

The script enumerates any existing envoy-eventlog files that are in the same location as the script, then reads the last row in the last event log to find the last saved ‘Event ID.”  The script will only save events that occur after that event id to prevent duplication of data.

I suggest scheduling the script to run at least once or twice per day to archive events from the Envoy.  On Linux a cron table entry, or a scheduled task on Windows can easily be used automate the process.
