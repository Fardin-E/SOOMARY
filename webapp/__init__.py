# Import the required libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, UserMixin
from sqlalchemy.sql import func

# Initializing database and naming it
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    # Initialize the web application
    app = Flask(__name__)

    # Encrypt cookies and session data
    app.config['SECRET_KEY'] = 'thesupersecretkey'

    # Informing the server where the database is located
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Initalizing database and using flask application as parameter
    db.init_app(app)

    # Import the blueprints for the pages
    from .pages import pages
    app.register_blueprint(pages, url_prefix='/')

    # Call to the create database function
    create_database(app)

    # If the user is not logged in, then display the Login page
    login_manager = LoginManager()
    login_manager.login_view = 'pages.login'
    login_manager.init_app(app)

    # Load the user using their id (primary key)
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app

# Database table for the summary data, connected to the user table (one to many relationship)
class Summ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(5000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Database table for the user data
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    summs = db.relationship('Summ')

def create_database(app):
    # If the database does not exist, create the database
    if not path.exists('webapp/' + DB_NAME):
        db.create_all(app=app)