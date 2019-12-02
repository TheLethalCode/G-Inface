from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
 
def authorize():
    """
    Returns an object for interacting with the drive api service
    """
    
    # The level of access to the drive folder. Here, complete access is requested
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Get the credentials if file already exists
    store = file.Storage('credentials.json')
    creds = store.get()

    # If token doesn't exist, or isn't valid, request new token
    if not creds or creds.invalid:

        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES, prompt='consent')
        
        # Open the browser requesting the authorisation from the user with the 
        # requested scopes. It waits for the access grant, and redirects it to a 
        # locally running server. Using this, the server requests an authorizstion
        # token. It also stores the credentials in the credentials.json file
        
        creds = tools.run_flow(flow, store)
    
    # Generates a resource object for interacting with the services of the api
    service = build('drive','v3',credentials=creds)
    return service


if __name__ == "__main__":
    service = authorize()