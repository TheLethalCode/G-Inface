from authenticate import authorize
from data import data
import sync
import os, sys

def usageInstructions():
    print("\nG-INFACE, the one program to sync all your files and folders!\n")
    print("OPTIONS: \n\t--sync - Syncs the folders added")
    print("\t--add <f1> <f2> .. - Adds folder to be synced")
    print("\t--remove <f1> <f2> .. - Removes folder to be synced")


def syncAll(dataObj, service):

    """
    Syncs the local folders specified to the drive
    """

    if not dataObj.foldersUpload:
        print("No folders to sync. Add folders to sync list first")
        return

    # Add all files to the drive folder
    for folder in dataObj.foldersUpload:
        sync.syncFolder(folder, service, dataObj.folderId)

    # # Remove extra files from drive folder
    for folder in dataObj.foldersUpload:
        sync.removeExtra(os.path.dirname(folder), service, dataObj.folderId, [os.path.basename(folder)])

    return


def addFolders(data, folders):
    """
    Adds the given folders to the list of contents to sync
    """

    # Converting paths to absolute
    folders = [os.path.expanduser(folder) for folder in folders]

    # Seeing if path exists
    folders = [item for item in folders if os.path.exists(item)]

    # If no valid paths exist in the list
    if not folders:
        print("No valid folders or files to add")
        return

    data.updateFolders(folders, False)
    print("Added Successfully")
    
    return


def removeFolders(data, folders):
    """
    Removes the folders from the list of contents to be synced
    """

    # Converting paths to absolute
    folders = [os.path.expanduser(folder) for folder in folders]

    data.updateFolders(folders, True)
    print("Removed Successfully")
    
    return


def main():
    
    # Initialize the data and service objects
    curData = data()
    service = authorize()

    # If the file doesn't exists
    if not curData.exists:
    
        # Get the ID of the sync folder in the drive and create the json file
        id = sync.createSync(service)
        curData.createFile(os.uname()[1],id)
    
    args = ["--sync","--add","--remove"]

    # If no options are provided
    if (len(sys.argv) == 1) or (sys.argv[1] not in args):
        usageInstructions()
        return

    # Sync option
    if sys.argv[1] == "--sync":
        syncAll(curData,service)
        return

    # Add option without folder
    if sys.argv[1] == "--add" and len(sys.argv) == 2:
        usageInstructions()
        return

    # Add option
    elif sys.argv[1] == "--add":
        addFolders(curData, sys.argv[2:])
        return

    # Remove option without folder
    if sys.argv[1] == "--remove" and len(sys.argv) == 2:
        usageInstructions()
        return

    # Remove option
    elif sys.argv[1] == "--remove":
        removeFolders(curData, sys.argv[2:])
        return
    

if __name__ == "__main__":
    main()