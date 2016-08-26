# -*- coding: utf-8 -*-
"""
Created on Mon May 23 20:17:46 2016

@author: john

File Transfer client side
=================================

This is the client side library for the File transfer manager

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

COMMAND_LABEL = 'command'


#==============================================================================
#%% Class definitions
#==============================================================================

class FileTransferClient(pcl.PacketClient):
    """
    Client for File transfer
    
    Example usage
    ---------------
    
    Setup client
    >>> ftc = FileTransferClient(hostIP,master_folder)
    
    Add file to master storage
    >>> ftc.addFile(filename)
    
    Add directory to master storage
    >>> ftc.addDir(dir_path)
    
    Add new master folder TODO : this may only be required when starting client
    >>> ftc.addMasterDir(master_folder_name,folder_path)
    
    Commit all to master folder
    >>> ftc.commit(folder_path)
    
    Delete file or folder from master folder
    >>> ftc.delete(folder_or_file_path))
    
    Find file in master folder
    >>> ftc.findFile(filename))
    
    """
    
    
    def __init__(self,serverIP,master_folder):
        """
        Initialise FileTransfer client
        
        Inputs
        -------
        serverIP : str
            IP or hostname of server
            
        master_folder_name : str
            Name of master folder on the server repository. This is where all
            the files are copied to.
        
        """
        
        # Initialise the base class
        super(FileTransferClient, self).__init__(serverIP)
        
        # Set the master folder
        self.masterFolder = master_folder
        
        # Create/Get a local file manager database
        self.localFileManager = mainfilemanager.Files()
    
    
    
    
    def addFile(self,filename):
        """
        Add a file to the storage repository in the the specified master folder.
        
        Inputs
        --------
        master_folder_name : str
            Name of master folder to store file in
            
        filename : str
            path/filename to local file that is to be uploaded to repository
            
        """
        
        # Check if file exists in master storage
        # if not then return
        pcl.makeTextPacket('command:')
        
        # Check last time the file was modified
        
        
        # Send file to master storage
        pass
    
    
    
    def addDir(self,dir_path):
        """
        
        
        Inputs
        --------
        
        dir_path : str
            path to local directory that is to be uploaded to repository
            
        """
        pass



    def addMasterDir(self,folder_path):
        """
        
        
        Inputs
        --------
        
        folder_path : str
            path to local directory that is to be uploaded to repository as a 
            new master folder
            
        """
        pass
    


    def commit(self,folder_path):
        """
        
        
        Inputs
        --------

        folder_path : str
            path to local directory that is to be uploaded to repository
            TODO : may not need this if there is a local file manager
        """
        pass


    def delete(self,folder_or_file_path):
        """
        
        
        Inputs
        --------
            
        filename : str
            path or filename that is to be deleted from the repository
            
        """
        pass
    


    def findFile(self,filename):
        """
        
        
        Inputs
        --------

        filename : str
            filename of file in the storage repository that is to be searched
            for. 
            Can be a regular expression
            
        """
        
        # Make a command packet
        # -----------------------
        reply = self.cmd('findfile',filename)
        
        return reply=='True'


    def getFileInfo(self,filename):
        """
        Get information about a file in the remote repository
        
        Inputs
        --------

        filename : str
            path/filename to remote file 
            
        Output
        ----------
        file_info : namedtuple
            File info with fields:
            size_bytes : size of file in bytes
            last_modified : date 
            
        """
        pass

    

    def xxxx(self,master_folder_name,XX):
        """
        
        
        Inputs
        --------
        master_folder_name : str
            Name of master folder to store file in
            
        filename : str
            path/filename to local file that is to be uploaded to repository
            
        """
        pass
    
    
    def cmd(self,command,parameters):
        """
        Send a command to the server
        
        Inputs
        ----------
        command : str
            Command name
            
        parameters : list of str
            list of parameters, they must all be strings
            
        """
        
        if isinstance(parameters,str):
            parameters = [parameters]
            
        # Check everything is a string
        assert all([isinstance(s,str) for s in parameters]), "FileTransferClient/cmd: All parameters must be strings"
        
        # Make the command packet
        cmd_packet = pcl.makeTextPacket('command',[command]+parameters)
        
        # Send to server
        reply = self.send(cmd_packet)
        
        return reply
        
        


#==============================================================================
#%% Functions
#==============================================================================

