# views.py
from . models import Post,User
from blog import blog,db,login_manager
from flask import render_template,flash,redirect,url_for,request
from flask_login import login_user,login_required,logout_user,current_user
from datetime import datetime
import mistune
from pytz import timezone
from dateutil import tz
from functools import wraps




@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

def login_required(role="any"):
	def wrapper(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
			if not current_user.is_authenticated:
				return login_manager.unauthorized()
			if ((current_user.urole != role) and (role != "any")):
				return login_manager.unauthorized()
			return fn(*args, **kwargs)
		return decorated_view
	return wrapper


#Landing page
@blog.route('/')
@blog.route('/login')
def login():
	return render_template('login.html')

@blog.route('/home/<int:page_num_index>')
@login_required(role='any')
def home(page_num_index):
	posts = Post.query.order_by(Post.date_posted.desc())
	posts=posts.paginate(per_page=5, page=page_num_index,error_out=True)
	return render_template('index.html',posts=posts)



#AboutUs
@blog.route('/aboutus')
def aboutus():
	return render_template('aboutus.html')


#Login Handler for Admin

@blog.route('/user_added',methods=['POST'])
def user_added():
	
	username = request.form['regusername']
	email = request.form['regemail']
	new_password = request.form['regpassword']
	urole = request.form['regrole']

	user_add = User(username=username,email=email,urole=urole)
	user_add.password=new_password
	db.session.add(user_add)
	db.session.commit()	


	return redirect(url_for('login'))

@blog.route('/logged_in',methods=['POST'])
def logged_in():
	error=""
	username = request.form['username']
	password = request.form['password']
	user = User.query.filter_by(username=username).first()
	if user is not None and user.verify_password(password):
		login_user(user)
		if user.get_urole()=='admin':
			return redirect(url_for('admin',page_num=1))
		else:
			return redirect(url_for('home',page_num_index=1))
	
	return redirect(url_for('login'))

#Admin page

@blog.route('/admin/<int:page_num>')
@login_required(role='admin')
def admin(page_num):
	search_true=True
	#current_username = current_user.username
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page_num,error_out=True)
	return render_template('admin.html',posts=posts)#,current_username=current_username)

@blog.route('/add_post')
@login_required(role='admin')
def add_post():
	return render_template('add_post.html')

@blog.route('/added',methods=['POST'])
@login_required(role='admin')
def added():
	
	author = request.form['name']
	title = request.form['title']
	temp = request.form['post']
	image_url = request.form['url']

	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()

	
	date_time = datetime.now()
	date_time = date_time.replace(tzinfo=from_zone)
	date_posted = date_time.astimezone(to_zone)

	#date_posted = date_temp.replace(tzinfo=timezone('UTC'))

	m = mistune.Markdown()
	post = m(temp)
	post_add = Post(author=author,title=title,post=post,image_url=image_url,date_posted=date_posted)
	db.session.add(post_add)
	db.session.commit()
	return redirect(url_for('admin',page_num=1))

@blog.route('/delete',methods=['POST'])
@login_required(role='admin')
def delete():
	post = Post.query.filter_by(title=request.form['delete']).first()
	if post is not None:
		db.session.delete(post)
		db.session.commit()
		flash("Post successfully Deleted")
		return redirect(url_for('admin',page_num=1))
	else:
		flash("No such Post available")
		return redirect(url_for('admin',page_num=1))

#Logout 

@blog.route('/logout')
@login_required(role='any')
def logout():
	logout_user()
	return redirect(url_for('login'))
