import os
from aws_uploads import upload_file
from dotenv import load_dotenv

from flask import Flask, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, CSFROnly
from models import db, connect_db, User, Message, Match, bcrypt, session

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False #Switch to true for redirects
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global.
    Adds global csfr_form"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        g.csrf_form = CSFROnly()

    else:
        g.user = None



def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.post("/signup")
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                age=form.age.data,
                zip_code=form.zip_code.data,
                bio=form.bio.data,
                hobbies=form.hobbies.data,
                interests=form.interests.data,
                radius=form.radius.data
            )
            db.session.commit()

        except IntegrityError:
            return jsonify(error = "invalid inputs")


@app.patch("/update")
def update():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    file = request.files("image")


    if form.validate_on_submit():
        g.user.username=form.username.data,
        g.user.password=form.password.data,
        g.user.age=form.age.data,
        g.user.zip_code=form.zip_code.data,
        g.user.bio=form.bio.data,
        g.user.hobbies=form.hobbies.data,
        g.user.interests=form.interests.data,
        g.user.radius=form.radius.data
        if file:
            upload_file(file, S3_BUCKET, file.filename)
            g.user.image


    db.session.commit()