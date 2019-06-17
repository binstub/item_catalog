# coding=utf8
import json
import random
import string

import httplib2
import requests
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
)
from flask import make_response
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User


app = Flask(__name__)
app.secret_key = 'super_secret_key'


# Retrieve Client Id from client secrets file retrieved from google
# developer console
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


# Connect to Database and create database session
engine = create_engine('postgresql://catalog:catalog@localhost/itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


# Login Login session from google sign in using OATH
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id
    print login_session['access_token']
    print login_session['google_id']

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if not create user
    logged_user_id = getUserID(data['email'])
    if not logged_user_id:
        logged_user_id = createUser(login_session)
    login_session['user_id'] = logged_user_id

    login_session['logged_in'] = True

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# ------------------------------------------------------
# USER HELPER FUNCTIONS
# ------------------------------------------------------
# Get the user id for the session
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# Get the user info based on the user id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    print user_id
    return user


# Create a new user if there isn't one already there
def createUser(login_session):
    print login_session
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['logged_in']

        flash("you are now been disconnected")

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/category/<int:category_id>/JSON')
def items_by_category_JSON(category_id):
    # category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# View JSON info of one specific item from one specific category
@app.route('/category/<int:category_id>/<int:item_id>/JSON')
def item_JSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# View JSON info of all categories
@app.route('/categories/JSON')
def categories_JSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog.JSON')
def getCatalog():
    """ Returns a JSON version of the catalog """
    catalog_json = []
    categories = session.query(Category).all()
    for category in categories:
        items = category.items
        builder = {}
        builder["id"] = category.id
        builder["name"] = category.name
        builder["items"] = [i.serialize for i in items]
        catalog_json.append(builder)
    return jsonify(Catalog=catalog_json)


# Show Catalog
@app.route('/')
@app.route('/catalog')
def show_categories():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Category).order_by(Category.name).all()
    return render_template(
        'categories.html',
        categories=categories
    )


# Displays a list of all items in this category
@app.route('/catalog/<category_name>/items')
def show_items(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    if 'logged_in' not in login_session:
        logged_in = False
    else:
        logged_in = login_session['logged_in']
    return render_template('items.html',
                           items=category.items,
                           category=category_name,
                           logged_in=logged_in)


# Displays Item details
@app.route('/catalog/<category_name>/<item_name>')
def show_item(category_name, item_name):
    if 'logged_in' not in login_session:
        logged_in = False
    else:
        logged_in = login_session['logged_in']
    return render_template(
        'item.html',
        page_heading=item_name,
        category_name=category_name,
        item=session.query(Item).filter_by(title=item_name).one(),
        logged_in=logged_in
    )


# Adds items to categories. Check sfor user authorization
@app.route('/catalog/<category_name>/add', methods=['GET', 'POST'])
def add_item(category_name):

    if 'username' not in login_session:
        return redirect('/login')

    if login_session['user_id'] == getUserID(login_session['email']):
        if request.method == 'POST':
            # receive values from html form
            item_title = request.form['item_title']
            item_desc = request.form['item_desc']
            category = session.query(Category).filter_by(
                name=category_name
            ).one()
            # store item into database
            item = Item(title=item_title,
                        description=item_desc,
                        category=category,
                        owner=getUserInfo(login_session['user_id']))
            session.add(item)
            session.commit()
            flash('%s has been successfully added' % item_title)
            # redirect to the items list of this category
            return redirect(url_for(
                'show_items',
                category_name=category_name))
        else:
            return render_template("add_item.html",
                                   category=category_name)
    else:
        return redirect(url_for('show_categories'))


# Edits items detail page
@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure the user is the owner of the item
    if user_authorized(item_name, login_session['user_id']) is False:
        flash('You are not authorized to edit %s.' % item_name)
        return redirect(url_for('show_categories'))

    if request.method == 'POST':
        print "inside post"
        # receive values from html form
        edit_title = request.form['edit_title']
        edit_desc = request.form['edit_desc']
        edit_category = request.form['edit_category']
        # retrieve category object
        category = session.query(Category).filter_by(name=edit_category).one()
        # retrieve the item object:
        item = session.query(Item).filter_by(title=edit_title).one()
        # Update the values:
        item.title = edit_title
        item.description = edit_desc
        item.category = category

        session.add(item)
        session.commit()
        flash("Item has been updated!")
        # redirect to items page
        return redirect(url_for(
            'show_item',
            category_name=edit_category,
            item_name=edit_title))
    else:
        item = session.query(Item).filter_by(title=item_name).one()
        return render_template("edit_item.html",
                               item=item,
                               category_name=item.category.name,
                               categories=session.query(Category).all())


# Delete Items from category
@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def del_item(item_name):
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')

    # Make sure the user is the owner of the item
    if user_authorized(item_name, login_session['user_id']) is False:
        flash('You are not authorized to delete %s.' % item_name)
        return redirect(url_for('show_categories'))

    if request.method == 'POST':
        # fetch item object
        item = session.query(Item).filter_by(title=item_name).one()
        category_name=item.category.name
        # delete the item from the database
        session.delete(item)
        session.commit()
        flash("%s has been deleted!" % item_name)
        # redirect to the items list of this category
        return redirect(url_for(
            'show_items',
            category_name=category_name))
    else:
        # GET Request : render the delete confirmation form
        item = session.query(Item).filter_by(title=item_name).one()
        return render_template(
            "delete_item.html",
            item=item,
            category_name=item.category.name
        )


def user_authorized(item_name, user_id):
    item = session.query(Item).filter_by(title=item_name).one()
    if item.owner.id == user_id:
        return True
    else:
        # The user is not the one who created the item and therefore not
        # authorized to make changes.
        return False


if __name__ == '__main__':

    # app.debug = True
    app.run(host='0.0.0.0', port=5000)
