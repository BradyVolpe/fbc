#!/usr/bin/python3
# Author: Brady Volpe
# Date: September 29, 2020
# Updated Aug, 2021
# Nimble This LLC 2013
# All Rights Reserved
# No part of this repo or any of its contents may be reproduced, copied, modified or adapted,
# without the prior written consent of the author, unless otherwise indicated for stand-alone materials.
#
#
#
# IMP : plotly, pysnmp and pandas modules are required for this script
# USAGE: getAndPlotFbcData.py <IPv4 : 1, IPv6 2> <SNMP community string> <cm IP > <filename>

import csv
from os import times
import sys
import time
import plotly.express as px
from pysnmp.hlapi import *

# Define MIBs
docsIf3CmSpectrumAnalysisMeasAmplitudeData = ".1.3.6.1.4.1.4491.2.1.20.1.35.1.2"
modemDescOID            = "1.3.6.1.2.1.1.1.0"
enableAnalyzerOID       = ".1.3.6.1.4.1.4491.2.1.20.1.34.1.0"
inactivityTimeoutOID    = ".1.3.6.1.4.1.4491.2.1.20.1.34.2.0"
startFreqOID            = ".1.3.6.1.4.1.4491.2.1.20.1.34.3.0"
stopFreqOID             = ".1.3.6.1.4.1.4491.2.1.20.1.34.4.0"
spanOID                 = ".1.3.6.1.4.1.4491.2.1.20.1.34.5.0"
binOID                  = ".1.3.6.1.4.1.4491.2.1.20.1.34.6.0"
windowOID               = ".1.3.6.1.4.1.4491.2.1.20.1.34.8.0"
avgOID                  = ".1.3.6.1.4.1.4491.2.1.20.1.34.9.0"

# Convert 2's complement 16 hex value to decimal
def twos(val):
    x = int(val, 16)
    if x > 32767:
        x = x - 65535
    return x

# Select transport target based on the IpAddress type
def getTransportTarget():
    if(int(sys.argv[1]) == 1):
        return UdpTransportTarget((str(sys.argv[3]), 161))
    else:
        return Udp6TransportTarget((str(sys.argv[3]), 161))


def getFormattedTime(hr, min, sec):
    return str(hr) + "hr:" + str(min) + "min:" + str(sec) + "sec"


def isModemReachable():
    for (errorIndication, errorStatus, errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                             CommunityData(str(sys.argv[2])),
                             getTransportTarget(),
                             ContextData(),
                             ObjectType(ObjectIdentity(
                                 modemDescOID))):

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
            break
        else:
            print("Modem is reachable...")
            print()


def doSetSNMP(message, oid, value, typeFlag):
    print(message)
    if(typeFlag == "int"):
        value = Integer(value)
    elif(typeFlag == "gague32"):
        value = Gauge32(value)
    for (errorIndication, errorStatus, errorIndex,
         varBinds) in setCmd(SnmpEngine(),
                             CommunityData(str(sys.argv[2])),
                             getTransportTarget(),
                             ContextData(),
                             ObjectType(ObjectIdentity(
                                 oid), value)):

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
            break
        else:
            print("Value applied sucessfully")
            print()


def setSpectrum():
    doSetSNMP("Enabling analyzer...", enableAnalyzerOID, 1, "int")
    doSetSNMP("Setting inactivity timeout...",
              inactivityTimeoutOID, 3000, "int")
    doSetSNMP("Setting start freq...", startFreqOID, 93000000, "gague32")
    doSetSNMP("Setting stop freq...", stopFreqOID, 993000000, "gague32")
    doSetSNMP("Setting span...", spanOID, 7500000, "gague32")
    doSetSNMP("Setting bin...", binOID, 256, "gague32")
    doSetSNMP("Setting window...", windowOID, 1, "int")
    doSetSNMP("Setting averge...", avgOID, 8, "gague32")


