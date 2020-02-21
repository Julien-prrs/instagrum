from flask import Flask, render_template, json, url_for, redirect, request, abort
from flask_login import LoginManager, UserMixin, login_required, login_url, logout_user, login_user, current_user
from flask_pymongo import PyMongo, ObjectId

# App
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/instagrum";
app.secret_key = b'"<Q\n]\xe6\x03rp\x95\xc8\xa4\xf0\xcb\xd4e'

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# Class
class User(UserMixin):
	def __init__(self, user):
		for key in user:
			setattr(self, key, user[key])

	def get_id(self):
		return str(self._id)

	def findById(_id:str):
		user = mongo.db.users.find_one({ "_id": ObjectId(_id) })
		return User(user)

	def findByUsername(username:str):
		user = mongo.db.users.find_one({ "username": username })
		if user is not None:
			return User(user)
		else:
			return None

	def authenticate(username:str, password:str):
		user = mongo.db.users.find_one({ "$or": [{"username": username},{"email": username}], "password": password })
		if user is not None:
			user = User(user)
		return user
		


# --------------------- #
# --- Login manager --- #
# --------------------- #

@login_manager.user_loader
def load_user(user_id:str):
	return User.findById(user_id)



# --------------------- #
# --- Views context --- #
# --------------------- #

@app.context_processor
def manage_assets():
	return dict(assets=json.load(open('./static/manifest.json')))



# -------------- #
# --- Routes --- #
# -------------- #

@app.route('/')
def home():
	users = mongo.db.users.find();
	return render_template('pages/home.html', title="Accueil", users=users)


@app.route('/user/<string:username>')
def profile(username):
    user = User.findByUsername(username);
    if user is not None:
        return render_template('pages/profile.html', title="Profile", user=user)
    else:
        return abort(404, "Désolé, cette instagrumeur n'existe pas")


@app.route('/post/<string:id>')
def post(id):
	return render_template('pages/post.html', title="post")


@app.route('/login', methods=['GET', 'POST'])
def login():
	if not current_user.is_authenticated:
		if request.form is not None:
			username = request.form.get('login[username]')
			password = request.form.get('login[password]')
			user = User.authenticate(username, password)

			if (user is not None):
				login_user(user)
				return redirect(url_for('home'));
		
		return render_template('pages/login.html', title="login")
	else:
		return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()

	if request.form is not None:
		firstName = request.form.get('inscription[firstName]')
		lastName = request.form.get('inscription[lastName]')
		userName = request.form.get('inscription[userName]')
		mail = request.form.get('inscription[mail]')
		password = request.form.get('inscription[password]')
		if firstName != "" and lastName != "" and userName != "" and mail != "" and password != "" :
			print(firstName)		
			print(lastName)		
			print(userName)		
			print(mail)		
			print(password)		
		return render_template('pages/inscription.html', title="inscription")

	return redirect(url_for('home'))


# ---------------------- #
# --- Error Handling --- #
# ---------------------- #

@app.errorhandler(404)
def http404(error):
	return render_template('404.html', error=error)

@app.errorhandler(500)
def http500(error):
    return render_template('500.html', error=error)