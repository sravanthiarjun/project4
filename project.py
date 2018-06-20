from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from flask import url_for
from flask import flash


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Company, Gadgets, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Electronic Gadgets Application"


# Connect to database and create database session
engine = create_engine('sqlite:///electronic.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def showLogin():
    session = DBSession()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    session = DBSession()
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Upgrade  credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check valid token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error to get abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that access user is valid or not
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify token valid for appilication or not
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token in session use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # check whether user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' \" style = \"width: 300px;'
    output += 'height: 300px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            flash("you have succesfully been logout")
            return redirect(url_for('showCompany'))
    else:
        flash("you were not logged in")
        return redirect(url_for('showCompany'))


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    session = DBSession()
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
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Comapny Information
@app.route('/companies/<int:item_id>/menu/JSON')
def companyMenuJSON(item_id):
    session = DBSession()
    item = session.query(Company).filter_by(id=item_id).one()
    items = session.query(Gadgets).filter_by(
        item_id=item_id).all()
    return jsonify(Gadgets=[i.serialize for i in items])


@app.route('/companies/<int:item_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(item_id, menu_id):
    session = DBSession()
    Menu_Item = session.query(Gadgets).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/companies/JSON')
def companyJSON():
    session = DBSession()
    thing = session.query(Company).all()
    return jsonify(thing=[r.serialize for r in thing])


# shows all companies
@app.route('/')
@app.route('/companies/')
def showCompany():
    session = DBSession()
    thing = session.query(Company).order_by(asc(Company.name))
    session.close()
    return render_template('company.html', thing=thing)

# create new company


@app.route('/companies/new/', methods=['GET', 'POST'])
def newCompany():
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newThing = Company(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newThing)
        flash('New Thing %s Successfully Created' % newThing.name)
        session.commit()
        session.close()
        return redirect(url_for('showCompany'))
    else:
        return render_template('newCompany.html')

# used to edit the company


@app.route('/companies/<int:item_id>/edit/', methods=['GET', 'POST'])
def editCompany(item_id):
    session = DBSession()
    editedThing = session.query(
        Company).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if editedThing.user_id == login_session['user_id']:
            if request.method == 'POST':
                if request.form['name']:
                    editedThing.name = request.form['name']
                    flash('Company Successfully Edited %s' % editedThing.name)
                    session.add(editedThing)
                    session.commit()
                    session.close()
                return redirect(url_for('showCompany'))
            else:
                return render_template('editCompany.html', thing=editedThing)
        else:
            flash('No permision!!')
            return redirect(url_for('showCompany', item_id=item_id))

# used to delete the company


@app.route('/companies/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteCompany(item_id):
    session = DBSession()
    thingToDelete = session.query(
        Company).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if thingToDelete.user_id == login_session['user_id']:
            if request.method == 'POST':
                session.delete(thingToDelete)
                flash('%s Successfully Deleted' % thingToDelete.name)
                session.commit()
                session.close()
                return redirect(url_for('showCompany', item_id=item_id))
            else:
                return render_template(
                    'deleteCompany.html', thing=thingToDelete)
        else:
            flash('No permision!!')
            return redirect(url_for('showCompany', item_id=item_id))
# shows the items in the company


@app.route('/companies/<int:item_id>')
@app.route('/companies/<int:item_id>/menu/')
def showMenu(item_id):
    session = DBSession()
    thing = session.query(Company).filter_by(id=item_id).one()
    items = session.query(Gadgets).filter_by(
        item_id=item_id).all()
    session.close()
    return render_template('gadget.html', items=items, thing=thing)


# used to ceate a new menu item
@app.route('/companies/<int:item_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(item_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    thing = session.query(Company).filter_by(id=item_id).one()
    if login_session['user_id'] == thing.user_id:
        if request.method == 'POST':
            newItem = Gadgets(
                name=request.form['name'],
                description=request.form['description'],
                price=request.form['price'],
                item_id=item_id,
                user_id=thing.user_id
                                            )
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' + newItem.name)
            session.close()
            return redirect(url_for('showMenu', item_id=item_id))
        else:
            return render_template('newmenuitem.html', item_id=item_id)
    else:
        flash("No permissions!!")
        return redirect(url_for('showCompany', item_id=item_id))
# used to edit a menu item


@app.route(
    '/companies/<int:item_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST'])
def editMenuItem(item_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Gadgets).filter_by(id=menu_id).one()
    thing = session.query(Company).filter_by(id=item_id).one()
    if login_session['user_id'] == thing.user_id:
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['price']:
                editedItem.price = request.form['price']
            session.add(editedItem)
            session.commit()
            session.close()
            flash('Menu Item Successfully Edited')
            return redirect(url_for('showMenu', item_id=item_id))
        else:
            return render_template(
                'editmenuitem.html',
                item_id=item_id, menu_id=menu_id, item=editedItem)
    else:
        flash("No permissions!!")
        return redirect(url_for('showCompany', item_id=item_id))
# used to delete the menu item


@app.route(
    '/companies/<int:item_id>/menu/<int:menu_id>/delete',
    methods=['GET', 'POST'])
def deleteMenuItem(item_id, menu_id):
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    thing = session.query(Company).filter_by(id=item_id).one()
    thingToDelete = session.query(Gadgets).filter_by(id=menu_id).one()
    if login_session['user_id'] == thing.user_id:
        if request.method == 'POST':
            session.delete(thingToDelete)
            session.commit()
            session.close()
            flash('Menu Item Successfully Deleted')
            return redirect(url_for('showMenu', item_id=item_id))
        else:
            return render_template('deletemenuitem.html', item=thingToDelete)
    else:
        flash("No permissions!!")
        return redirect(url_for('showCompany', item_id=item_id))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
