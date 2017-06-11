passwd = '999999'             # change this line to reflect your envoy's password
# don't forget to pass your envoy ip address to this script when it is called
# as   Python3 save-events-s.py '192.168.1.254'

#--------------------------------------------------------------------------------------------------------------------------------------# Name:
# Purpose:            Read Envoy event log data directly from the Envoy.  Save the
#                           data to files named:  envoy-eventlog-yyyymmdd-hhmmss.csv
#                           If logfiles exist in the same folder as this script, the latest envoy-eventlog
#                           is read and only events after the last saved event id are written out
#                           to avoid duplicate data.
#
#  Notes:               The Envoy IP address must be passed to this program when it is run.
#                            Example to run:   Python save-events.py '192.168.1.20' 
#                            will read data from the envoy with the ip address 192.168.1.20
#
# Requires:             Python Version 3.0 or later  (tested on version 3.5)
# Author:                Ken Clifton
# Web site:              http://www.kenclifton.com
# Tested on:            Linux and Windows
#
# Created:               12/30/2016
#
# Updated:               1/2/2017
# Update Purpose:   Added timeout=30 to both urllib.request.urlopen to allow for
#                               older, slower Envoys that require more tiime to respond.
#                               Also changed code to only create CSV file if rows that need to be
#                               written actually exist.
#                               Also added try, except error handling to show errors on urlopen and read.
#
# Updated:               4/25/2017
# Update Purpose:   Modified script to work with Envoy-S
#                               This required implementing basic authentication.
#                               The initial dummy read is no longer required -- it was removed.
#                               The url was shortened to only include the start and the end.
#
# SPECIAL UPDATE:   4/26/2017
# PURPOSE:             The cron job puts files in the root home folder instead of the 
#                               documents folder.  The folder path was hard coded into this program.
#
#-------------------------------------------------------------------------------------------------------------------------------------

def read_envoy_data( envoy_ip ):
    # function read_envoy_data gets the json data from the envoy

    import urllib.request
    import json
    import socket
    
    socket.setdefaulttimeout(30)
    
    url = 'http://' + envoy_ip + '/datatab/event_dt.rb?start=0&length=600'
    
    # https://docs.python.org/3/library/functions.html#input
    # https://docs.python.org/3/library/getpass.html
    auth_user='envoy'
    auth_passwd = passwd

    # https://docs.python.org/3.4/howto/urllib2.html#id5
    #
    # If you would like to request Authorization header for Digest Authentication,
    # replace HTTPBasicAuthHandler object to HTTPDigestAuthHandler
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, auth_user, auth_passwd)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
      
    # notes about eventTableString:
    # iSortCol_0=  [zero indexed eventlog column to sort by]
    # sSortDir_0= [sort direction: 'asc' is ascending 'desc' is descending
    eventTableString = '/datatab/event_dt.rb' + \
    '?start=0' + \
    '&length=600' 
     
    # build the full url to get the eventTable
    url = 'http://' + envoy_ip + eventTableString
    
    try:
        response = urllib.request.urlopen(url,  timeout=30)
    except urllib.error.URLError as error:
        print('Data was not retrieved because error: {}\nURL: {}'.format(error.reason, url) )
        quit()  # exit the script - some error happened
    except socket.timeout:
        print('Connection to {} timed out, '.format( url))
        quit()  # exit the script - cannot connect
    
    try:
        # Convert bytes to string type and string type to dict
        string = response.read().decode('utf-8')
    except urllib.error.URLError as error:
        print('Reading of data stopped because error:{}\nURL: {}'.format(error.reason, url) )
        response.close()  # close the connection on error
        quit()  # exit the script - some error happened
    except socket.timeout:
        print('Reading data at {} had a socket timeout getting log, '.format( url))
        response.close()  # close the connection on error
        quit()  # exit the script - read data timeout
    json_data = json.loads(string)
    
    #close the open response object
    #urllib.request.urlcleanup()
    response.close()
    return json_data
    #------------------------------------------ end read_envoy_data function

