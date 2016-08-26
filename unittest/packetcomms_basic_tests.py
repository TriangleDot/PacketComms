# -*- coding: utf-8 -*-
"""
Created on Sun May 22 14:08:16 2016

@author: john


PacketComms library unit tests
===================================

This script has tests on the basic functions of packetcommslib, that don't 
involve going from client to server

"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,sys
import unittest

# Third party libraries
import numpy as np

# My libraries
sys.path.append('/home/john/Documents/Python/Projects/packet_comms_checkouts/trunk')
import packetcommslib as pcl


#==============================================================================
#%% Constants
#==============================================================================

TEMP_DIR = '/home/john/Documents/Python/Projects/External_test_storage/PacketsComms/unittest_data'


#==============================================================================
#%% Class definitions
#==============================================================================

class TestPacketFunctions(unittest.TestCase):

    def setUp(self):
        pass
    
    def teardown(self):
        pass


    # ------------------------------------------------------------------------
    #%% Tests
    # ------------------------------------------------------------------------
    def test_template(self):
        # Put test here
        
        

        # test condition
        self.assertTrue(True)
        
        
    def test_byte_conversion(self):
        """
        Test the integer<->byte conversion functions
        
        """
        
        initial_number = 3876
        final_number = pcl.bytes2int64(pcl.uint642bytes(initial_number))
        
        self.assertTrue(initial_number==final_number)
        

    def test_text_string_packet(self):
        """
        Create and extract text packets using string format
        
        """
        
        # Input data
        data_label = "/Data/New_place"
        text = "Some text to send"
        
        # Packet
        text_packet = pcl.makeTextPacket(data_label,text)
        
        # Extracted packet
        (label,text_out) = pcl.extractPacket(text_packet)
        
        self.assertTrue(label==data_label and text_out==text)
        
        
        
        
    def test_text_list_packet(self):
        """
        Create and extract text packets using list format
        
        """
        
        # Input data
        data_label = "/Data/New_place"
        text_list = ["Sending","some","text","in","a","list"]
        
        # Packet
        text_list_packet = pcl.makeTextPacket(data_label,text_list)
        
        # Extracted data
        (list_label,text_list_out) = pcl.extractPacket(text_list_packet)

        self.assertTrue(list_label==data_label and text_list_out==text_list)
        
        
    @unittest.skip("array packet does not work yet")    
    def test_array_packet(self):
        """
        Create and extract array packet
        
        """
        
        # Make an array packet
        # -----------------------
        data_label ='array packet'
        array = np.array([[1,2,3],[4,5,6]]).transpose()
        columns = ['col1','col2']
        
        
        packet = pcl.makeArrayPacket(data_label,array,columns)
        
        (label,array_out) = pcl.extractPacket(packet)
        
        print("Packet: %s" % label)
        print("Array :")
        print(array_out)
        
        self.assertTrue(label==data_label and all(array_out==array))
        
        
        
    def test_file_packet(self):
        """
        * Write a file
        * Convert to packet
        * Extract packet
        * Compare
        
        """
        
        test_string = 'This is a test file for packetcommslib'
        
        filename = os.path.join(TEMP_DIR,'file_packet_test.txt')
        
        with open(filename,'w') as fid:
            fid.write(test_string)

        label = 'File packet test'             
        file_packet = pcl.makeFilePacket(label,filename)
        
        #print('file_packet = ',file_packet)
        
        (label_out,(filename_out,file_contents)) = pcl.extractPacket(file_packet)
        
        self.assertTrue( label_out==label 
                        and file_contents.decode()==test_string 
                        and filename_out==filename)
        

        


#==============================================================================
#%% Runner
#==============================================================================

if __name__ == '__main__':
    unittest.main()