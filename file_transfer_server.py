# -*- coding: utf-8 -*-
"""
Created on Tue May 24 08:05:53 2016

@author: john

==============================================================================
 License
==============================================================================


Copyright 2016 John Bainbridge

This file is part of PacketComms.

PacketComms is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PacketComms is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PacketComms.  If not, see <http://www.gnu.org/licenses/>.


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