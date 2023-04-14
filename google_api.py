import os
from flask import Flask, request, url_for, session, redirect

# Import google APIs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Get and Set environment variable
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
GOOGLE_SCOPES = os.environ['GOOGLE_SCOPES']
SECRETS_FILE = os.environ['SECRETS_FILE']

'''
Convert Credential into dictonary format
'''


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


'''
Google Auth
A standardized way to get authorization url
'''


def google_auth(redirect_uri):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # steps.
    flow = InstalledAppFlow.from_client_secrets_file(
        SECRETS_FILE, scopes=GOOGLE_SCOPES)

    # The URI created here must exactly match one of the authorized redirect
    # URIs for the OAuth 2.0 client, which you configured in the API Console.
    # If this value doesn't match an authorized URI, you will get a
    # 'redirect_uri_mismatch' error.
    flow.redirect_uri = url_for(redirect_uri, _external=True, _scheme='https')

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server
        # apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    session['AUTH_STATE_KEY'] = state

    return authorization_url


'''
set_credentials
Return credentials to connect with people API
'''


def set_credentials(redirect_uri):
    state = session['AUTH_STATE_KEY']

    flow = InstalledAppFlow.from_client_secrets_file(
        SECRETS_FILE, scopes=GOOGLE_SCOPES, state=state)
    flow.redirect_uri = url_for(redirect_uri, _external=True, _scheme='https')

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # In a production app, you likely want to save these
    # credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)


'''
Connect to the People API.
Return the name of all connections.
'''


def user_contacts():
    # Get credential from session
    credentials = Credentials(
        **session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)

    # Build connection to people API
    service = build('people', 'v1', credentials=credentials)

    # Get user contacts
    try:
        # Build connection to people API
        service = build('people', 'v1', credentials=credentials)
        person_fields = 'names,emailAddresses,phoneNumbers,addresses'

        # Call the People API
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=25,
            personFields=person_fields).execute()

        # Get all the contacts details
        connections = results.get('connections', [])
        contacts_list = []

        # Get necessary contacts details from connections list
        for person in connections:
            metadata = person.get('metadata', [])
            names = person.get('names', [])
            emails = person.get('emailAddresses', [])
            phoneNumbers = person.get('phoneNumbers', [])
            addresses = person.get('addresses', [])

            # Get all the values form indivual list
            first_name = names[0]['givenName'] if names else ''
            try:
                if names[0]['familyName']:
                    last_name = names[0]['familyName']
            except BaseException:
                last_name = ''

            id = metadata['sources'][0].get('id') if metadata else 1
            name = names[0].get('displayName') if names else ""
            email = emails[0].get('value') if emails else ""
            phone = phoneNumbers[0].get('value') if phoneNumbers else ""
            country = addresses[0].get('country') if addresses else ""
            resourceName = person.get('resourceName').split("/")
            # Appened the contacts list with each contact's detail
            contacts_list.append({
                "id": id,
                "name": name,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "resourceName": resourceName[1],
                "country": country,
                "etag": person.get('etag')

            })

        return contacts_list
    except BaseException:
        redirect(url_for('index', _external=True, _scheme='https'), code=302)


'''
Connect to the People API.
Add the user contact.
'''


def create_google_contact(data):

    # Get credential from session
    credentials = Credentials(
        **session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)

    # Build connection to people API
    try:
        service = build('people', 'v1', credentials=credentials)

        # Create New Contact
        newContact = {
            "names": [
                {
                    "givenName": data['first_name'][0],
                    "familyName": data['last_name'][0]
                }
            ],
            "emailAddresses": [
                {
                    'value': data['email'][0]
                }
            ],
            "phoneNumbers": [
                {
                    'value': data['phone'][0]
                }
            ],
            "addresses": [
                {
                    'country': data['country_name']
                }
            ]
        }
        # Add New contact to the user
        service.people().createContact(body=newContact).execute()
    except BaseException:
        redirect(url_for('index', _external=True, _scheme='https'), code=302)


'''
Connect to the People API.
Add the user contact.
'''


def delete_google_contact(contactResourceName):
    # Get credential from session
    credentials = Credentials(
        **session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)

    # Build connection to people API
    try:
        service = build('people', 'v1', credentials=credentials)

        # Delete contact to the user
        service.people().deleteContact(
            resourceName='people/' +
            contactResourceName).execute()

    except BaseException:
        return redirect(
            url_for(
                'index',
                _external=True,
                _scheme='https'),
            code=302)


'''
Get a contact information to edit
'''


def get_single_contact(resourceName):
    # Get credential from session
    credentials = Credentials(
        **session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)

    # Build connection to people API
    try:
        service = build('people', 'v1', credentials=credentials)
        person_fields = 'names,emailAddresses,phoneNumbers,addresses'
        results = service.people().get(resourceName='people/'+resourceName,
                                       personFields=person_fields).execute()

        # Get all the list for contact detail
        names = results.get('names', [])
        emails = results.get('emailAddresses', [])
        phone_numbers = results.get('phoneNumbers', [])
        addresses = results.get('addresses', [])

        # Get all the details for contact
        first_name = names[0]['givenName'] if names else ''
        try:
            if names[0]['familyName']:
                last_name = names[0]['familyName']
        except BaseException:
            last_name = ''
        # Get all the contacts details
        contact_detail = {
            "first_name": first_name,
            "last_name": last_name,
            "email": emails[0].get('value') if emails else '',
            "phone": phone_numbers[0].get('value') if phone_numbers else '',
            "resourceName": resourceName,
            "etag": results.get('etag'),
            "country": addresses[0].get('country') if addresses else ''
        }
        return contact_detail
    except BaseException:
        redirect(url_for('index', _external=True, _scheme='https'), code=302)


'''
Update google contact
'''


def update_google_contact(contactResourceName, data):
    # Get credential from session
    credentials = Credentials(
        **session['credentials'])
    session['credentials'] = credentials_to_dict(credentials)
    # Build connection to people API
    try:
        service = build('people', 'v1', credentials=credentials)

        # Update Contact
        updateContactInfo = {
            "resourceName": 'people/' + contactResourceName,
            "etag": data['etag'],
            "names": [
                {
                    "givenName": data['first_name'],
                    "familyName": data['last_name']
                }
            ],
            "emailAddresses": [
                {
                    'value': data['email']
                }
            ],
            "phoneNumbers": [
                {
                    'value': data['phone']
                }
            ],
            "addresses": [
                {
                    'country': data['country_name']
                }
            ]
        }
        # Update contact information
        result = service.people().updateContact(
            resourceName='people/' + contactResourceName,
            updatePersonFields='names,emailAddresses,phoneNumbers,addresses',
            body=updateContactInfo).execute()
    except BaseException:
        return redirect(
            url_for(
                'index',
                _external=True,
                _scheme='https'),
            code=302)


'''
Delete all Session varibables.
'''


def google_logout():
    # Delete session variables
    session.pop('credentials', None)
    session.pop('AUTH_STATE_KEY', None)
    session.clear()
