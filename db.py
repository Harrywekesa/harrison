from app import db, User
from werkzeug.security import generate_password_hash

admin = User(username='harrison', email='harrisonwekesa09@gmail.com', password=generate_password_hash('harrison123'), is_admin=True)
db.session.add(admin)
db.session.commit()
