from app import app
from db import db
from models import User, Course, Resource

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Recreate all tables
    db.create_all()
    print("Database cleared and tables recreated.")