def get_last_eventlog_id( folderpath ):
    # function get_last_eventlog_id  looks in the same folder as this
    # script for any previously saved envoy eventlogs.  If previous logs are found
    # it opens the latest log, then reads the last event id saved, then returns it.
    
    import os
    
    # get the last eventlog id number from last error log file
    import csv
    items = os.listdir(folderpath)        #get list of files in folder path
    loglist = []                          # create a new loglist object
    for afile in items:       # loop through all the files in the directory
        # only add to loglist if it is a csv file and envoy event log           
        if afile[:15] == 'envoy-eventlog-' and afile[-4:] == '.csv':
            loglist.append(afile)   #add file to the list of log files
    
    loglist.sort()        # sort the files
    loglist.reverse()  # reverse the list so that the file with the latest / newest date is first
    
    lastLogEntryNumber =  0     # initialize the last log id number
    if len(loglist) > 0:   # if at least one logfile was found...
        # use latest (first) file in the sorted list
        fileToRead = os.path.join(folderpath,loglist[0])
        with open(fileToRead,  newline='') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                if count > 0:   # if second row 
                    lastLogEntryNumber = int(row[0]) # get the id number
                    break
                else:
                    count = count + 1
    # end of code to get last log id number which is returned in lastLogEntryNumber
    
    return lastLogEntryNumber
    #------------------------------------------ end get_last_eventlog_id function

def main():

    import csv
    import os
    import sys
    import time
    
    # check to see if the envoy ip was passed as a command line argument
    if len(sys.argv) > 1:
        envoy_ip = sys.argv[1]
    else:
        envoy_ip = '192.168.1.254'
    
    # call function read event log data from the envoy
    envoy_data = read_envoy_data(envoy_ip)
    
    ############################
    ##    SPECIAL MOD FOR CRON JOB             ##
    ##   Normally this would just getcwd()       ##
    ############################
    # get current working directory
    folderPath = os.getcwd()
    #folderPath = '/envoy_logs'
    ############################
    ##  END OF SPECIAL MOD FOR CRON JOB   ##
    ############################    

    # call function to find the last saved event id
    # this allows only new events to be saved to avoid duplication
    lastLogEntryNumber = get_last_eventlog_id(folderPath)
 
    # build the new logfile name
    timestr = time.strftime("%Y%m%d-%H%M%S")
    # os.path.join is used to make this cross-platform (Windows, Linux, Mac)
    #  folderpath is joined with either a / or \ depending upon the operating system
    logfile_name = os.path.join(folderPath,"envoy-eventlog-" + timestr + ".csv")
    
   
    # from the json_data retrieved from the url extract the aaData item
    aaData = envoy_data['aaData']
    
    column_name_list = []
    column_name_list.append( 'Event ID' )
    column_name_list.append( 'Event' )
    column_name_list.append('HW Serial Num')
    column_name_list.append('Device')
    column_name_list.append('Date')
    writeHeadings = True
    
    eventCount = 0                                # counter for number of events written
    for eventLog_line in aaData:           # loop through all data table row items
        rowlist = []                                          #create new list object for row  

        for eventLog_column in eventLog_line:  # loop through columns in the row
            rowlist.append(eventLog_column)       # add column text to python list object
        
        # convert hw_serial_number to string so it shows correctly -- not scientific notation
        hw_serial_number = rowlist[2]
        rowlist[2] = "'" + str(hw_serial_number)
        
        eventID = rowlist[0]        
        if eventID.isdigit():                              # see if the row has an event id number
            if int(rowlist[0]) > lastLogEntryNumber:
                if writeHeadings == True:
                     # write out errorlog
                    errlog_out = open(logfile_name, 'w',  newline='')  # mode was wb on python2.7
                    mywriter = csv.writer(errlog_out, dialect='excel')           #create csv writer
                    mywriter.writerow(column_name_list)   # write the row with the headings to a csv row
                    writeHeadings = False
                mywriter.writerow(rowlist)           # write the row with the log number
                eventCount = eventCount + 1     # count events written
                
    if writeHeadings == False:
        print('Successful run, {} events written to new log.'.format(eventCount))
        errlog_out.close()                                    # close csv file
    # end main()

# allow script to be imported if necessary    
if __name__ == '__main__':
    main()
