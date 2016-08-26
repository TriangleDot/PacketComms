# -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:05:53 2016

@author: john

File transfer server
=============================

Server side library for File transfer

"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,sys
import collections

BASEPATH, dummy = os.path.split(os.path.abspath(__file__))
sys.path.append(BASEPATH)

# Third party libraries


# My libraries
import packetcommslib as pcl
import mainfilemanager


#==============================================================================
#%% Constants
#==============================================================================






#==============================================================================
#%% Functions
#==============================================================================

def packet_processor(payload):
    pass



#==============================================================================
#%% Runner
#==============================================================================

server = pcl.PacketServer()
server.packet_handler_class = pcl.PacketHandler    

server.run()