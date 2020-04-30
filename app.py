from flask import Flask, render_template, json, url_for, redirect, request, abort, flash, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_url, logout_user, login_user, current_user
from flask_pymongo import PyMongo, ObjectId
from flask_mail import Mail, Message
from passlib.hash import argon2
from datetime import datetime
import secrets
from bson.json_util import dumps

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

	def isTokenValid(createdAt):
		now = datetime.datetime.now()
		return (now - datetime.timedelta(hours=24) <= createdAt <= now)
		
	def authenticate(username:str, password:str):
		user = mongo.db.users.find_one({ "$or": [{"username": username},{"email": username}] })
		if user is not None and argon2.verify(password, user['password']):
			return User(user)
		return None

	def findById(_id:str):
		user = mongo.db.users.find_one({ "_id": ObjectId(_id) })
		return User(user)

	def findByUsername(username:str):
		user = mongo.db.users.find_one({ "username": username })
		if user is not None:
			user['followersCount'] = mongo.db.follow.count({ "followee": user['_id'], "end": None });
			user['followeesCount'] = mongo.db.follow.count({ "follower": user['_id'], "end": None });
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
	followees = []
	homeImg = []
	likes = []
	for res in mongo.db.follow.find({"follower": current_user._id, "end": None}, {"followee": 1}):
		followees.append(ObjectId(res["followee"]))
	for res2 in followees:
		for res3 in mongo.db.images.find({"user_id": res2}):
			homeImg.insert(0, res3)
	for res4 in mongo.db.likes.find({"user_id": current_user._id}):
		likes.append(res4)
	return render_template('pages/home.html', title="Accueil", homeImg=homeImg, likes=likes, nblikes=len(likes), user=current_user)

@app.route('/user/<string:username>')
def profile(username):
	user = User.findByUsername(username)
	if user is not None:
		isFollowed = mongo.db.follow.find_one({ "follower": current_user._id, "followee": user._id, "end": None })
		userImg = mongo.db.images.find({ "username": username }, { "image_name": 1, "_id": 0 })
		return render_template('pages/profile.html', title="Profile", user=user, userImg=userImg, isFollowed=isFollowed)
	return abort(404, "Désolé, cette instagrumeur n'existe pas")

@app.route('/addImage/<string:username>')
def addImage(username):
	user = User.findByUsername(username)
	return render_template('pages/addImage.html', title="addImage", user=user)

@app.route('/importImage', methods=["POST"])
def importImage():
	if "image" in request.files:
		image = request.files["image"]		
		if image.filename != "":
			mongo.save_file(image.filename, image)
			mongo.db.images.insert({"username": request.form.get("username"), "user_id": current_user._id, "image_name": image.filename, "date": datetime.now().strftime('%d/%m/%Y %H:%M:%S'), "title": request.form.get("image_title"), "description": request.form.get("image_description")})
	return redirect(url_for('profile', username=current_user.username))

@app.route('/importImageProfile', methods=["POST"])
def importImageProfile():
	if "image" in request.files:
		image = request.files["image"]		
		if image.filename != "":
			mongo.save_file(image.filename, image)
			mongo.db.users.update({"username": current_user.username}, {"$set": {"profile_image": image.filename}})
	return redirect(url_for('profile', username=current_user.username))

@app.route('/deleteImage/<filename>', methods=["POST"])
def deleteImage(filename):
	if filename != "":
		mongo.db.images.delete_one({"image_name": filename})
	return redirect(url_for('profile', username=current_user.username))

@app.route('/like/<file_id>', methods=["POST"])
def likeImage(file_id):
	if file_id != "":
		like = mongo.db.likes.find({"user_id": current_user._id, "file_id": file_id})
		if like.count() == 0:
			mongo.db.likes.insert({"user_id": current_user._id, "file_id": file_id})
		else :
			mongo.db.likes.delete_one({"user_id": current_user._id, "file_id": file_id})
	return redirect(url_for('home'))

@app.route('/file/<filename>')
def file(filename):
	return mongo.send_file(filename)

@app.route('/search', methods=['GET', 'POST'])
def search():
	if request.args.get('q') is not None:
		search = request.args.get('q')
		users = mongo.db.users.find({ "$or":[
			{"username": {"$regex": ".*"+search+".*", '$options' : 'i'}},
			{"firstname": {"$regex": ".*"+search+".*", '$options' : 'i'}},
			{"lastname": {"$regex": ".*"+search+".*", '$options' : 'i'}}
		]}, { "username": 1, "firstname": 1, "lastname": 1, "profile_image": 1 })
		return dumps(users)
	return render_template('pages/search.html')

@app.route('/post/<string:id>')
def post(id):
	full_img = []
	for res in mongo.db.images.find({ "image_name":id }):
		full_img.insert(0,res)
	return render_template('pages/post.html', title="post", image=id, full_img=full_img[0], user=current_user)

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
					"password": argon2.hash(password),
					"profile_image": "",
					"isAdmin": False
				})
				return redirect(url_for('login'))
		return render_template('pages/inscription.html', title="inscription")
	return redirect(url_for('home'))

@app.route('/api/feed', methods=['GET'])
def apiFeed():
	if request.args.get('offset') is not None:
		offset = int(request.args.get('offset'))
		images = mongo.db.images.find().limit(6).skip(offset)
		return dumps(images)
	return abort(500, 'Missing offset param')

@app.route('/follow', methods=['POST'])
def apiFollowUser():
	if request.is_json:
		data = request.get_json();
		user = mongo.db.users.find_one({ "username": data['user'] })
		if user is not None:
			mongo.db.follow.insert_one({
				"follower": current_user._id,
				"followee": user['_id'],
				"start": datetime.now()
			})
			return dumps({ 'code': 200, 'status': 'success' })
	return dumps({ 'code': 200, 'status': 'error' })

@app.route('/unfollow', methods=['POST'])
def apiUnfollowUser():
	if request.is_json:
		data = request.get_json();
		user = mongo.db.users.find_one({ "username": data['user'] })
		if user is not None:
			mongo.db.follow.update_one({"follower": current_user._id, "followee": user['_id'], "end": None}, { "$set": {"end": datetime.now() }})
			return dumps({ 'code': 200, 'status': 'success' })
	return dumps({ 'code': 200, 'status': 'error' })


# ---------------------- #
# --- Error Handling --- #
# ---------------------- #

@app.errorhandler(404)
def http404(error):
	return render_template('404.html', error=error)

@app.errorhandler(500)
def http500(error):
	return render_template('500.html', error=error)
