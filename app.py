from flask import Flask, render_template, json, url_for, redirect, request, abort, flash
from flask_login import LoginManager, UserMixin, login_required, login_url, logout_user, login_user, current_user
from flask_pymongo import PyMongo, ObjectId
from flask_mail import Mail, Message
from passlib.hash import argon2
from datetime import datetime
import secrets

# App
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/instagrum"
app.secret_key = b'"<Q\n]\xe6\x03rp\x95\xc8\xa4\xf0\xcb\xd4e'

mongo = PyMongo(app)
mail = Mail(app)

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

	def isTokenValid(createdAt):
		now = datetime.datetime.now()
		return (now - datetime.timedelta(hours=24) <= createdAt <= now)

	def findByUsername(username:str):
		user = mongo.db.users.find_one({ "username": username })
		if user is not None:
			return User(user)
		else:
			return None

	def authenticate(username:str, password:str):
		user = mongo.db.users.find_one({ "$or": [{"username": username},{"email": username}] })
		if user is not None and argon2.verify(password, user['password']):
			return User(user)
		return None
		


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
@login_required
def home():
	return render_template('pages/home.html', title="Accueil")


@app.route('/user/<string:username>')
def profile(username):
	userImg= []
	for res in mongo.db.images.find({'username': username}, {'profile_image_name': 1, '_id': 0}):
		userImg.append(res)
	user = User.findByUsername(username)
	if user is not None:
		return render_template('pages/profile.html', title="Profile", user=user, userImg=userImg)
	else:
		return abort(404, "Désolé, cette instagrumeur n'existe pas")


@app.route('/addImage/<string:username>')
def addImage(username):
	user = User.findByUsername(username)
	return render_template('pages/addImage.html', title="addImage", user=user)

@app.route('/importImage', methods=["POST"])
def importImage():
	if "profile_image" in request.files:
		profile_image = request.files["profile_image"]		
		if profile_image.filename != "":
			mongo.save_file(profile_image.filename, profile_image)
			mongo.db.images.insert({"username": request.form.get("username"), "profile_image_name": profile_image.filename, "date": datetime.now().strftime('%d/%m/%Y %H:%M:%S')})
	return redirect(url_for('home'))

@app.route('/file/<filename>')
def file(filename):
	return mongo.send_file(filename)


@app.route('/post/<string:id>')
def post(id):
	return render_template('pages/post.html', title="post", image=id)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if not current_user.is_authenticated:
		if request.method == "POST":
			username = request.form.get('login[username]')
			password = request.form.get('login[password]')
			user = User.authenticate(username, password)
			if (user is not None):
				login_user(user)
				return redirect(url_for('home'))
			else:
				flash('Identifiant ou mot de passe non valide', 'login-form--error')
		
		return render_template('pages/login.html', title="login")
	else:
		return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgotPassword():
	if not current_user.is_authenticated:
		if request.method == "POST" and request.form.get('email'):
			email = request.form.get('email');
			user = mongo.db.users.find_one({ "email": email })
			
			if user is not None:
				token = secrets.token_hex(25)
				mongo.db.users.update({ "email": email }, {
					"$set": {
						"recovery_token": token,
						"recovery_token_created_at": datetime.datetime.now()
					}
				})
				
				msg = Message("Réinitialisation de votre mot de passe", sender="no-reply@instagrum.com", recipients=[email])
				msg.html = render_template('mails/password-recovery.html', user=user, token=token)
				mail.send(msg)

			flash('Si ce compte existe, vous allez recevoir un email afin de réinitialiser votre mot de passe', 'password-recovery')
		return render_template('pages/forgot-password.html')
	else:
		return redirect(url_for('home'))

@app.route('/forgot-password/<string:token>', methods=['GET', 'POST'])
def resetPassword(token):
	if not current_user.is_authenticated:
		user = mongo.db.users.find_one({ "recovery_token": token })
		tokenIsValid = True;
		if user is not None and User.isTokenValid(user['recovery_token_created_at']):
			if request.method == "POST":
				password = request.form.get('password');
				if password == request.form.get('password_confirm'):
					mongo.db.users.update({ "recovery_token": token }, {
						"$set": {
							"password": argon2.hash(password),
							"recovery_token": None,
							"recovery_token_created_at": None,
						}
					})
					return redirect(url_for('login'))
				else:
					flash('Les mots de passes ne sont pas identique', 'password-reset-error')
		else:
			tokenIsValid = False;
			flash('Token invalide ou expiré', 'password-reset-error')
		return render_template('pages/forgot-password.html', hasToken=True, tokenIsValid=tokenIsValid)
	else:
		return redirect(url_for('home'))


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
	if not current_user.is_authenticated:
		if request.method == "POST":
			firstName = request.form.get('inscription[firstName]')
			lastName = request.form.get('inscription[lastName]')
			userName = request.form.get('inscription[userName]')
			mail = request.form.get('inscription[mail]')
			password = request.form.get('inscription[password]')

			for res in mongo.db.users.find( {"$or": [ {"username": userName}, {"email": mail} ] }):
				if res is not None: 
					flash("Nom d'utilisateur et / ou mail déjà utilisé", 'signup-form--error')
					return render_template('pages/inscription.html', title="inscription")

			if firstName == "":
				flash('Vous devez renseignez votre prénom', 'signup-form--error')
			
			if lastName == "":
				flash('Vous devez renseignez votre nom', 'signup-form--error')

			if userName == "":
				flash('Vous devez renseignez un nom d\'utilsateur', 'signup-form--error')

			if mail == "":
				flash('Vous devez renseignez une adresse email', 'signup-form--error')

			if password == "":
				flash('Vous devez renseignez un mot de passe', 'signup-form--error')

			if firstName != "" and lastName != "" and userName != "" and mail != "" and password != "" :
				mongo.db.users.insert_one({
					"firstname": firstName,
					"lastname": lastName,
					"username": userName,
					"email": mail,
					"password": argon2.hash(password)				
				})
				return redirect(url_for('login'))
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