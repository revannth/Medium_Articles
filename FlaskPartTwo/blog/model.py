# models.py

from blog import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

class User(UserMixin,db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	urole = db.Column(db.String(80),index=True)
	password_hash = db.Column(db.String(128))
	

	@property
	def password(self):
		raise AttributeError('password is not a readable entity')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)


	def __repr__(self):
		return '<User %r>'%(self.username)

	def get_id(self):
		return self.id
	def get_username(self):
		return self.username
	def get_urole(self):
		return self.urole