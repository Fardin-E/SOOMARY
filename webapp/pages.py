# Import the required libraries
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, Summ, User
import json
from newspaper import Article

# Blueprints to define the URLs
pages = Blueprint('pages', __name__)

# Defining the URL for Home page
@pages.route('/', methods=['GET', 'POST'])

# Requires users to be logged in to access the page
@login_required
def home():

    # If the method is POST, then get the URL from the form
    if request.method == 'POST':
        URL = request.form.get('url')

        # If the user inputs no value for URL, then send an error flash
        if len(URL) < 1:
            flash('Must enter URL!', category='error')
        else:
            # Otherwise, using the URL, get the article
            article=Article(URL)

            # Download, parse and process the article
            article.download()
            article.parse()
            article.nlp()

            # Convert to string and remove the unnecessary punctuation 
            aString = str(article.authors)
            a1 = aString.replace('[','')
            a2 = a1.replace(']','')
            author = a2.replace("'","")

            # Assign the article title, author and summary into one string
            summ = article.title + ", " + author + ". " + article.summary

            # Store the string into the database, depending the the current user
            new_summ = Summ(data=summ, user_id = current_user.id)
            db.session.add(new_summ)
            db.session.commit()

    # Display the Home page to the current user
    return render_template("home.html", user=current_user)

# Define the URL for about page
@pages.route('/about')
def about():

    # Display the About page to the current user
    return render_template('about.html', user=current_user)

# Define the URL for Deleting summary
@pages.route('/delete-summ', methods=['POST'])
def delete_summ():

    # Retrieve the summary ID from the database and deletes it
    summ = json.loads(request.data)
    summId = summ['summId']
    summ = Summ.query.get(summId)
    if summ:
        if summ.user_id == current_user.id:
            db.session.delete(summ)
            db.session.commit()
    return jsonify({})

# Define the URL for Login page
@pages.route('/login', methods=['GET', 'POST'])
def login():

    # If the method is POST, then get the email and password from the form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Filter through users using email
        user = User.query.filter_by(email=email).first()

        # If the user exists, then check their password
        if user:

            # If the password is correct, login the user and display a valid "logged in" flash
            if check_password_hash(user.password, password):
                flash('Logged in!', category='valid')

                # Remember the user using cookies
                login_user(user, remember=True)

                # Redirect the user to the Home page
                return redirect('/')

            # Otherwise if the password is incorrect, flash and error message with a "incorrect password"
            else:
                flash('Incorrect password!', category='error')
        
        # If the email does not exist, then display an error "user does not exist" flash
        else:
            flash('User does not exist.', category='error')

    # Display the Login page to the current user
    return render_template("login.html", user=current_user)

# Define the URL for Logout page
@pages.route('/logout')

# Requires users to be logged in to access the page
@login_required
def logout():

    # Logout the user and display the Login page
    logout_user()
    return redirect(url_for('pages.login'))

# Define the URL for Sign up page
@pages.route('/sign-up', methods=['GET', 'POST'])
def sign_up():

    # If the method is POST, then get the email and password from the form
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')

        # Filter through users using email
        user = User.query.filter_by(email=email).first()

        # If the email is already in the database, then display an error "email already exists" flash
        if user:
            flash('Email already exists.', category='error')

        # If the user does not enter an email, then display an error flash
        elif len(email) < 1:
            flash('Must enter email.', category='error')

        # If the length of the length of the password entered is not longer than 7, then display an error flash
        elif len(password1) < 7:
            flash('Password must be longer than 7 characters.', category='error')
            
        else:
            # Otherwise, add the user to the database and encrypt their password
            new_user = User(email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            # Remember the user using cookies
            login_user(new_user, remember=True)

            # Display a valid flash with the message "account created"
            flash('Account created!', category='valid')

            # Once the user has signed up, redirect them to the Home page
            return redirect('/')

    # Continue to display the Sign up page if the user is unable to sign up successfully
    return render_template("sign_up.html", user=current_user)