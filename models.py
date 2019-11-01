from server import db

#abstact to models.py
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(80), unique=True)
  password = db.Column(db.String(120), unique=False)

  first_name = db.Column(db.String(120), unique=False)
  middle_name = db.Column(db.String(120), unique=False)
  last_name = db.Column(db.String(120), unique=False)
  zip_code = db.Column(db.String(120), unique=False)

  city = db.Column(db.String(120), unique=False)
  county = db.Column(db.String(120), unique=False)
  state = db.Column(db.String(120), unique=False)

  def __init__(self, email, password):
    self.email = email
    self.password = password

  def __repr__(self):
    return '<User %r>' % self.email
