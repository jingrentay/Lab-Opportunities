import warnings

from wtforms import fields
warnings.filterwarnings("ignore")
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.Model.models import User, Student, Faculty, Application, Post, Major, Field
from config import Config
import datetime
from project import create_user1, create_user2, init_majors_and_fields

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ROOT_PATH = '..//'+basedir

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

# TEST: USER (FACULTY & STUDENT)

    def test_password_hashing(self): # TEST INITIATIVE: Passwords are being saved correctly
        u1 = User(username = 'test', wsu_id = '111111111', email='testy.tester@wsu.edu', user_type = 'Student')
        u2 = User(username = 'test2', wsu_id = '222222222', email='testy2.tester@wsu.edu', user_type = 'Faculty')
        u1.set_password('abc')
        u2.set_password('123')

        self.assertFalse(u1.check_password('123'))
        self.assertTrue(u1.check_password('abc'))

        self.assertFalse(u2.check_password('abc'))
        self.assertTrue(u2.check_password('123'))


    #Tests whether has the student has actually applied to a post after sending the application
    def test_has_applied(self):
        f1 = create_user1('Faculty', 'andy', 'aofallon@wsy.edu', 'abc', '444444444')
        db.session.add(f1)
        p1 = Post(user_id =f1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(Post.query.all()[0].id, p1.id)
        u2 = Student(username='Tay', wsu_id = '111127598', email ='jingren.tay@wsu.edu', user_type = 'Student')
        u2.set_password('abc')
        db.session.add(u2)
        db.session.commit()
        u2.apply(p1,'Hi','Bob')
        db.session.commit()
        self.assertEqual(u2.has_applied(p1), True)

        
        p2 = Post(user_id =f1.id, title='My post', body='This is my 2nd test post.', time_commitment = '100', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p2)
        db.session.commit()
        self.assertEqual(Post.query.all()[1].id, p2.id)
        db.session.commit()
        self.assertEqual(u2.has_applied(p2), False)
        
        
    def test_get_user_posts(self):
        init_majors_and_fields()
        f1 = create_user1('Faculty', 'sakire', 'sakire@wsu.edu', 'abc', '55555555')
        db.session.add(f1)
        _majors = Major.query.slice(0,2) # Gets first two majors in list (TODO: if you can find a better way of sorts majors please change)
        fields = _majors.first().fields
        faculty_user = User.query.filter_by(username = 'sakire').first()
        p1 = Post(user_id = faculty_user.id, title= 'Database Integrity', 
            body = 'We are looking for 3-4 year undergrad students who enjoy working in the fields of networking and cybersecurity. We are teaming up with Amazon to make penetration software that will test the integrity of their AWS systems. You do not need to be an expert on databases nor security, but it would be very helpful.', 
            majors = _majors,
            fields = fields,
            time_commitment = '25',
            start_date = datetime.datetime(2022, 1, 10),
            end_date = datetime.datetime(2022, 5, 21)
            )
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(f1.get_user_posts().all(), [p1])


    #Tests both student and faculty are displaying the correct status before and after reviewing
    def test_get_status(self):
        u1 = Faculty(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Faculty')
        u1.set_password('123')
        db.session.add(u1)
        db.session.commit()
        p1 = Post(user_id = u1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        u2 = Student(username='Tay', wsu_id = '111127598', email ='jingren.tay@wsu.edu', user_type = 'Student')
        u2.set_password('abc')
        db.session.add(u2)
        db.session.commit()
        u2.apply(p1,'Hi','Bob')
        db.session.commit()
        self.assertEqual(u2.get_status(p1), 'Pending')

    def test_get_status_application(self):
        u1 = Faculty(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Faculty')
        u1.set_password('123')
        db.session.add(u1)
        db.session.commit()
        p1 = Post(user_id = u1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        u2 = Student(username='Tay', wsu_id = '111127598', email ='jingren.tay@wsu.edu', user_type = 'Student')
        u2.set_password('abc')
        db.session.add(u2)
        db.session.commit()
        u2.apply(p1,'Hi','Bob')
        db.session.commit()
        self.assertEqual(Application.query.all()[0].status, 'Pending')
        

    #Tests both student and faculty have correct user type registered into the database
    def test_get_user_type(self):
        u1 = Student(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Student')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.get_user_type(), 'Student')

        u2 = Faculty(username='test2', wsu_id = '111111117', email='testy2.tester@wsu.com', user_type = 'Faculty')
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u2.get_user_type(), 'Faculty')

    def test_get_major(self):
        init_majors_and_fields()
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)
        db.session.commit()
        self.assertEqual(s1.get_major(), 'Computer Science')


    #test the function can_apply where student should not be able to apply if there is no wsu id in the profile
    def test_can_apply_student(self):
        u1 = Student(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Student')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.can_apply(), True)

        u2 = Student(username='tay', wsu_id = None, email='testy2.tester@wsu.com', user_type = 'Student')
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u2.can_apply(), False)


    def test_apply_student(self):
        u1 = Student(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Student')
        db.session.add(u1)
        db.session.commit()
        f1 = create_user1('Faculty', 'andy', 'aofallon@wsy.edu', 'abc', '444444444')
        db.session.add(f1)
        db.session.commit()
        p1 = Post(user_id =f1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        u1.apply(p1,'Hi', 'KC Wang')
        db.session.commit()
        self.assertEqual(Application.query.all()[0].applicant_id, u1.id)
        self.assertEqual(Application.query.all()[0].post_id, p1.id)



    def test_unapply_student(self):
        u1 = Student(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Student')
        db.session.add(u1)
        db.session.commit()
        f1 = create_user1('Faculty', 'andy', 'aofallon@wsy.edu', 'abc', '444444444')
        db.session.add(f1)
        db.session.commit()
        p1 = Post(user_id =f1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        u1.apply(p1,'Hi', 'KC Wang')
        db.session.commit()
        u1.unapply(p1)
        db.session.commit()
        self.assertEqual(Application.query.all(), [])
        

    def test_can_apply_faculty(self):
        u1 = Faculty(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'Faculty')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.can_apply(), False)

    
    def test_post_1(self): # TEST INITIATIVE: Datebase allocation
        u1 = Faculty(username='test', wsu_id = '111111111', email='testy.tester@wsu.com', user_type = 'faculty')
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.posts.all(), [])

        p1 = Post(user_id = u1.id, title='My post', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(u1.posts.count(), 1)
        self.assertEqual(u1.posts[0].title, 'My post')
        self.assertEqual(u1.posts[0].body, 'This is my test post.')
        self.assertEqual(u1.posts[0].time_commitment, '20')
        self.assertEqual(u1.posts[0].start_date, datetime.datetime(2023, 5, 11).date())
        self.assertEqual(u1.posts[0].end_date, datetime.datetime(2024, 1, 21).date())

        p2 = Post(user_id = u1.id, title='Second post', body='This is my 2nd test post.', time_commitment = '100', start_date = datetime.datetime(2024, 10, 12), end_date = datetime.datetime(2025, 1, 17))
        db.session.add(p2)
        db.session.commit()
        self.assertEqual(u1.posts.count(), 2)
        self.assertEqual(u1.posts[1].title, 'Second post')
        self.assertEqual(u1.posts[1].body, 'This is my 2nd test post.')
        self.assertEqual(u1.posts[1].time_commitment, '100')
        self.assertEqual(u1.posts[1].start_date, datetime.datetime(2024, 10, 12).date())
        self.assertEqual(u1.posts[1].end_date, datetime.datetime(2025, 1, 17).date())

    def test_get_fields(self):
        f1 = create_user1('Faculty', 'andy', 'aofallon@wsu.edu', 'abc', '444444444')
        db.session.add(f1)
        db.session.commit()
        major1 = Major(name = 'Computer Science', id = 1)
        field1 = Field(field = 'Machine Learning', id = 1)
        db.session.add(major1)
        db.session.add(field1)
        faculty_user = User.query.filter_by(username = 'andy').first()
        p1 = Post(user_id = faculty_user.id, title= 'Everyone Loves Checkers', 
            body = 'If you are interested in machine learning, do I have a lab position for you. We are teaming up with the International Association for Professional Checkers Players to create a machine learning AI that will test the skills of the best checker players across the world. Applicants who have taken intro to machine learning courses and further will have a competitive advantage in receiving a position for this lab.', 
            majors = [major1],
            fields = [field1],
            time_commitment = '10-20',
            start_date = datetime.datetime(2022, 6, 2),
            end_date = datetime.datetime(2022, 8, 28)
            )
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(p1.get_fields().all() , [field1])
        

    def test_get_majors(self):
        f1 = create_user1('Faculty', 'andy', 'aofallon@wsu.edu', 'abc', '444444444')
        db.session.add(f1)
        db.session.commit()
        major1 = Major(name = 'Computer Science', id = 1)
        field1 = Field(field = 'Machine Learning', id = 1)
        db.session.add(major1)
        db.session.add(field1)
        faculty_user = User.query.filter_by(username = 'andy').first()
        p1 = Post(user_id = faculty_user.id, title= 'Everyone Loves Checkers', 
            body = 'If you are interested in machine learning, do I have a lab position for you. We are teaming up with the International Association for Professional Checkers Players to create a machine learning AI that will test the skills of the best checker players across the world. Applicants who have taken intro to machine learning courses and further will have a competitive advantage in receiving a position for this lab.', 
            majors = [major1],
            fields = [field1],
            time_commitment = '10-20',
            start_date = datetime.datetime(2022, 6, 2),
            end_date = datetime.datetime(2022, 8, 28)
            )
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(p1.get_majors().all() , [major1])

    


# TEST: APPLICATION

    def test_application_1(self): # TEST INITIATIVE: Relationship validity
        init_majors_and_fields()
        # faculty user
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsy.edu', 'abc', '55555555')
        db.session.add(f1)

        # student user
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)
        db.session.commit()

        self.assertEqual(2, User.query.count()) # verify users are made
        
        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(1, Application.query.count())           #    testing: if expected application count is correct
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student
        self.assertEqual('Test Position 1', a2.get_position())   #    testing: if application relationship with post is correct

    def test_application_2(self): # TEST INITIATIVE: Application relationship on multiple applications for one post
        init_majors_and_fields()
        # faculty user 1
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsu.edu', 'abc', '55555555')
        db.session.add(f1)

        # faculty user 2
        f2 = create_user1('Faculty', 'andy', 'aofallon@wsu.edu', 'abc', '444444444')
        db.session.add(f2)

        # faculty user 3
        f3 = create_user1('Faculty', 'ted', 'ted@wsu.edu', 'abc', '333333333')
        db.session.add(f3)

        # student user 1
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)

        # student user 2
        s2 = create_user2('Student', 'bobby', 'bobby@wsu.edu', 'abc', '232323231', 'Bob', 'Marley', '1123456785', 
                           'Electrical Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            3.67, datetime.datetime(2026, 5, 20), 'Bio102 - C, cs322 - A, cs223 - D', 'C/C++, Javascript, HTML', 'None')
        db.session.add(s2)

        # student user 3
        s3 = create_user2('Student', 'tay', 'tay@wsu.edu', 'abc', '783625424', 'jing ren', 'tay', '5672341234', 
                            'Computer Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            2.67, datetime.datetime(2022, 5, 20), 'cs360 - C, cs322 - A, cs355 - F', 'C/C++, Haskell, HTML', 'None')
        db.session.add(s3)

        db.session.commit()          

        self.assertEqual(6, User.query.count()) # verify users are made

        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a1 = Application(applicant_id = s3.id, post_id = p1.id, student_applied = s3, position_for = p1, faculty_ref = "BOB (111)-111-111")
        db.session.add(a1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(2, Application.query.count())           #    testing: works correctly with multiple applications
        self.assertEqual(s3.id, a1.get_applicant().id)           #    testing: if application belongs to student 3
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student 1
        self.assertEqual([], s2.applications)                    #    testing: that student 2 never applied


    def test_application_3(self): # TEST INITIATIVE: Phantom Applications (From Post Deletion)
        init_majors_and_fields()
        # faculty user
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsy.edu', 'abc', '55555555')
        db.session.add(f1)

        # student user
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)
        db.session.commit()

        self.assertEqual(2, User.query.count()) # verify users are made
    
        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(1, Application.query.count())           #    testing: if expected application count is correct
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student
        self.assertEqual('Test Position 1', a2.get_position())   #    testing: if application relationship with post is correct

        applications = p1.get_applicants()

        for application in applications: # Remove connection in applications
            application.phantom_name = p1.title
            application.make_phantom()  # Retain post information
        
        db.session.delete(p1)
        db.session.commit()

        self.assertEqual(0, Post.query.count())                                   #    testing: verify post has been deleted
        self.assertEqual(1, Application.query.count())                            #    testing: verify application was never deleted
        self.assertEqual([p1.title, 'No Longer Available'], a2.get_phantom())     #    testing: application is now in phantom mode


# TEST: MAJORS

    def test_majors_1(self):  # TEST INITIATIVE: Database allocation
        major1 = Major(name = 'Computer Science', id = 1)
        major2 = Major(name = 'Computer Engineering', id = 2)
        major3 = Major(name = 'Electrical Engineering', id = 3)
        major4 = Major(name = 'Mechanical Engineering', id = 4)

        db.session.add(major1) # Add Majors
        db.session.add(major2)
        db.session.add(major3)
        db.session.add(major4) 
        db.session.commit()

        self.assertEqual(4, Major.query.count())                             #    testing: verify 4 majors have been made
        self.assertEqual('Computer Science', major1.get_major_name())        #    testing: major1 is correct
        self.assertEqual('Electrical Engineering', major3.get_major_name())  #    testing: major3 is correct

    def test_majors_2(self): # TEST INITIATIVE: Relationship validity
        init_majors_and_fields() # populate database with majors connected to fields (and vice versa)

        major2 = Major.query.all()[1] # 2nd major created

        self.assertEqual('Computer Engineering', major2.get_major_name())  #    testing: major2 is correct

        major_fields = major2.get_fields() # init_majors_and_fields() assigns 6 fields to Computer Engineering
        
        self.assertEqual(6, len(major_fields))  # testing: major2's fields were properly assigned

# TEST: FIELDS
    def test_fields_1(self): # TEST INITIATIVE: Database allocation
        # Research Fields
        field1 = Field(field = 'Machine Learning', id = 1)
        field2 = Field(field = 'Networking', id = 2)
        field3 = Field(field = 'Data Science', id = 3)
        field4 = Field(field = 'Logic Circuits', id = 4)

        db.session.add(field1) # Add Majors
        db.session.add(field2)
        db.session.add(field3)
        db.session.add(field4) 
        db.session.commit()
        
        self.assertEqual(4, Field.query.count())                        #    testing: verify 4 fields have been made
        self.assertEqual('Machine Learning', field1.get_name())         #    testing: field1 is correct
        self.assertEqual('Data Science', field3.get_name())             #    testing: field3 is correct

    def test_fields_2(self):  # TEST INITIATIVE: Relationship validity
        init_majors_and_fields() # populate database with majors connected to fields (and vice versa)

        field6 = Field.query.filter_by(id = 6).first() # 6th field created

        self.assertEqual('Quantum Computing', field6.get_name())  #    testing: field6 is correct

        field_majors = field6.get_majors() # init_majors_and_fields() assigns 3 majors to Quantum Computing
        
        self.assertEqual(3, len(field_majors))  # testing: field6's majors were properly assigned



# TEST: APPLICATION

    def test_application_1(self): # TEST INITIATIVE: Relationship validity
        init_majors_and_fields()
        # faculty user
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsy.edu', 'abc', '55555555')
        db.session.add(f1)

        # student user
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)
        db.session.commit()

        self.assertEqual(2, User.query.count()) # verify users are made
        
        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(1, Application.query.count())           #    testing: if expected application count is correct
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student
        self.assertEqual('Test Position 1', a2.get_position())   #    testing: if application relationship with post is correct

    def test_application_2(self): # TEST INITIATIVE: Application relationship on multiple applications for one post
        init_majors_and_fields()
        # faculty user 1
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsu.edu', 'abc', '55555555')
        db.session.add(f1)

        # faculty user 2
        f2 = create_user1('Faculty', 'andy', 'aofallon@wsu.edu', 'abc', '444444444')
        db.session.add(f2)

        # faculty user 3
        f3 = create_user1('Faculty', 'ted', 'ted@wsu.edu', 'abc', '333333333')
        db.session.add(f3)

        # student user 1
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)

        # student user 2
        s2 = create_user2('Student', 'bobby', 'bobby@wsu.edu', 'abc', '232323231', 'Bob', 'Marley', '1123456785', 
                           'Electrical Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            3.67, datetime.datetime(2026, 5, 20), 'Bio102 - C, cs322 - A, cs223 - D', 'C/C++, Javascript, HTML', 'None')
        db.session.add(s2)

        # student user 3
        s3 = create_user2('Student', 'tay', 'tay@wsu.edu', 'abc', '783625424', 'jing ren', 'tay', '5672341234', 
                            'Computer Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            2.67, datetime.datetime(2022, 5, 20), 'cs360 - C, cs322 - A, cs355 - F', 'C/C++, Haskell, HTML', 'None')
        db.session.add(s3)

        db.session.commit()          

        self.assertEqual(6, User.query.count()) # verify users are made

        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a1 = Application(applicant_id = s3.id, post_id = p1.id, student_applied = s3, position_for = p1, faculty_ref = "BOB (111)-111-111")
        db.session.add(a1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(2, Application.query.count())           #    testing: works correctly with multiple applications
        self.assertEqual(s3.id, a1.get_applicant().id)           #    testing: if application belongs to student 3
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student 1
        self.assertEqual([], s2.applications)                    #    testing: that student 2 never applied


    def test_application_3(self): # TEST INITIATIVE: Phantom Applications (From Post Deletion)
        init_majors_and_fields()
        # faculty user
        f1 =  create_user1('Faculty', 'sakire', 'sakire@wsy.edu', 'abc', '55555555')
        db.session.add(f1)

        # student user
        s1 = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
        db.session.add(s1)
        db.session.commit()

        self.assertEqual(2, User.query.count()) # verify users are made
    
        p1 = Post(user_id = f1.id, title='Test Position 1', body='This is my test post.', time_commitment = '20', start_date = datetime.datetime(2023, 5, 11), end_date = datetime.datetime(2024, 1, 21))
        db.session.add(p1)
        db.session.commit()

        a2 = Application(applicant_id = s1.id, post_id = p1.id, student_applied = s1, position_for = p1, faculty_ref = "KC WANG (000)-000-000")
        db.session.add(a2)
        db.session.commit()

        self.assertEqual(1, Application.query.count())           #    testing: if expected application count is correct
        self.assertEqual(s1.id, a2.get_applicant().id)           #    testing: if application belongs to student
        self.assertEqual('Test Position 1', a2.get_position())   #    testing: if application relationship with post is correct

        applications = p1.get_applicants()

        for application in applications: # Remove connection in applications
            application.phantom_name = p1.title
            application.make_phantom()  # Retain post information
        
        db.session.delete(p1)
        db.session.commit()

        self.assertEqual(0, Post.query.count())                                   #    testing: verify post has been deleted
        self.assertEqual(1, Application.query.count())                            #    testing: verify application was never deleted
        self.assertEqual([p1.title, 'No Longer Available'], a2.get_phantom())     #    testing: application is now in phantom mode


# TEST: MAJORS

    def test_majors_1(self):  # TEST INITIATIVE: Database allocation
        major1 = Major(name = 'Computer Science', id = 1)
        major2 = Major(name = 'Computer Engineering', id = 2)
        major3 = Major(name = 'Electrical Engineering', id = 3)
        major4 = Major(name = 'Mechanical Engineering', id = 4)

        db.session.add(major1) # Add Majors
        db.session.add(major2)
        db.session.add(major3)
        db.session.add(major4) 
        db.session.commit()

        self.assertEqual(4, Major.query.count())                             #    testing: verify 4 majors have been made
        self.assertEqual('Computer Science', major1.get_major_name())        #    testing: major1 is correct
        self.assertEqual('Electrical Engineering', major3.get_major_name())  #    testing: major3 is correct

    def test_majors_2(self): # TEST INITIATIVE: Relationship validity
        init_majors_and_fields() # populate database with majors connected to fields (and vice versa)

        major2 = Major.query.all()[1] # 2nd major created

        self.assertEqual('Computer Engineering', major2.get_major_name())  #    testing: major2 is correct

        major_fields = major2.get_fields() # init_majors_and_fields() assigns 6 fields to Computer Engineering
        
        self.assertEqual(6, len(major_fields))  # testing: major2's fields were properly assigned

# TEST: FIELDS
    def test_fields_1(self): # TEST INITIATIVE: Database allocation
        # Research Fields
        field1 = Field(field = 'Machine Learning', id = 1)
        field2 = Field(field = 'Networking', id = 2)
        field3 = Field(field = 'Data Science', id = 3)
        field4 = Field(field = 'Logic Circuits', id = 4)

        db.session.add(field1) # Add Majors
        db.session.add(field2)
        db.session.add(field3)
        db.session.add(field4) 
        db.session.commit()
        
        self.assertEqual(4, Field.query.count())                        #    testing: verify 4 fields have been made
        self.assertEqual('Machine Learning', field1.get_name())         #    testing: field1 is correct
        self.assertEqual('Data Science', field3.get_name())             #    testing: field3 is correct

    def test_fields_2(self):  # TEST INITIATIVE: Relationship validity
        init_majors_and_fields() # populate database with majors connected to fields (and vice versa)

        field6 = Field.query.filter_by(id = 6).first() # 6th field created

        self.assertEqual('Quantum Computing', field6.get_name())  #    testing: field6 is correct

        field_majors = field6.get_majors() # init_majors_and_fields() assigns 3 majors to Quantum Computing
        
        self.assertEqual(3, len(field_majors))  # testing: field6's majors were properly assigned



if __name__ == '__main__':
    unittest.main(verbosity=2)