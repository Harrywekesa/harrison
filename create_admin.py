from app import app
from db import db
from models import User
from werkzeug.security import generate_password_hash

admin_email = 'harrisonwekesa09@gmail.com'
admin_password = '123'

with app.app_context():
    # Create an admin user
    hashed_password = generate_password_hash(admin_password)
    admin_user = User(username='admin', email=admin_email, password=hashed_password, is_admin=True)
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin user created with email: {admin_email}")
