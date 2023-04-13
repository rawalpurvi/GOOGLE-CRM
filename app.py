from __future__ import print_function
from pickle import NONE
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_wtf import Form
from forms import *

import os
import hashlib
import json

# Import google_api for authorization & coonect to people API
from google_api import (
    google_auth,
    set_credentials,
    user_contacts,
    create_google_contact,
    delete_google_contact,
    get_single_contact,
    update_google_contact,
    google_logout
)

# Third-party libraries
from flask import (
    Flask,
    render_template,
    request,
    Response,
    redirect,
    url_for,
    session,
    jsonify
)

# create and configure the app
app = Flask(__name__)



# Create seceret key for google login
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# Set state for google login button
state = hashlib.sha256(os.urandom(1024)).hexdigest()

# Get google client Id from environment
GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']


'''
Login page get Google Signin Button.
'''
@app.route('/')
def index():
    # render login page
    return render_template("index.html", state=state, GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)


'''
After user login set all values into session.
'''
@app.route('/login', methods=['POST', 'GET'])
def login():
    # Get google credential and decode using jose
    token = request.form.get("credential")

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        user_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Set variables to session 
        session['user_id'] = user_info["sub"]
        session['user_name'] = user_info["name"]
        session['user_email'] = user_info["email"]

    except ValueError:
        # Invalid token
        raise ValueError('Invalid token')

    # Get authorization url using google_auth
    authorization_url = google_auth('user_contact_info')
    # Redirect authoriztion url
    return redirect(authorization_url)

'''
Get all contacts information for user.
'''
@app.route('/user_contact_info', methods=['GET'])
def user_contact_info():
    try:
        # Check if user is logged in
        if 'user_id' in session:
            form = ContactForm()
            # if state parameter in the responce url set all the credeential
            if request.args.get('state', default=None, type=None):
                set_credentials('user_contact_info')

            # Get all the contacts
            show_results = user_contacts()

            return render_template("main.html", name=session['user_name'], email=session['user_email'], contacts=show_results,form=form)
        # if user is not logged in redirect to login page
        else:
            return redirect(url_for('index', _external=True,_scheme='https'))
    except:
        return redirect(url_for('index', _external=True,_scheme='https'))


'''
Render add contact page for user. 
'''
@app.route('/add_contact', methods=['GET'])
def add_contact():
    # Check if user is logged in
    if 'user_id' in session:
        form = ContactForm()
        form.country_name.coerce = str
        form.country_name.default = 'US'
        form.process()
        return render_template('add_contact.html', name = session['user_name'], email=session['user_email'],form=form)
    # if user is not logged in redirect to login page
    else:
        return redirect(url_for('index', _external=True,_scheme='https'))

'''
Add new contact information for user.
'''
@app.route('/add_contact', methods=['POST'])
def add_user_contact():
    data = {}
    if 'user_id' in session:
        form = ContactForm()
        
        if form.validate_on_submit():

                # Get form data
                data['first_name'] = request.form.get("first_name"),
                data['last_name'] = request.form.get("last_name"),
                data['email'] = request.form.get("email"),
                data['phone'] =  request.form.get("phone"),
                data['country_name'] =  request.form.get("country_name")

                # create user contact
                create_google_contact(data)

                return redirect(url_for('user_contact_info'))
        else:
                print(form.errors)
                return render_template('add_contact.html', name = session['user_name'], email=session['user_email'],form=form)
    else:
        return redirect(url_for('index', _external=True,_scheme='https'))

'''
Delete contact information for user.
'''
@app.route('/contacts/<delete_id>/delete', methods=['DELETE'])
def delete_user_contact(delete_id):

    if 'user_id' in session:
        # Delete contact
        delete_google_contact(delete_id)

        # Return list after delete the contact
        return jsonify({
            'message': 'Contact ' + delete_id + ' was successfully deleted!',
            'success': True,
            'url': url_for('user_contact_info')
        })

    else:
        return redirect(url_for('index', _external=True,_scheme='https'))
    

'''
Show contact information for update information
'''
@app.route('/edit_contact/<edit_resouceName>', methods=['GET'])
def show_contact(edit_resouceName):
    # shows the Edit contact page with the given resource
    # Check if user is logged in
    if 'user_id' in session:
        # Fetch venue information for that contact
        show_results = get_single_contact(edit_resouceName)

        return render_template('edit_contact.html', name = session['user_name'] , email=session['user_email'], contact=show_results)
    # if user is not logged in redirect to login page
    else:
        return redirect(url_for('index', _external=True,_scheme='https'))

'''
Update contact information
'''
@app.route('/edit_contact/<edit_resouceName>', methods=['POST'])
def update_contact(edit_resouceName):
    data = {}
    # Get all the value to update google contact for user
    if 'user_id' in session:
        form = ContactForm()
        
        # Get form data
        data['first_name'] = request.form.get("first_name")
        data['last_name'] = request.form.get("last_name")
        data['email'] = request.form.get("email")
        data['phone'] =  request.form.get("phone")
        data['etag'] = request.form.get("etag")
        data['country_name'] =  request.form.get("country_name")

        if form.validate_on_submit():
            
            # Update user contact
            update_google_contact(edit_resouceName,data)

            return redirect(url_for('user_contact_info'))
        else:
            #Print errors from validation
            print(form.errors)
            # Get all the contacts
            try:
                show_results = user_contacts()
                return render_template("main.html", name=session['user_name'], email=session['user_email'],
                                                contacts=show_results,form=form,data=json.dumps(data),
                                                edit_resouceName=edit_resouceName,
                                                show_modal_on_page_load=True)
            except:
                return redirect(url_for('index', _external=True,_scheme='https'))

    else:
        return redirect(url_for('index', _external=True,_scheme='https'))



'''
Delete all session variables.
'''
@app.route('/user_logout')
def user_logout():
    
    # Pop all session variables
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)

    # Remove all session data. 
    session.clear()
    google_logout()

    # render login page
    return redirect(url_for('index', _external=True,_scheme='https'))


if __name__ == '__main__':
    app.run(port=8888, debug=True)