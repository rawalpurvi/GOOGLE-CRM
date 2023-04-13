GOOGLE-CRM

I wanted to learn how to add google sign-in button to the application and how to conntect with google API, so I built this small application. The web application of GOOGLE-CRM is built to connect with google's people API to perfrom CRUD operations to the user contacts. Google user can create, update and delete their contacts using this application. This application is using people api to do this operations. This applications runs on python3 and flask. I download md4 bootstrap (https://mdbootstrap.com/docs/b4/) and save into static folder for fronend design.

Getting Started

    ## Pre-requisites and Local Development

    Run this application one should have Python3, pip on their local machines.

    Setup ngrok for secure host (https://dashboard.ngrok.com/get-started/setup) or get SSL for local server.

    ## Get Google credetials

    Follow the steps described in Setup(https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid) to configure your OAuth Consent Screen and to obtain a Client ID.

    Set all enpoints for the application to redirecting from google on `Client ID for Web application`.

    Authorized JavaScript origins (need https or use ngrok):

    https://localhost:8888
    https://localhost:8888/login


    Authorized redirect URIs (need https or use ngrok):

    https://localhost:8888/login
    https://localhost:8888/user_contact_info
    https://localhost:8888/contacts
 

    Get all the credentials and dwonload credential file on local. 

    Save secret file as `credentials.json` outside the folder to get credential for connection to the google's people api.

    Add test users in your Google cloud application to define which user can login to this applcation.

    Save value as an environment variable. Here are the variable list:

    GOOGLE_SCOPES
    SECRETS_FILE
    GOOGLE_CLIENT_ID

    ## How to run the application

    Download code and set virual environment to install requirnments with this command:

    source env/bin/activate

    From folder run pip install requirements.txt . All required packages are included in the requirenments file. 

    To run the application run the following commands:

    python3 app.py

    The application is run on http://127.0.0.1:8888/ by default but need to setup ngrok or SSL to run the web app on secure server https.


Web Application Preference

    ## Getting Started

    Base Url: At present this app can only be run locally and is not hosted as a base url. The app is hosted at the default, http://127.0.0.1:8888/ , need to get a secure host.

    Authentication: This version of the application does not require authentication and API keys.

    ## Functionalities

    1. Get Contacts

    GET '/user_contact_info'
    - Fetches all contacts information of google user who logged in to this applicaton.
    - Request Arguments: None
    - Returns: List of values for each contact Name, Email, Phonenumber, country. 

    2. Add Contact

    POST '/add_contact'
    - Allow user to add new contact.
    - Request Arguments: None
    - User can add Name, Email, Phonenumber and country name for contact.

    3. Delete Contact

    DELETE '/contacts/<delete_id>/delete'
    - Delete contact form google account using contact resourceName
    - Request Argument: delete_id
    - Show rest of the contacts in the list


    4. Update Contact

    POST '/edit_contact/<edit_resouceName>'
    - Request Data: ResourceName for the contact
    - Update Name, Email, Phonenumber and Country Name of that contact
    - Return list of contacts with updated contact


Deployment N/A

Author

Purvi Rawal

Acknoledgemnts

Team of Google for the documents for Sign In with Google and People API.