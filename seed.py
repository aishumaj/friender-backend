
from app import db
from models import User, Match

db.drop_all()
db.create_all()


user1 = User(
    username = "user1",
    first_name = "user1",
    password = "password",
    age = 20,
    zip_code = "12345,
    ")