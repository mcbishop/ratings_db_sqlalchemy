"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.orm.exc import NoResultFound

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')


@app.route('/create_user', methods=['GET'])
def show_create_user_form():
    """Show user creation form."""
    
    return render_template("user_creation_form.html")


@app.route('/create_user', methods=['POST'])
def create_user():
    """Add new user to database from create user form."""
    
    username = request.form.get('login_email')
    password = request.form.get('password')    
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')
    print "======= USERNAME: %s, PASSWORD: %s, AGE: %s, ZIPCODE: %s" %(username, password, age, zipcode)

    user = User(email=username,
                password=password,
                age=age,
                zipcode=zipcode)
    db.session.add(user)
    db.session.commit()

    flash('Created new user. Please log in.')

    return redirect('/login')


@app.route('/login', methods=['GET'])
def show_login_form():
    """Show user login form."""
    return render_template('login_form.html')
    
@app.route('/login', methods=['POST'])
def login_user():
    """Process submission of login information.""" 
    username = request.form.get('login_email')
    password = request.form.get('password')
    print "======= USERNAME = %s, PASSWORD: %s =======" % (username, password)

    # Query for password by username
    try:
        (retrieve_password,
         user_id) = db.session.query(User.password, User.user_id).filter_by(email=username).one()
    except NoResultFound:
        # if user doesn't exist, flash unknown user message, and redirect to create user.
        # flash('Created new user.')
        # Check for presence of previous session. Return 0 if not found.
        print "========== DIDN'T FIND USER ======="
        counter = session.get('username_not_found', 0)
        counter += 1
        session['username_not_found'] = counter
        flash('Username not found. Try again.')
        # If user failed login 3 times, redirect to create user page.
        if counter >= 3:
            return redirect('/create_user')
        else:
            return redirect('/login')       

    if retrieve_password == password:
        # If username matches pw, log user in.
        flash('You were successfully logged in.')
        #to keep user logged in, add user ID to session. 
        session['user_id'] = user_id
        return redirect('/user_detail/%s' % (user_id))
    else:
        # If user login exists, but password is incorrect, flash message and reload page.
        flash ('Incorrect password. Try again.')
        return redirect('/login')


@app.route('/logout', methods=["GET"])
def show_logout_form():
    """Shows logout form."""

    return render_template("logout_form.html")


@app.route('/logout', methods=["POST"])
def logout_user():
    """Removes user session data to logout user."""
    
    session['user_id'] = None
    flash('You were successfully logged out.')
    return redirect('/')


@app.route('/movie_detail/<int:movie_id>', methods=["GET"])
def show_movie_detail(movie_id):
    """Shows movie details."""
    try:
        movie = Movie.query.filter_by(movie_id=movie_id).one()
    except NoResultFound:
        print "========== DIDN'T FIND MOVIE ======="
        flash('Movie not found.')
        # If user id not found, redirect to user list page.
        return redirect('/movies')          

    return render_template("movie_detail.html", movie=movie)


@app.route('/movies', methods=["GET"])
def show_movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/user_detail/<int:user_id>')
def show_user_detail(user_id):
    """Show user detail page."""

    try:
        user = User.query.filter_by(user_id=user_id).one()
    except NoResultFound:
        # if user doesn't exist, flash unknown user message, and redirect to create user.
        # flash('Created new user.')
        # Check for presence of previous session. Return 0 if not found.
        print "========== DIDN'T FIND USER ======="
        flash('Username not found.')
        # If user id not found, redirect to user list page.
        return redirect('/users')          

    return render_template("user_detail.html", user=user)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
