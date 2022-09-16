import os
from aws_uploads import allowed_file, upload_file
from dotenv import load_dotenv

from flask import Flask, g, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
# import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies, unset_jwt_cookies

from models import db, connect_db, User, Message, Match, DEFAULT_IMAGE

load_dotenv()


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
# Switch to true for redirects
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
# app.config["JWT_COOKIE_SECURE"] = False
# app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

toolbar = DebugToolbarExtension(app)
jwt = JWTManager(app)

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
    zip_code = request.form["zip_code"]
    bio = request.form["bio"]
    hobbies = request.form["hobbies"]
    interests = request.form["interests"]
    radius = request.form["radius"]

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
            first_name=first_name,
            password=password,
            age=age,
            zip_code=zip_code,
            bio=bio,
            hobbies=hobbies,
            interests=interests,
            radius=radius,
            image=image_url
        )
        db.session.commit()
        # encoded_jwt = jwt.encode({"username": f"{new_user.username}"}, os.environ['SECRET_KEY'], algorithm="HS256")
        # return (jsonify(token = encoded_jwt), 201)


    except IntegrityError:
        return (jsonify(msg="Username already exists."), 400)


    # access_token = create_access_token(identity = new_user.serialize())
    # set_access_cookies(response, access_token)
    serialized = new_user.serialize()
    access_token = create_access_token(identity=serialized)
    return (jsonify(access_token = access_token), 201)



@app.post("/login")
def login():
    """Handle user login"""

    username = request.json["username"]
    password = request.json["password"]

    user = User.authenticate(username, password)

    if user:
        # response = jsonify({"msg": "login successful"})
        access_token = create_access_token(identity = user.serialize())
        # set_access_cookies(response, access_token)
        return (jsonify(access_token = access_token), 201)
    else:
        return (jsonify(error="Incorrect username/password"), 401)

@app.get(“/profile”)
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    current_username = current_user.get(‘username’)
    user = User.query.filter(User.username == current_username).first()
    serialized = user.serialize()
    return (jsonify(user = serialized), 201)
    
@app.patch("/update")
@jwt_required()
def update():
    token_user = get_jwt_identity()
    token_username = token_user.get('username')
    user = User.query.get_or_404(token_username)

    if token_user:
        # username = request.form["username"]
        first_name = request.form["first_name"]
        # QUESTION: don't need password/username because user shouldn't update those?
        # password = request.form["password"]
        age = request.form["age"]
        zip_code = request.form["zip_code"]
        bio = request.form["bio"]
        hobbies = request.form["hobbies"]
        interests = request.form["interests"]
        radius = request.form["radius"]

    # user = User.authenticate(username, password)
    # # if ValueError => "incorrect login"
    # if not user:
    #     return (jsonify(error="Incorrect username/password"), 401)

        file = request.files["image"]

        S3_BUCKET = os.environ.get('S3_BUCKET')
        S3_LOCATION = os.environ.get('S3_LOCATION')
        name = f"{token_username}-prof-pic"

        image_url = DEFAULT_IMAGE

        if file and allowed_file(file.filename):
            upload_file(file, S3_BUCKET, name)
            image_url = f"https://{S3_BUCKET}.s3.{S3_LOCATION}.amazonaws.com/{name}"

        print(user.username)
        try:
            # user.username= token_username
            user.first_name = first_name or token_user.get("first_name")
            # user.password = token_user.get("password")
            user.age = age or token_user.get("age")
            user.zip_code = zip_code or token_user.get("zip_code")
            user.bio = bio or token_user.get("bio")
            user.hobbies = hobbies or token_user.get("hobbies")
            user.interests = interests or token_user.get("interests")
            user.radius = radius or token_user.get("radius")
            user.image = image_url or token_user.get("image_url")

            db.session.commit()

        except IntegrityError:
            # possibly catch other errors?
            return "info could not be updated"

        serialized = user.serialize()
        return (jsonify(user = serialized), 200)

############################################################
# show potential matches (unseen)


@app.get("/potentials")
@jwt_required()
def potentials():
    current_user = get_jwt_identity()
    current_username = current_user.get('username')
    all_users = User.query.all()

    unseen = {}
    for user in all_users:
        # TODO:don't add seen users
        if user.username != current_username:
            unseen[user.username] = user.serialize()


    return (jsonify(unseen=unseen), 201)

# Match with potentials


@app.post("/like")
@jwt_required()
def like():

    # return (jsonify(new_match = []), 201)
    current_user = get_jwt_identity()
    current_username = current_user.get('username')

    liked_username = request.json["liked_username"]
    is_like = request.json["is_like"]
    is_reject = request.json["is_reject"]

    # check if row exists with current user in user2col
    # TODO: try/except with integrity error if current user already liked user2
    exists = db.session.query(
        db.session.query(Match)
        .filter(
            Match.user1 == liked_username,
            Match.user2 == current_username
        )
        .exists()
    ).scalar()

    print("exists user1", exists)
    new_match = None
    # check if current_user has already been liked or rejected by liked_username
    if exists:
        # TODO: make a better variable name
        is_user_2_matched_to_user_1 = Match.query.filter(
            Match.user1 == liked_username,
            Match.user2 == current_username
        ).first()

        if is_like and not is_user_2_matched_to_user_1.is_rejected:
            is_user_2_matched_to_user_1.is_matched = True
        else:
            is_user_2_matched_to_user_1.is_rejected = True
        new_match = is_user_2_matched_to_user_1
    else:
        new_match = Match(user1=current_username, user2=liked_username)
        if is_reject:
            new_match.is_rejected = True

        db.session.add(new_match)

    db.session.commit()

    serialized = new_match.serialize()

    return (jsonify(new_match = serialized), 201)
