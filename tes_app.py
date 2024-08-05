import unittest
from app import app, db
from models import User, Course, Resource

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

        # Create a test user
        self.user = User(username='testuser', email='testuser@example.com', password='password', is_admin=True)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to My Website', response.data)

    def test_login_page(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_register_page(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_admin_dashboard_access(self):
        with self.app:
            self.app.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=True)
            response = self.app.get('/admin/dashboard')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Admin Dashboard', response.data)

    def test_add_course(self):
        with self.app:
            self.app.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=True)
            response = self.app.post('/admin/add_course', data=dict(
                title='Test Course',
                description='This is a test course.',
                level='6',
                category='ICT'
            ), follow_redirects=True)
            self.assertIn(b'Course added successfully!', response.data)

    def test_add_resource(self):
        with self.app:
            self.app.post('/login', data=dict(email='testuser@example.com', password='password'), follow_redirects=True)
            self.app.post('/admin/add_course', data=dict(
                title='Test Course',
                description='This is a test course.',
                level='6',
                category='ICT'
            ), follow_redirects=True)
            course = Course.query.first()
            with open('test_file.txt', 'w') as f:
                f.write('This is a test file.')
            with open('test_file.txt', 'rb') as f:
                response = self.app.post('/admin/add_resource', data=dict(
                    title='Test Resource',
                    description='This is a test resource.',
                    course_id=course.id,
                    is_free=True,
                    file=f,
                    price=0.0
                ), follow_redirects=True)
            self.assertIn(b'Resource added successfully!', response.data)

if __name__ == '__main__':
    unittest.main()
