from authenticate import authorize
from data import data
import os, sys

# def find_root(service):
    
#     page_token = None

#     while True:
#         results = service.files().list(
#                 q = "'root' in parents",
#                 fields = "nextPageToken, files(id, name, mimeType, ownedByMe, parents, size)",
#                 pageToken = page_token
#             ).execute()
        
#         for file in results.get('files',[]):
#             print(file['name'])

#         page_token = results.get('nextPageToken',None)
#         if page_token is None:
#             break

def createSync(service):

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


def main():
    
    curData = data()
    service = authorize()

    # If the file doesn't exists
    if not curData.exists:
        
        # Get the ID of the sync folder in the drive
        id = createSync(service)

        # Create the file with the required data
        curData.createFile(os.uname()[1],id)
    

if __name__ == "__main__":
    main()