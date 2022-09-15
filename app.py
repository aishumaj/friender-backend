from http.client import UNAUTHORIZED
import os
from aws_uploads import allowed_file, upload_file
from dotenv import load_dotenv

from flask import Flask, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Message, Match, DEFAULT_IMAGE

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False #Switch to true for redirects
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.drop_all()
db.create_all()

##############################################################################
# User signup/login/logout

@app.post("/signup")
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect JSON of new user.
    """

    username = request.form["username"]
    first_name = request.form["first_name"]
    password = request.form["password"]
    age = request.form["age"]
    zip_code= request.form["zip_code"]
    bio= request.form["bio"]
    hobbies = request.form["hobbies"]
    interests = request.form["interests"]
    radius= request.form["radius"]

    print("username and pw", username, password)

    file = request.files["image"]
    print("file: ", file)

    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_LOCATION = os.environ.get('S3_LOCATION')
    name = f"{username}-prof-pic"

    image_url = DEFAULT_IMAGE

    if file and allowed_file(file.filename):
        upload_file(file, S3_BUCKET, name)
        image_url = f"https://{S3_BUCKET}.s3.{S3_LOCATION}.amazonaws.com/{name}"

    try:
        new_user = User.signup(
            username=username,
            first_name = first_name,
            password = password,
            age = age,
            zip_code = zip_code,
            bio = bio,
            hobbies = hobbies,
            interests = interests,
            radius=radius,
            image=image_url
        )

        db.session.commit()

    except IntegrityError:
        return "Username already exists."

    serialized = new_user.serialize()
    return (jsonify(user=serialized), 201)

@app.post("/login")
def login():
    """Handle user login"""

    username = request.json["username"]
    password = request.json["password"]

    user = User.authenticate(username, password)

    if user:
        serialized = user.serialize()
        return (jsonify(user=serialized), 201)
    else:
        return (jsonify(error="Incorrect username/password"), 401)

@app.patch("/update")
def update():
    username = request.form["username"]
    first_name = request.form["first_name"]
    password = request.form["password"]
    age = request.form["age"]
    zip_code= request.form["zip_code"]
    bio= request.form["bio"]
    hobbies = request.form["hobbies"]
    interests = request.form["interests"]
    radius= request.form["radius"]


    user = User.authenticate(username, password)
    # if ValueError => "incorrect login"
    if not user:
        return (jsonify(error="Incorrect username/password"), 401)

    file = request.files["image"]

    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_LOCATION = os.environ.get('S3_LOCATION')
    name = f"{username}-prof-pic"

    image_url = DEFAULT_IMAGE

    if file and allowed_file(file.filename):
        upload_file(file, S3_BUCKET, name)
        image_url = f"https://{S3_BUCKET}.s3.{S3_LOCATION}.amazonaws.com/{name}"


    try:
        user.username= user.username
        user.first_name = first_name or user.first_name
        user.password = user.password
        user.age = age or user.age
        user.zip_code = zip_code or user.zipcode
        user.bio = bio or user.bio
        user.hobbies = hobbies or user.hobbies
        user.interests = interests or user.intersts
        user.radius = radius or user.radius
        user.image = image_url or user.image_url

        db.session.commit()

    except IntegrityError:
        # possibly catch other errors?
        return "info could not be updated"

    serialized = user.serialize()
    return (jsonify(user=serialized), 201)

############################################################
# Show all matches

# show potential matches (unseen)
@app.get("/potentials")
def potentials():
    # query all -
    # find user1 = user.username
    # => ids = Match.query.filter(user1=self)
    # and don't show users in user2Col where match/ rejection = F
    User.potential


# Show User Profile


