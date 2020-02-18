from flask import Flask
from flask_pymongo import PyMongo

# App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/pythonFlaskMMO"
mongo = PyMongo(app)

# Routes
@app.route('/')
def index():
    return '<h1>Page - Index</h1>'
