from flask import Flask, render_template, json, url_for
from flask_pymongo import PyMongo

# App
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/instagrum";
mongo = PyMongo(app);


# Views context
@app.context_processor
def manage_assets():
    return dict(assets=json.load(open('./static/manifest.json')))


# Routes
@app.route('/')
def home():
    users = mongo.db.users.find();
    return render_template('pages/home.html', title="Accueil", users=users)