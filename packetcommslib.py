# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 20:04:51 2014

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


Generic packet client/server functions
===========================================


Example usage
=====================

Setup server
-------------------
from packetcommslib import *

# Run server
testServer()

Setup client
---------------------
import socket
import packetcommslib as pcl

# Get IP address of host
hostIP = socket.gethostname() # Local host
#hostIP = socket.gethostbyname('raspberrypi')  # External host

# send packet string
pcl.sendPacket(hostIP,"Hi Raspberry Pi, are you tasty")




@author: john
"""

# TODO:
# Can probably remove numpy dependency by using the to_bytes() method for ints
# 64bit integer example
# A = int(4001)
# A_bytes = A.to_bytes(8,byteorder='little')  
#
# Convert bytes back to int
# int.from_bytes(A_bytes, byteorder='little')


#=============================================================================
#%% Imports
#=============================================================================

import os
import socket
import threading 

import numpy as np


#=============================================================================
#%% Constants
#=============================================================================


# Magic number for identifying packets from this library
MAGIC_NUMBER = 3986316

# Packet numbers
DATA_PACKET = 4001
TEXT_PACKET = 4002
FLOAT_PACKET = 4003
INT_PACKET = 4004
FILE_PACKET = 4005
QUIT_PACKET = 4666

# Text packet Separator for splitting up text packets
TEXT_PACKET_SEPARATOR = "<sep>"

# uint64 size in bytes
SIZEOF_UINT64 = 8

SOCKET_PORT = 63406

DEBUG = True

# Packet labels
SERVER_EXIT = 'server_exit'
UNKNOWN_PACKET = 'unknown_packet_type'
FILE_TRANSFER_PACKET = 'file'


#=============================================================================
#%% Functions
#=============================================================================

# TODO : these functions are for replacing numpy

def uint642bytes(integer):
    """
    Convert int to bytes as a 64bit integer
    
    Input
    ---------
    integer : int
    
    Output
    ---------
    byte_int : bytes
        integer converted to bytes
    
    """
    
    A = int(integer)
    return A.to_bytes(8,byteorder='little')  
    
    
def bytes2int64(byte_uint64):
    """
    Convert byte string into unsigned int
    
    Inputs
    ---------
    byte_uint64: bytes
        uint64 converted into bytes by uint642bytes()
        
    Outputs
    ---------
    integer : int
    
    """
    return int.from_bytes(byte_uint64, byteorder='little')
    

def file2bytes(fpath):
    """
    Read a file into a byte string
    
    Inputs
    --------
    fpath : str
        full path to file
        
    Outputs
    --------
    byte_data : bytestring
        file contents as a bytestring
        
    """
    
    with open(fpath,'rb') as fid:
        byte_data = fid.read()
        
    return byte_data

    
def bytes2file(byte_data,fpath):
    """
    Write byte string out to a file
    
    Inputs
    --------
    byte_data : bytestring
        file contents as a bytestring
        
    fpath : str
        full path to file
        
    """
    
    with open(fpath,'wb') as fid:
        fid.write(byte_data)
        
        

#=============================================================================
#%% Client side for sending data
#=============================================================================


def wrapDataPacket(dataPacket):
    """ 
    Wrap the data packet for sending over TCIP connection
    This adds the magic number and the length of the total packet to the front of
    the data packet. The server can then read this first and will
    then know how long to read data from the connection.
    
    Input
    ------
    dataPacket : byte string or str
        The packet to be transmitted
    
    Output
    ----------
    wrappedPacket: byte string
        The packet converted into a byte string. This is what will be transmitted.
    
    """
    
    # Get length of packet
    # ------------------------
    pkLen = len(dataPacket)
    
    # Check for empty packets
    # return without error for now
    
    if pkLen == 0:
        return
        
    # Make sure packet is a byte string
    if hasattr(dataPacket,'encode'):
        packet = dataPacket.encode()
    else:
        packet = dataPacket
        
    
    # Add to packet
    # ------------------------
    # Add the total length of the packet including the size of the integer
    # that is being added
    wrappedPacket = b''.join([uint642bytes(MAGIC_NUMBER),
                              uint642bytes(pkLen+SIZEOF_UINT64),
                              packet])
    
    # Return bytes packet
    return wrappedPacket
    
        
    
def sendPacket(hostIP,dataPacket):
    """ 
    Send the packet over a TCIP link to the server
    
    Wrap data packet and send. Then close connection.
    
    Inputs
    -----------
    hostIP : str
        IP address of host
    dataPacket : str or bytes
        packet data to send
    
    
    Outputs
    ---------
    successFlag = True if packet sent, otherwise False
    
    """
    
    # Wrap the data packet
    # ----------------------------
    wrappedPacket = wrapDataPacket(dataPacket)
    
    # Check it worked, otherwise return
    if wrappedPacket == None:
        return False
        
        
    # Send packet
    # ------------------------------
    
    # Create socket object
    s = socket.socket()        
    
    # Connect socket to port on server
    s.connect((hostIP, SOCKET_PORT))
    
    if DEBUG:
        print("\nClient Program\n---------------\n")
        print("\nConnected to server")
        print("\tPeername : ",s.getpeername())
        print("\tSocket name : ",s.getsockname())
        print("Packet length = %d" % len(wrappedPacket))
    
    
    # Send command as bytes
    s.send(wrappedPacket)
    
    # Read reply
    reply = readPacket(s)
    
    print("Reply : %s" % reply)
    
    
    # Close the socket
    s.close()

    if DEBUG:              
        print("Connection is closed")
        
    # Return if everything worked
    return reply



#=============================================================================
#%% server functions
#=============================================================================


def testServer():
    """ 
    Simple server for testing the client functions
    
    Prints output to console for debugging
    
    """
    
    # Setup the socket
    # -------------------------------------------------
    s = socket.socket()         # Create a socket object
    #host = socket.gethostname() # Get local machine name
    host = socket.gethostbyname('0.0.0.0') # listen for any computer
    s.bind((host, SOCKET_PORT))        # Bind to the port
    
    print("Initialising test server\n---------------------")
    
    
    s.listen(5)                 # Now wait for client connection.
    
    
    # Main Server loop
    # -----------------------------------------------
    while True: # Loop forever, listening for client connections
       print("Listening\n")
                
       c, addr = s.accept()     # Establish connection with client.
       print('Got connection from', addr)
       
       # Read packet from connection
       # TODO : this should be passed to a thread
       packet = readPacket(c)
       print("\nReceived packet\n[%s]" % packet )
       
       
       # Send reply
       if packet:
           reply = "Success"
       else:
           reply = "failed"
           
       c.send(wrapDataPacket(reply))
     
       
       # Close the connection
       # TODO should this be done here or in readPackets ?
                
       c.close()                
       print("Closing connection")
       
       
       
def readPacket(conn):
    """
    Read packet from client connection.
    
    First get the length of the data, then read the rest of the packet
    
    Input
    -----------
    conn = socket passed from server
    
    Output
    --------
    packet_contents : byte string
        contents of the packet, without any decoding
    
    
    """
    
    # Read Magic number
    # ---------------------
    # Keep reading until we have the first uint64 number from
    # the packet
    packet_magic_number = b''
    
    while len(packet_magic_number) < SIZEOF_UINT64:
        # Get data from socket
        chunk = conn.recv(SIZEOF_UINT64-len(packet_magic_number))
        
        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading magic number")
            
        # Data received - add it to the packet
        packet_magic_number = packet_magic_number + chunk
        
    # Check this is the correct number
    # if not then drop the connection
    magic_number = bytes2int64(packet_magic_number[0:SIZEOF_UINT64])
    
    
    if magic_number != MAGIC_NUMBER:
        if DEBUG:
            print("Unknown packet [%d] : dropping connection" % magic_number)
        return
        
    
    if DEBUG:
        print("Reading packet ...")
    
    # Read packet length
    # ---------------------
    # Keep reading until we have the first uint64 number from
    # the packet
    packet = b''
    
    while len(packet) < SIZEOF_UINT64:
        # Get data from socket
        chunk = conn.recv(SIZEOF_UINT64-len(packet))
        
        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading packet length")
            
        # Data received - add it to the packet
        packet = packet + chunk
        
    # Packet should now contain the length of the total packet
    # decode the length
    packetLength = bytes2int64(packet[0:SIZEOF_UINT64])
    
    if DEBUG:
        print("\tPacket Length = %d" % packetLength)
        print("\tReading rest of packet ...")
    
    # Read the rest of the packet
    # -------------------------------
    while len(packet) < packetLength:
        # Get data from socket
        chunk = conn.recv(packetLength-len(packet))
        
        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading packet")
            
        # Data received - add it to the packet
        packet = packet + chunk
    
    
    if DEBUG:
        print("\tPacket received [%d bytes]:" % len(packet))
        print(packet[SIZEOF_UINT64:])
        
    try:
        return packet[SIZEOF_UINT64:] #.decode('utf-8')
        
    except Exception as ex:
        print("Failed to read packet")
        print(ex)
        
    return None
    
    



#=============================================================================
#%% Array Packet Constructor/Extractor
#=============================================================================
#Functions for packaging arrays of numbers into byte packets
# TODO : These may not work


def makeArrayPacket(data_label,array_in,columnNamesList = None):
    """
    Convert a numpy array into a packet for sending over network
    
    Inputs
    ------
    label : str
        label for use in storing the array, could be an HDF5 path
    array_in : numpy array
        data to be sent
    columnNamesList : list of str
        list of column names for the array
    
    Outputs
    -----------
    Packet in string form
    
    The format:
    * Packet type number [UINT16] 0-65536
    * No. rows [UINT64]
    * No. columns [UINT64]
    * length of column name text + data label [UINT64]
    * data label and Column name text comma delimited [Bytes]
    * Data - 2D array float64 converted to byte string
    
    """
    
    # Check for recarray and extract out to normal array
    # ------------------------------------------------------
    # TODO 
    
    
    # Get shape of array
    # ----------------------

    # Get dimensions
    nRows,nCols = array_in.shape
    
    
    # Check Column names
    # ----------------------
    if columnNamesList == None:
        # Assign default column names
        # 'dataset1', 'dataset2' etc
        columnNamesList = []
        for iCol in range(nCols):
            columnNamesList.append('dataset%d' % iCol+1)
            
    # Check column names list is same length as number of columns
    assert len(columnNamesList)==nCols, "Column names list does not have the same number of entries as there are columns"
            
    # Add data Label to column list
    # want to put all strings to be transmitted in the same place
    columnNamesList.insert(0,data_label)
    
    # Construct the data packet
    # --------------------------
    # Make everything into a string and then pack it together
    
    # initialise packet list
    dataPacket = []
    
    # Add Packet type as 64 bit unsigned integer
    dataPacket.append( np.uint64(DATA_PACKET).tostring() )
    
    # Add Number of rows as 64 bit unsigned integer
    dataPacket.append( np.uint64(nRows).tostring() )
    
    # Add Number of columns as 64 bit unsigned integer
    dataPacket.append( np.uint64(nCols).tostring() )
    
    # Add Column names 
    
    # Package the column names into a comma delimited list 
    # Add the length of the column name package first and then the list itself.
    colNamePackage = ','.join(columnNamesList)
    
    # Add length of package as 64 bit int
    dataPacket.append(np.uint64(len(colNamePackage)).tostring() )
    
    # Add column name package as bytes
    dataPacket.append(colNamePackage.encode())
    
    # Add data 
    dataPacket.append( np.float64(array_in).tostring())
    
    # Return byte string packet by joining all the items in the list
    return dataPacket
    
    
def extractArrayPacket(packet):
    """
    Extract 2D array data from packet
    
    Inputs
    --------
    packet : byte string 
        packet as generated by makeArrayPacket but with the packet type stripped
        off
    
    Outputs
    --------
    (data_label,array_out) = tuple of outputs
    
    Where
        data_label : str
            Label used for storing, e.g. HDF5 path
        array_out = 2D numpy recarray with column names included
    
    """
    
    

    # Extract integer data (No. Rows, columns and header string)    
    # -----------------------------------------------------------------------
    # Get all 4 numbers in one shot
    # Gives array with [Channel, No. Rows,No. Cols,Length of Column header string]

    nH = 3 # Number of integers to extract first
    
    numData = np.fromstring(packet[0:SIZEOF_UINT64*nH],dtype = 'uint64')
    nRows = numData[0]
    nCols = numData[1]
    headerLength = int(numData[2])
    
    
    # Extract header
    # ----------------
    # Slice out header, convert from bytes to string and separate by delimiters
    headerList = packet[SIZEOF_UINT64*nH:SIZEOF_UINT64*nH+headerLength].decode().split(',')
    
    # Extract channel label as the first item
    data_label = headerList[0]
    
    # Extract the numerical data
    # ---------------------------
    # extract the remaining string and convert to float64
    # this produces a 1D array
    array_out = np.fromstring(packet[SIZEOF_UINT64*nH+headerLength:],dtype='float64')
    
    # resize to original dimensions
    array_out = array_out.reshape((nRows,nCols))
    
    # convert to recarray and add column headers
    recarray_out = np.core.records.fromarrays(array_out.transpose(), 
                                             names = headerList[1:])
                                            
    return (data_label,recarray_out)   


#=============================================================================
#%% Text Packet Constructor/Extractor
#=============================================================================

def makeTextPacket(data_label,text):
    """
    Make a text packet.
    
    Inputs
    ------------
    data_label : str
        label for use in storing the text, e.g. an HDF5 path
        
    text: str
        The text to send
        
    Output
    ---------
    packet : byte str
    
    
    Format:
    
    * Packet type number [UINT16] 0-65536
    * data_label
    * <sep>  (separator string)
    * text
    
    """
    
    # Check input for a list of strings
    # ---------------------------------
        
    if isinstance(text,list):
        # Make list into one string with separators
        text = TEXT_PACKET_SEPARATOR.join(text)
        
    
    
    # Construct the packet
    # ------------------------
    
    # initialise packet list
    dataPacket = []
    
    # Add Packet type as 64 bit unsigned integer
    #dataPacket.append( np.uint64(TEXT_PACKET).tostring() )
    dataPacket.append( uint642bytes(TEXT_PACKET) )
    
    # Add data label
    dataPacket.append(data_label.encode())
    
    # Add separator
    dataPacket.append(TEXT_PACKET_SEPARATOR.encode())
    
    # Add payload text
    dataPacket.append(text.encode())
    
    
    # Return byte string packet
    # -----------------------------
    
    # Combine into one byte string
    return b''.join(dataPacket)
    
    

def extractTextPacket(packet):
    """
    Extract from a text packet
    
    
    Inputs
    --------
    packet : byte string 
        packet as generated by makeArrayPacket but with the packet type stripped
        off
    
    Outputs
    --------
    (data_label,text) : tuple of outputs
    
    """
    
    # The packet type number has been removed so all that is needed is
    # to decode from bytes to normal string and separate the data label
    # from the main text
    
    # Decode and split into list or strings
    string_list = packet.decode().split(TEXT_PACKET_SEPARATOR)
    num_strings = len(string_list)
    
    # Quick quality check
    assert num_strings >= 2,'Text packet does not have enough data'
    
    # Data label is first element
    data_label = string_list[0]
    
    # Allow for passing lists of strings
    if num_strings == 2:
        # A single string was passed
        text = string_list[1]
    else:
        # A list was passed, so return the list
        text = string_list[1:]
        
    
    return (data_label,text)
    


#=============================================================================
#%% File Packet Constructor/Extractor
#=============================================================================

def makeFilePacket(data_label,filename):
    """
    Make a file packet.
    Read the file into a binary string and put in a packet
    
    Inputs
    ------------
    data_label : str
        label for use in storing the file
        
    filename: str
        full path/filename to file
        
    Output
    ---------
    packet : byte str
    
    
    Format:
    
    * Packet type number [UINT16] 0-65536
    * data_label
    * <sep>  (separator string)
    * file contents
    
    """
    
    # Validate file
    assert os.path.exists(filename), "makeFilePacket: filename does not exist [%s]" % filename
        
        
    
    # Read file into binary string
    # --------------------------------    
    file_contents = file2bytes(filename)
    
    
    # Construct the packet
    # ------------------------
    
    # initialise packet list
    dataPacket = []
    
    # Add Packet type as 64 bit unsigned integer
    dataPacket.append( uint642bytes(FILE_PACKET) )
    
    # Add data label
    dataPacket.append(data_label.encode())
    
    # Add separator
    dataPacket.append(TEXT_PACKET_SEPARATOR.encode())
    
    # Add filename
    dataPacket.append(filename.encode())

    # Add separator    
    dataPacket.append(TEXT_PACKET_SEPARATOR.encode())
    
    # Add payload text
    dataPacket.append(file_contents)
    
    
    # Return byte string packet
    # -----------------------------
    
    # Combine into one byte string
    return b''.join(dataPacket)
    
    

def extractFilePacket(packet):
    """
    Extract from a file packet
    
    
    Inputs
    --------
    packet : byte string 
        packet as generated by makeArrayPacket but with the packet type stripped
        off
    
    Outputs
    --------
    (data_label,file_contents_bytes) : tuple of outputs
    
    """
    
    # The packet type number has been removed so all that is needed is
    # to decode from bytes to normal string and separate the data label
    # from the main text
    
    # Decode and split into list or strings
    string_list = packet.split(TEXT_PACKET_SEPARATOR.encode())
    num_strings = len(string_list)
    
    # Quick quality check
    assert num_strings == 3,'File packet does not have enough data'
    
    # Data label is first element
    data_label = string_list[0].decode()
    
    # Filename is the second element
    filename = string_list[1].decode()
    
    # File contents is the third element
    file_contents = string_list[2]
    
        
    return (data_label,(filename,file_contents) )
    
     
    
#=============================================================================
#%% Server shutdown Packet 
#=============================================================================

def makeShutdownPacket():
    """
    Make a special packet that causes the server to shutdown.
    For unit testing
    
    Inputs
    ------------
    -    
    
    Output
    ---------
    packet : byte str
    
    
    Format:
    
    * Packet type number [UINT16] 0-65536
    * data_label
    * <sep>  (separator string)
    * text
    
    """
    
    # Check input for a list of strings
    # ---------------------------------
        
        
    
    
    # Construct the packet
    # ------------------------
    
    # initialise packet list
    dataPacket = []
    
    # Add Packet type as 64 bit unsigned integer
    #dataPacket.append( np.uint64(TEXT_PACKET).tostring() )
    dataPacket.append( uint642bytes(QUIT_PACKET) )
    
    # Add dummy data
    dataPacket.append('dummy'.encode())
    
    
    # Return byte string packet
    # -----------------------------
    
    # Combine into one byte string
    return b''.join(dataPacket)    

    
def serverShutdown(hostIP):
    """
    Send the shutdown command to the packet server

    Input
    -----    
    hostIP : str
        IP address of host
    
    
    """
    
    sendPacket(hostIP,makeShutdownPacket())
    


#=============================================================================
#%% Packet extraction top level functions
#=============================================================================

    
     
def getPacketType(packet):
    """ packetType,remainingPacket = getPacketType(packet)
    
    Read first unit64 from unwrapped packet string to identify which
    packet has been sent. Then return the rest of the packet for extraction
    by other functions
    
    Input
    --------
    packet = byte string packet
    
    Outputs
    ----------
    packetType : uint64
        numerical packet type as defined at top of this file
    remainingPacket : byte str
        packet with type stripped off
    
    """
    
    #packetType = np.fromstring(packet[0:SIZEOF_UINT64],dtype = 'uint64')
    packetType = bytes2int64(packet[0:SIZEOF_UINT64])
    
    return int(packetType),packet[SIZEOF_UINT64:]
    




def extractPacket(packet):
    """
    Top level packet extraction. Determines the type of packet and then calls
    the appropriate extraction function
    
    Input
    ---------
    packet : byte str
        byte string packet passed on by readPacket
        
    Output
    -------
    (label,payload) : (str,variable)
        Returns the label that comes with the packet and the payload, which
        can be various types:
            array : numpy recarray
            text : str
            int
            float
            
    """
    
    # Check the packet type
    # ------------------------
    # Note: this removes the packet type number from front of packet
    
    
    packetType,packet = getPacketType(packet)
    
    if packetType == DATA_PACKET:
        return extractArrayPacket(packet)
        
    elif packetType == TEXT_PACKET:
        return extractTextPacket(packet)
        
    elif packetType == FILE_PACKET:
        return extractFilePacket(packet)
        
    elif packetType == INT_PACKET:
        pass
    
    elif packetType == FLOAT_PACKET:
        pass
    
    elif packetType == QUIT_PACKET:
        return (SERVER_EXIT,'dummy')
    
    else:
        print("Unknown packet type [%d]" % packetType)
        return(UNKNOWN_PACKET,packet)
        
        
    
    
                
#=============================================================================
#%% Threaded server functions
#=============================================================================

class PacketServer():
    """
    Basic packet server
    
    
    Example usage
    --------------
    
    setup server
    >>> server = PacketServer()
    
    Run server
    >>> server.run()
    
    Setting up your own packet handler
    -------------------------------------
    You can add your own packet handler by adding functions to the PacketHandler()
    class that handle packets based on their labels.
    
    >>> handler = PacketHandler()
    >>> handler.packet_processor['command'] = process_commands
    Where process_commands is a function that accepts a single input which will
    be the payload of the packet.
  
    
    
    """
    
    def __init__(self):
        """
        Initialise server variables
        
        """
        
        # Setup the port
        self.port = SOCKET_PORT
        
        # Setup Packet handler
        self.packet_handler_class = PacketHandler
        
        # Packet processing functions
        # - replace with custom stuff
        # key = label
        # value = function
        self.packet_processor = {}
        
        

    def run(self):
        """ 
        Server that passes packets to threads
        
        """
        
        # Setup the socket
        # -------------------------------------------------
        s = socket.socket()         # Create a socket object
        #host = socket.gethostname() # Get local machine name
        host = socket.gethostbyname('0.0.0.0') # listen for any computer
        s.bind((host, self.port))        # Bind to the port
        
        print("Initialising Packet server\n---------------------")
    
        # Management variables    
        threads = []    
        server_shutdown = False
        
        s.listen(5)                 # Now wait for client connection.
        
        
        # Main Server loop
        # -----------------------------------------------
        while not server_shutdown: # Loop forever, listening for client connections
           print("Listening\n")
                    
           c, addr = s.accept()     # Establish connection with client.
           print('Got connection from', addr)
           
           # Read packet from connection
           handler = self.packet_handler_class(c,addr,server_shutdown)
           handler.daemon = True
           # Pass in the packet processing functions
           handler.packet_processor = self.packet_processor
           handler.start()
           threads.append(handler) 
           
           
        # Wait for all the threads to finish
        for thread in threads:
           thread.join()
           
        # Safe to exit now
       
       
       


class PacketHandler(threading.Thread):
    """
    Handle packets and perform appropriate actions
    
    """
    

    def __init__(self,conn,address,server_shutdown):
        """
        Inputs
        ------
        conn: socket
        
        address : IP address (?)
        
        server_shutdown: bool
            set this to True to shutdown the server. Used with the special
            'Quit' packet
            
        """
        
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.server_shutdown = server_shutdown
        
        # Packet processing functions
        # - replace with custom stuff
        self.packet_processor = {}


    def run(self):
        
       # Read packet from connection
       packet = readPacket(self.conn)
       #print("\nReceived packet\n[%s]" % packet )
       
       # Extract packet
       packet_label,payload = extractPacket(packet)
       
       # Process packet payload
       reply = self.process_packet(packet_label,payload)           
       
       
       # Send reply
       if not reply:
           reply = "failed"

       print("Reply: %s" % reply)
       self.conn.send(wrapDataPacket(reply))
       
       
       # Close the connection                
       self.conn.close()                
       print("Closing connection")
       
       
       # Special packet label for shutting down server
       if packet_label == SERVER_EXIT:
           self.server_shutdown = True
           
           
       
           
       
       
    
    def process_packet(self,packet_label,payload):
       """
       Process the type of packet
       
       Input
       ------
       packet_label : string
           
       payload : string or array or byte string
           Output of extractPacket()
           
       Output
       --------
       reply : string
           reply to send back to client
       
       """
       
       # Apply custom process to each packet type
       
       if packet_label not in self.packet_processor:
           if not DEBUG:
               print("No processing method for packet [%s]" % packet_label)
               return "No processing available"
           
           # If no processing then printout the packet contents
           print("Packet label: %s" % packet_label)
           print("Packet contents:")
           print(payload)
           return "Debug printout at server"
           


       # Run process for each packet
       reply = self.packet_processor[packet_label](payload)
       
       return reply
       
       
#=============================================================================
#%% Packet client
#=============================================================================

class PacketClient():
    """
    Template for client side. This class acts as a way to store the hostIP
    and provide a class interface to the packet library
    
    """
    
    def __init__(self,hostIP):
        """
        Setup connection to host
        
        """
        
        self.host = hostIP
        
        
    def send(self,data_packet):
        """
        Basic function for sending packets that have been pre-prepared
        
        Input
        -----
        data_packet : byte string
            Usually the output of makeTextPacket, makeFilePacket, 
            makeArrayPacket etc.
            
        Output
        --------
        reply : string
            reply from server
            
        """
        
        reply = sendPacket(self.host,data_packet)
        
        return reply.decode()
        
        
