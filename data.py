import json, os

class data(object):

    # Initializes the required class variables
    def __init__(self):
        
        # Check whether the file exists.
        if os.path.exists('.data.json'):
            
            # If it exists, load the values
            with open('.data.json','r') as jsDa:
                vals = json.load(jsDa)
            
            self.hostname = vals.get('hostname', False)
            self.folderId = vals.get('id', None)
            self.foldersUpload = vals.get('folders',[])
            
            # If the data is not there, mark it as not present
            if self.hostname is not None and self.folderId is not None:
                self.exists = True
            else:
                self.exists = False

        else:
            self.hostname = None
            self.folderId = None
            self.foldersUpload = None
            self.exists = False

    # Create the initialization file
    def createFile(self, hostname, id):

        # Create a new json file with the valid data
        self.hostname = hostname
        self.folderId = id
        self.foldersUpload = []

        dataVal = {
            'hostname' : hostname,
            'id' : id,
            'folders' : []
        }

        with open('.data.json','w') as jsDa:
            json.dump(dataVal,jsDa)

        self.exists = True


    # Update the folders to sync 
    def updateFolders(self, folders, remove):

        with open('.data.json','r') as jsDa:
            vals = json.load(jsDa)

        with open('.data.json','w') as jsDa:

            # Update the folders as required
            if remove:
                vals['folders'] = [item for item in vals['folders'] if item not in folders ]

            else:
                vals['folders'].extend([item for item in folders if item not in vals['folders']])
                # print(vals['folders'])
                # exit(0)
            # Dump the update list to the json file
            json.dump(vals, jsDa)

        self.foldersUpload = vals['folders']