def getFbcData():
    ampdata = []
    print("Getting FBC data...")
    time.sleep(10)
    startTime = time.time()
    endLocalTime = time.localtime(startTime + 60)
    while(time.time() <= (startTime + 60)):
        currentTime = time.localtime()
        print("Trying to get FBC data at ", getFormattedTime(currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec),
              " last try at ", getFormattedTime(endLocalTime.tm_hour, endLocalTime.tm_min, endLocalTime.tm_sec))
        errorOccurred = False
        for (errorIndication, errorStatus, errorIndex,
             varBinds) in bulkCmd(SnmpEngine(),
                                  CommunityData(str(sys.argv[2])),
                                  getTransportTarget(),
                                  ContextData(),
                                  0, 2,
                                  ObjectType(ObjectIdentity(
                                      docsIf3CmSpectrumAnalysisMeasAmplitudeData)),
                                  lexicographicMode=False):

            if errorIndication:
                print(errorIndication)
                errorOccurred = True
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
                errorOccurred = True
                break
            else:
                for varBind in varBinds:
                    ampdata.append(varBind[1].prettyPrint()[2:])
        if len(ampdata) > 1 and errorOccurred == False:
            break
    doSetSNMP("Disabling analyzer...", enableAnalyzerOID, 2, "int")
    if len(ampdata) <= 1:
        print("No FBC data available")
        sys.exit()
    else:
        print("Got the FBC data...")

    # Decode each AmplitudeData row and write frequency,amplitude values to output file
    try:
        with open(sys.argv[4], "w") as outF:
            ampDataLen = len(ampdata)
            index = 0
            for x in ampdata:
                if(index < ampDataLen-1):
                    centerfreq  = int(x[0:8], 16)
                    freqspan    = int(x[8:16], 16)
                    numbins     = int(x[16:24], 16)
                    binspacing  = int(x[24:32], 16)
                    resbw       = int(x[32:40], 16)

                    startfreq = centerfreq - (numbins / 2 * binspacing)

                    i = 0
                    bin = 0
                    while i < numbins*4:
                        freq = startfreq + (bin * binspacing)
                        j = 40 + i
                        hexvalue = x[j:j+4]
                        ampvalue = twos(hexvalue) / 100.0

                        print(str(freq) + "," + str(ampvalue), file=outF)

                        i += 4
                        bin += 1
                    index += 1
    except Exception as ex:
        print("Error occurred while processing amplitude data : ", ex)
        sys.exit()



def showFbcData():
    print("Plotting graph...")
    xdata = []
    ydata = []

    with open(sys.argv[4]) as csvfile:
        csvData = csv.reader(csvfile, delimiter=',')
        for row in csvData:
            xdata.append(float(row[0]) / 1000000)
            ydata.append(float(row[1]))

    fig = px.line(x=xdata, y=ydata,
                  labels={'x': 'Frequency (MHz)', 'y': 'Amplitude (dB)'},
                  title='DOCSIS Cable Modem Full Band Capture', markers=True)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                      title={'x': 0.5, 'xanchor': 'center'})
    fig.update_traces(hovertemplate='Frequency: <b>%{x:.2f} MHz</b><br>Amplitude: <b>%{y:.2f} dBmV</b>',
                      line_color='rgb(68,114,196)')
    fig.update_xaxes(showline=True, linewidth=2,
                     linecolor='black', gridcolor='rgb(209,209,209)')
    fig.update_yaxes(showline=True, linewidth=2,
                     linecolor='black', gridcolor='rgb(209,209,209)')
    fig.write_html(sys.argv[4] + ".html")
    print("Graph saved into ", str(sys.argv[4] + ".html"))


if __name__ == "__main__":
    
    if ((len(sys.argv)) < 5):
        print("Usage: getAndPlotFbcData.py <IPv4 : 1, IPv6 2> <SNMP community string> <cm IP> <filename>")
        sys.exit()

    isModemReachable()
    setSpectrum()
    getFbcData()
    showFbcData()

# End of file
