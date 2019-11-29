from authenticate import authorize
from data import data
import sync
import os, sys

def syncAll(data, service):

    """
    Syncs the local folders specified to the drive
    """

    for folder in data.foldersUpload:
        sync.syncFolder(folder, service, data.folderId)


def addFolders(data, folders):
    """
    Adds the given folders to the list of contents to sync
    """
    pass


def removeFolders(data, folders):
    """
    Removes the folders from the list of contents to be synced
    """
    pass


def main():
    
    # Initialize the data and service objects
    curData = data()
    service = authorize()

    # If the file doesn't exists
    if not curData.exists:
        
        # Get the ID of the sync folder in the drive and create the json file
        id = sync.createSync(service)
        curData.createFile(os.uname()[1],id)
    
    

if __name__ == "__main__":
    main()