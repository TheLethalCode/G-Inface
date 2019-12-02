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


def removeFile(service, id):
    """
    Remove the file with the given id
    """

    # Delete the file given by its is
    service.files().delete(id)


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
                    for fileFolder in os.listdir(syncPath):
                        syncFolder(fileFolder,service, file['id'])

                # If file, check whether the contents are the same
                else:

                    # If they are not the same, remove the old and upload the new
                    if not ( abs( os.stat(syncPath).st_size - file['size'] ) < 100 ) : 
                        removeFile(service, file['id'])
                        uploadFile(syncPath, service, par_id)

                return

        page_token = results.get('nextPageToken',None)
        if page_token is None:
            break
    
    # If the directory is not present, create it.
    if os.path.isdir(syncPath):

        # Creating the directory under the parent directory
        metadata = {
            'name' : os.path.basename(syncFolder),
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
            syncFolder(fileFolder,service, fileData['id'])

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
    uploadFile(sys.argv[1], service, syncRoot)
