import os, sys
from authenticate import authorize
from googleapiclient.http import MediaFileUpload

def uploadFile(filePath, service, par_id):
    """
    Uploads the content of a file to the given directory id.
    """

    # Uploads the file under the directory pointed by par_if
    metadata = {
        'name' : os.path.basename(filePath),
        'parents' : [par_id]
    }

    content = MediaFileUpload(filePath, resumable= True, chunksize=524288)

    request = service.files().create(
                body = metadata, 
                media_body = content 
            )

    print("{} - Preaparing file\r".format(os.path.basename(filePath)),end = "")

    #Upload in chunks
    response = None
    while response is None:
        
        # Print the status of the upload
        status, response = request.next_chunk()
        if status:
            print("{} - Uploading ( {:.2%} )\r".format(os.path.basename(filePath),
                                                         status.progress()), end = "")

    print("{} - Upload Complete       ".format(os.path.basename(filePath)))


def removeFile(service, Fid, name):
    """
    Remove the file with the given id
    """

    if name:
        print("{} Deleted".format(name))

    # Delete the file given by its is id
    service.files().delete(fileId=Fid).execute()


def removeExtra(localPath, service, driveFolderID, init = None):
    
    """
    localPath points to a sync file or folder supposed to be under the drive folder pointed by driveFolderID.
    The function removes extra contents in the drive folder not in the local one.
    """

    contents = init

    # The contents of the local directory
    if contents is None:
        contents = [content for content in os.listdir(localPath)]
        print("Removing extra files from {}".format(localPath))


    page_token = None
    while True:
    
        # Look for all contents in the parent directory
        results = service.files().list(
                q = "'{}' in parents".format(driveFolderID),
                fields = "nextPageToken, files(id, name)",
                pageToken = page_token
            ).execute()

        # Look through the contents of the folder of the drive
        for file in results.get('files',[]):

            # If the file is not in the directory
            if file['name'] not in contents:
                
                # Remove the file from the drive
                removeFile(service, file['id'], file['name'])
        
            else:

                path = os.path.join(localPath, file['name'])
                
                # Remove the extra contents in that directory
                if os.path.isdir(path):
                    removeExtra(path, service, file['id'])
        
                        
        page_token = results.get('nextPageToken',None)
        if page_token is None:
            break


def syncFolder(syncPath, service, par_id):
    """
    Syncs a particular local folder under the specified parent directoty.
    If the local file doesn't already exist, it uploads the contents of the file.
    """
    page_token = None
    
    while True:
    
        # Look for all folders in the parent directory
        results = service.files().list(
                q = "'{}' in parents".format(par_id),
                fields = "nextPageToken, files(id, name, size)",
                pageToken = page_token
            ).execute()
        
        # If the required folder to be synced is found, check if all
        # the contents of the directory are present in the drive

        for file in results.get('files',[]):
            if os.path.basename(syncPath) == file['name']:

                # After finding the item, check whether it is a directory or file
                # If directory, recurse and sync all of its contents
                if os.path.isdir(syncPath):

                    print("{} - Recursing".format(os.path.basename(syncPath)))

                    for fileFolder in os.listdir(syncPath):
                        fileFolder = os.path.join(syncPath,fileFolder)
                        syncFolder(fileFolder,service, file['id'])

                    print("{} - Complete".format(os.path.basename(syncPath)))

                # If file, check whether the contents are the same
                else:

                    # If they are not the same, remove the old and upload the new
                    if not ( abs( os.stat(syncPath).st_size - int(file['size']) ) < 10 ) :
                        print("{} - Updating\r".format(os.path.basename(syncPath)),end="") 
                        removeFile(service, file['id'], None)
                        uploadFile(syncPath, service, par_id)

                    # else:
                    #     print("{} - Already Present".format(os.path.basename(syncPath)))

                return

        page_token = results.get('nextPageToken',None)
        if page_token is None:
            break
    
    # If the directory is not present, create it.
    if os.path.isdir(syncPath):

        print("{} - Directory Created".format(os.path.basename(syncPath)))

        # Creating the directory under the parent directory
        metadata = {
            'name' : os.path.basename(syncPath),
            'mimeType' : 'application/vnd.google-apps.folder',
            'parents'  : [par_id]
        }

        # Getting the ID of the created directory
        fileData = service.files().create(
                        body = metadata,
                        fields = 'id'
                        ).execute()

        # Syncing the subfolders
        for fileFolder in os.listdir(syncPath):
            fileFolder = os.path.join(syncPath,fileFolder)
            syncFolder(fileFolder,service, fileData['id'])
        
        print("{} - All contents uploaded".format(os.path.basename(syncPath)))

    # If it is a file, upload it
    else:
        uploadFile(syncPath, service, par_id)


def createSync(service):

    """
    Looks for the local computer's sync folder in the drive. If it is present, it returns its id.
    If not, it creates the folder and returns the id.
    """

    page_token = None
    hostname = os.uname()[1]

    while True:

        # Look for all folders in the root directory
        results = service.files().list(
                q = "'root' in parents and mimeType = 'application/vnd.google-apps.folder'",
                fields = "nextPageToken, files(id, name)",
                pageToken = page_token
            ).execute()
        
        # If required folder is found, return its ID
        for file in results.get('files',[]):
            if "G_{}".format(hostname) == file['name']:
                return file['id']

        page_token = results.get('nextPageToken',None)
        if page_token is None:
            break

    # Else create the folder

    print("Creating Root Folder for syncing")

    metadata = {
        'name' : 'G_{}'.format(hostname),
        'mimeType' : 'application/vnd.google-apps.folder'
    }

    fileData = service.files().create(
                    body = metadata,
                    fields = 'id'
                    ).execute()

    # And return its id
    return fileData['id']


if __name__ == "__main__":

    service = authorize()
    syncRoot = createSync(service)
    syncFolder("/home/thelethalcode/Downloads", service, syncRoot)
    # removeExtra(os.path.expanduser("~"), service, syncRoot)
