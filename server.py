from flask import Flask, request, render_template, redirect, jsonify,session, flash
import requests, json, re
from flask_sqlalchemy import SQLAlchemy
from email_confirm import send_confirmation_email

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = "LaunchMobilityFTW"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/test_db'

db = SQLAlchemy(app)

#abstract to models.py
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, unique=True)
  email = db.Column(db.String(80), unique=True)
  password = db.Column(db.String(120))
  confirmed = db.Column(db.Boolean, default=False)

  first_name = db.Column(db.String(120))
  middle_name = db.Column(db.String(120))
  last_name = db.Column(db.String(120))
  zip_code = db.Column(db.String(5))

  city = db.Column(db.String(120))
  county = db.Column(db.String(120))
  state = db.Column(db.String(120))


  def __init__(self, email, password):
    self.email = email
    self.password = password

  def __repr__(self):
    return '<User %r>' % self.email

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/registration')
def registration():
  return render_template('registration.html')

@app.route('/api/register', methods=['POST'])
def register_api():
  errors = []
  email = request.form['email']
  password = request.form['password']
  password_confirm = request.form['password_confirm']

#validate registration details
  if len(email) < 5:
    error = "Email prefix must include atleast 5 characters"
    errors.append(error)
  elif not EMAIL_REGEX.match(email):
    error = "Invalid Email Address"
    errors.append(error)
  if len(password) < 7:
    error = "Password must include atleast 7 characters"
    errors.append(error)
  if password != password_confirm:
    error = "Passwords must match"
    errors.append(error)

  if len(errors) > 0:
    return jsonify(errors = errors)
  else:
    user = User.query.filter_by(email=email).first()
    if user:
      errors.append("User already exists, please login or choose a unique email for account")
    else:
      user = User(email, password)

      if password == password_confirm:
        db.session.add(user)
        db.session.commit()

      #send account confirmation email
      #send_confirmation_email(user.email)
      #print('confirmation email sent to: test')
      return jsonify(
        email=user.email,
        message="User successfully registered!"
      )
      
@app.route('/register', methods=['POST'])
def register():
  #delineate routes for client and api, requires active http request
  #activated_route = request.url_rule

  email = request.form['email']
  password = request.form['password']
  password_confirm = request.form['password_confirm']

  #validate registration details
  if len(email) < 5:
    error = "Email prefix must include atleast 5 characters"
    flash(error)
  elif not EMAIL_REGEX.match(email):
    error = "Invalid Email Address"
    flash(error)
  if len(password) < 7:
    error = "Password must include atleast 7 characters"
    flash(error)
  if password != password_confirm:
    error = "Passwords must match"
    flash(error)

  if '_flashes' in session.keys():
        return redirect("/registration")

  #check for user in db
  user = User.query.filter_by(email=email).first()
  print(user)

  if user and user != '':
    #for client, return flash message and redirect to /registration
      flash("User already exists in db, please login or register unique email for account")
      return redirect('/registration')
  else:
    user = User(email, password)

    if password == password_confirm:
      db.session.add(user)
      db.session.commit()

      #send account confirmation email
      #send_confirmation_email(user.email)
      #print('confirmation email sent to: test')

    #api request from client
    else:
      return redirect('/')

@app.route('/api/profile/<email>')
@app.route('/profile/<email>')
##assumes user has authenticated successfully
def profile_view(email):
  activated_route = request.url_rule

  user = User.query.filter_by(email=email).first()

  if user.confirmed == True:
    if 'logged_in' in session and 'email' in session:
      if session['logged_in'] == True and session['email'] == email:
        if activated_route == '/api/profile/' + user.email:
          return jsonify(
            id=user.id,
            email=user.email,
            confirmed = user.confirmed,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            zip_code=user.zip_code,
            city=user.city,
            county=user.county,
            state=user.state
          )
        else:
          return render_template('profile.html', user=user)
  else:
    return redirect('/')

@app.route('/profile_edit/<email>')
#assumes user has authenticated successfully
def profile_edit(email):
  if 'logged_in' in session and 'email' in session:
    if session['logged_in'] == True and session['email'] == email:
      user = User.query.filter_by(email=email).first()
      return render_template('profile_edit.html', user=user)
  else:
    return redirect('/')

@app.route('/api/profile_edit/<email>/update', methods=['POST'])
@app.route('/profile_edit/<email>/update', methods=['POST'])
def profile_update(email):
  activated_route = request.url_rule

  user = User.query.filter_by(email=email).first()
  user.first_name = request.form['first_name']
  user.middle_name = request.form['middle_name']
  user.last_name = request.form['last_name']
  user.zip_code = request.form['zip_code']

  #gather geo data for user account
  geo_data = get_geo_data(user.zip_code)

  if geo_data["city"]:
    user.city = geo_data["city"]
  if geo_data["county"]:
    user.county = geo_data["county"]
  if geo_data["state"]:
    user.state = geo_data["state"]

  db.session.commit()

  #if request from mobile app to api
  if activated_route == '/api/profile_edit/<email>/update':
    return jsonify(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        zip_code=user.zip_code,
        city=user.city,
        county=user.county,
        state=user.state
        )

 #if request from client
  else:
    return redirect('/profile/'+ email)

@app.route('/api/confirm/<email>')
@app.route('/confirm/<email>')
def confirm_email(email):
  activated_route = request.url_rule

  user = User.query.filter_by(email=email).first()
  user.confirmed = True
  db.session.commit()
  print('user account confirmed!')

  if activated_route == '/api/confirm/' + email:
    return jsonify(
      message=f'User account: {email} activated! Please login to access your profile.'
    )
  else:
    #return flash message and redirect to login page
    return f'{user.email} has been activated! please login to access your account'
    #return redirect('/')

@app.route('/api/login', methods=['POST'])
@app.route('/login', methods=["POST"])
def login():
  activated_route = request.url_rule

  email = request.form['email']
  password = request.form['password']

  user = User.query.filter_by(email=email).first()
  print(user)

  if user:
    if user.confirmed == True:
      if password == user.password and user.confirmed == True:
        session['email'] = user.email
        session['logged_in'] = True

        if activated_route == '/api/login':
          return jsonify(
            email=user.email,
            message="User logged in"
          )
        else:
          return redirect('/profile/'+ email)
      else:
        return jsonify(
            email=user.email,
            error="Invalid Password"
          )
    else:
      return jsonify(
            email=user.email,
            error="Please confirm user account"
          )
    
def get_geo_data(zip_code):
  """geo_data = json.loads(requests.get('http://api.geonames.org/postalCodeLookupJSON?postalcode=' + zip_code + '&country=US&username=ckearse').content)"""

  geo_data = {"postalcodes":[{"adminCode2":"045","adminCode1":"PA","adminName2":"Delaware","lng":-75.399118,"countryCode":"US","postalcode":"19063","adminName1":"Pennsylvania","placeName":"Media","lat":39.918804}]}

  city = geo_data["postalcodes"][0]["placeName"]
  county = geo_data["postalcodes"][0]["adminName2"]
  state = geo_data["postalcodes"][0]["adminCode1"]

  return {'city':city, 'county':county, 'state':state}

@app.route('/api/admin_dashboard')
@app.route('/admin_dashboard')
def admin_dashboard():
  users = User.query.all()
  return render_template('admin_dash.html', users=users)

@app.route('/api/logout')
@app.route('/logout')
#clear session, redirect to root
def logout():
  session.clear()
  return redirect('/')

if __name__ == "__main__":
  app.run()