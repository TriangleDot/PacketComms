# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 20:12:20 2014

@author: john
"""



#=================================================================
#%% Setup Server [Run in separate console]
#=================================================================
# Note : Runs best in standard Spyder console, not iPython

# Setup paths
# =============
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')


# Imports
# ===========

import numpy as np

from packetcommslib import *

# Run server
# =============
testServer()


#=================================================================
#%% Setup Packet Server [Run in separate console]
#=================================================================
# Note : Runs best in standard Spyder console, not iPython

# Setup paths
# =============
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')


# Imports
# ===========

import numpy as np

from packetcommslib import *

# Run server
# =============
server = PacketServer()
server.run()


#=================================================================
#%% Setup Client [Run in separate console]
#=================================================================


# Setup paths
# =============
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')


# Imports
# ===========
import socket

import numpy as np

import packetcommslib as pcl

# Get IP address of host
hostIP = socket.gethostname() 
#hostIP = socket.gethostbyname('raspberrypi')


#%% Send packet to server

dataPacket = "Hi Raspberry Pi, are you tasty"
pcl.sendPacket(hostIP,dataPacket)

#%% Shutdown server
pcl.serverShutdown(hostIP)
    

#%% Test sending text packets
data_label = "/Data/New_place"

text = "Some text to send"
text_list = ["Sending","some","text","in","a","list"]

text_packet = pcl.makeTextPacket(data_label,text)
text_list_packet = pcl.makeTextPacket(data_label,text_list)

pcl.sendPacket(hostIP,text_packet)
pcl.sendPacket(hostIP,text_list_packet)



#=================================================================
#%% Array Packet making/extracting test
#=================================================================
import sys,imp
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')
import packetcommslib as pcl

# Make an array packet
# -----------------------
array = np.array([[1,2,3],[4,5,6]]).transpose()
columns = ['col1','col2']


packet = pcl.makeArrayPacket('label',array,columns)

(label,array_out) = pcl.extractPacket(packet)

print("Packet: %s" % label)
print("Array :")
print(array_out)

#=================================================================
#%% Text Packet making/extracting test
#=================================================================
import sys,imp
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')
import packetcommslib as pcl

data_label = "/Data/New_place"

text = "Some text to send"
text_list = ["Sending","some","text","in","a","list"]

text_packet = pcl.makeTextPacket(data_label,text)
text_list_packet = pcl.makeTextPacket(data_label,text_list)

(label,text_out) = pcl.extractPacket(text_packet)
(list_label,text_list_out) = pcl.extractPacket(text_list_packet)

