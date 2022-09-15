"""SQLAlchemy models for Friender."""

from datetime import datetime
from distutils.log import debug

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE = "/img/default-pic.png"

class Match(db.Model):
    """Connection between two users"""

    __tablename__ = "matches"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user1 = db.Column(
        db.Text,
        db.ForeignKey('users.username')
    )

    user2 = db.Column(
        db.Text,
        db.ForeignKey('users.username')
    )

    is_matched = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_rejected = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

class User(db.Model):
    """User in the system"""

    __tablename__ = "users"

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
        primary_key=True
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    age = db.Column(
        db.Integer,
        nullable=False,
    )

    zip_code = db.Column(
        db.Text,
        nullable=False,
    )

    image = db.Column(
        db.Text,
        default = DEFAULT_IMAGE
    )

    bio = db.Column(
        db.Text,
        nullable=False,
    )

    hobbies = db.Column(
        db.Text,
        nullable=False,
    )

    interests = db.Column(
        db.Text,
        nullable=False,
    )

    radius = db.Column(
        db.Integer,
        nullable=False
    )

    matches = db.relationship(
        "User",
        secondary="matches",
        primaryjoin= (Match.user1 == username),
        secondaryjoin= (Match.user2 == username),
        backref="seen")

    # messages = db.relationship("Message", backref="user")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.first_name}>"

    def serialize(self):
        """Serialize to dictionary"""

        return {
            "username": self.username,
            "firstname": self.first_name,
            "age": self.age,
            "zipcode": self.zip_code,
            "bio": self.bio,
            "hobbies": self.hobbies,
            "interests": self.interests
        }

    @classmethod
    def signup(cls, username, first_name, password, age, zip_code, bio, hobbies, interests, radius, image):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name = first_name,
            password = hashed_pwd,
            age = age,
            zip_code = zip_code,
            bio = bio,
            hobbies = hobbies,
            interests = interests,
            radius=radius,
            image=image
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            print("is_auth:", is_auth)

            if is_auth:
                return user

        return False

    def potential(self):
        # SELECT * FROM users
        # if self == user1  in matches don't show that row
        users = User.query.all()
        


    # def seen_by_one_user


class Message(db.Model):
    """Messages between matches"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(500),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    sender = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete="cascade")
    )

    recipient = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete="cascade")
    )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)





