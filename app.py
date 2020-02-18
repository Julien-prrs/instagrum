from flask import Flask, render_template
from flask_pymongo import PyMongo

# App
app = Flask(__name__, static_folder="static", template_folder="templates");
app.config["MONGO_URI"] = "mongodb://localhost:27017/flaskInstagram";
mongo = PyMongo(app);

# Routes
@app.route('/')
def home():
    users = mongo.db.users.find();
    return render_template('layouts/home.html', title="Accueil", users=users);