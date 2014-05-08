#!/usr/bin/python
# -*- coding: utf-8 -*-
####################################################################################################
#
# Copyright (c) 2014, JAMF Software, LLC.  All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#               * Redistributions of source code must retain the above copyright
#                 notice, this list of conditions and the following disclaimer.
#               * Redistributions in binary form must reproduce the above copyright
#                 notice, this list of conditions and the following disclaimer in the
#                 documentation and/or other materials provided with the distribution.
#               * Neither the name of the JAMF Software, LLC nor the
#                 names of its contributors may be used to endorse or promote products
#                 derived from this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY JAMF SOFTWARE, LLC "AS IS" AND ANY
#       EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL JAMF SOFTWARE, LLC BE LIABLE FOR ANY
#       DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
####################################################################################################
#
# SUPPORT FOR THIS PROGRAM
#
#       This program is distributed "as is" by JAMF Software, LLC.
#
####################################################################################################
#
# ABOUT THIS PROGRAM
#
# NAME
#    updateDeviceWithoutInventory.py -- Update Mobile Device Inventory
#
# SYNOPSIS
#    /usr/bin/python updateDeviceWithoutInventory.py
#
# DESCRIPTION
#    This script was designed to update mobile device inventory in a JSS for those that do not have
#    a full inventory report.
#    For the script to function properly, users must be running the JSS version 7.31 or later and
#    the account provided must have API privileges to "READ" and "UPDATE" mobile devices in the JSS.
#
####################################################################################################
#
# HISTORY
#
#    Version: 1.0
#
#    - Created by Matt Fjerstad on 4/25/14
#
#####################################################################################################
#
# DEFINE VARIABLES & READ IN PARAMETERS
#
#####################################################################################################
#
# HARDCODED VALUES SET HERE
#
jss_host = "localhost" #Example: 127.0.0.1 if run on server
jss_port = 8443
jss_path = "" #Example: "jss" for a JSS at https://www.company.com:8443/jss
jss_username = "admin"
jss_password = "jamf1234"


import sys
import httplib
import base64
import urllib2
import xml.dom.minidom
from xml.dom.minidom import parseString

class Device:
    id = -1

def main():
    devices = getDevices()
    updateDeviceInventory(devices)

def getAuthHeader(u,p):
    # Compute base64 representation of the authentication token.
    token = base64.b64encode('%s:%s' % (u,p))
    return "Basic %s" % token


def getDevices():
    devices = [];
    allDevices = xml.dom.minidom.parseString(getDeviceListFromJSS())
    nodes = allDevices.getElementsByTagName('mobile_device')
    for node in nodes:
        try:
            device = xml.dom.minidom.parseString(node.toxml())
            id = device.getElementsByTagName('id')[0].childNodes[0].data
            d = Device()
            d.id = id
            name = device.getElementsByTagName('name')[0].childNodes[0].data
            serial = device.getElementsByTagName('serial_number')[0].childNodes[0].data
            if (name == serial):
                devices.append(d)
        except:
            print "parse failed"
    return devices


#print node.getElementsByTagName('name').toxml()

def getDeviceListFromJSS():
    print "Getting device list from the JSS..."
    headers = {"Authorization":getAuthHeader(jss_username,jss_password),"Accept":"application/xml"}
    try:
        conn = httplib.HTTPSConnection(jss_host,jss_port)
        conn.request("GET",jss_path + "/JSSResource/mobiledevices",None,headers)
        data = conn.getresponse().read()
        conn.close()
        return data
    except httplib.HTTPException as inst:
        print "Exception: %s" % inst
        sys.exit(1)

def updateDeviceInventory(devices):
    print "Updating Devices Inventory..."
    ##Parse through each device and submit the command to update inventory
    for index, device in enumerate(devices):
        percent = "%.2f" % (float(index) / float(len(devices)) * 100)
        print str(percent) + "% Complete -"
        submitDataToJSS(device)
    print "100.00% Complete"

def submitDataToJSS(Device):
    print "\tSubmitting command to update device id " +  str(Device.id) + "..."
    try:
        url = "https://" + str(jss_host) + ":" + str(jss_port) + str(jss_path) + "/JSSResource/mobiledevices/id/" + str(Device.id)
        #Write out the XML string with new data to be submitted
        newDataString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device><command>UpdateInventory</command></mobile_device>"
        #print "Data Sent: " + newDataString
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url,newDataString)
        request.add_header("Authorization", getAuthHeader(jss_username,jss_password))
        request.add_header('Content-Type', 'application/xml')
        request.get_method = lambda: 'PUT'
        opener.open(request)
    except httplib.HTTPException as inst:
        print "\tException: %s" % inst
    except ValueError as inst:
        print "\tException submitting PUT XML: %s" % inst
    except urllib2.HTTPError as inst:
        print "\tException submitting PUT XML: %s" % inst
    except:
        print "\tUnknown error submitting PUT XML."

main()


























