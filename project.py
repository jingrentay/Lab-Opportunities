from app import create_app, db
from app.Model.models import Faculty, User, Student, Post, Major, Field, postMajors, majorFields
import datetime
app = create_app()

# ================================================================
#   Name:           Init DB
#   Description:    If there is not db, call this function to initialize it
#   Last Changed:   10/26/21
#   Changed By:     Reagan Kelley
#   Change Details: Skeleton version for initDB (taken from smileApp)
#=================================================================
@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()

    # Creates Majors and Research Fields
    if Major.query.count() == 0:
        init_majors_and_fields()

        print("Majors")
        for major in Major.query.all():
            print('\t', major)

        print('\nResearch Fields:')
        for field in Field.query.all():
            print('\t', field)
            
    if(app.debug):
        if(User.query.count() == 0): # Don't reinitialize if already initialzed (duh)
            print("Debug: Initializing with pre-existing data...")
            fill_db()

    # if Field.query.count() is None:
    #     field_name = [{'field_name':'Artificial Intelligence', 'major_name':'Computer Science'}]
    #     for f in field_name:
    #         db.session.add(Field(majors = f['majors'], field = f['field']))
    #     db.session.commit()

def init_majors_and_fields():
    # Majors
    major1 = Major(name = 'Computer Science', id = 1)
    major2 = Major(name = 'Computer Engineering', id = 2)
    major3 = Major(name = 'Electrical Engineering', id = 3)
    major4 = Major(name = 'Mechanical Engineering', id = 4)

    fieldNA = Field(field = 'Empty Field', id = -1)
    # Research Fields
    field1 = Field(field = 'Machine Learning', id = 1)
    field2 = Field(field = 'Networking', id = 2)
    field3 = Field(field = 'Data Science', id = 3)
    field4 = Field(field = 'Logic Circuits', id = 4)
    field5 = Field(field = 'Unix-Linux Systems', id = 5)
    field6 = Field(field = 'Quantum Computing', id = 6)
    field7 = Field(field = 'Circuit Design', id = 7)
    field8 = Field(field = 'Robotics', id = 8)
    field9 = Field(field = 'Electronics', id = 9)
    field10 = Field(field = 'Cyber Security', id = 10)
    field11 = Field(field = 'Mobile Devices', id = 11)

    # Build relationship between majors and fields
    # Computer Science
    major1.fields.append(field1)
    major1.fields.append(field2)
    major1.fields.append(field3)
    major1.fields.append(field5)
    major1.fields.append(field6)
    major1.fields.append(field10)

    # Computer Engineering
    major2.fields.append(field1)
    major2.fields.append(field2)
    major2.fields.append(field4)
    major2.fields.append(field6)
    major2.fields.append(field8)
    major2.fields.append(field11)

    # Electrical Engineering
    major3.fields.append(field4)
    major3.fields.append(field6)
    major3.fields.append(field7)
    major3.fields.append(field8)
    major3.fields.append(field9)
    major3.fields.append(field11)

    # Mechanical Engineering
    major4.fields.append(field4)
    major4.fields.append(field7)
    major4.fields.append(field8)
    major4.fields.append(field9)
    major4.fields.append(field11)


    db.session.add(major1) # Add Majors
    db.session.add(major2)
    db.session.add(major3)
    db.session.add(major4) 

    db.session.add(field1) # Add Fields
    db.session.add(field2)
    db.session.add(field3)
    db.session.add(field4)
    db.session.add(field5)
    db.session.add(field6)
    db.session.add(field7)
    db.session.add(field8)
    db.session.add(field9)
    db.session.add(field10)
    db.session.add(field11)

    db.session.add(fieldNA)
    
    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)

# ================================================================
#   Name:           create_user1
#   Description:    Creates a user of type student or Faculty
#   Last Changed:   12/6/21
#   Changed By:     Reagan Kelley
#   Change Details: Initial Implementation
# ================================================================
def create_user1(user_type, username, email, password, wsu_id):
    if (user_type == 'Faculty'):
        new_user = Faculty(username = username, wsu_id = wsu_id, email = email, user_type = 'faculty')
    elif (user_type == 'Student'):
        new_user = Student(username = username, wsu_id = wsu_id, email = email, user_type = 'student')
    else:
        print('create_user: improper user type')
        return None

    new_user.set_password(password)
    db.session.add(new_user)
    return new_user

# ================================================================
#   Name:           create_user2
#   Description:    Creates a user of type student
#   Last Changed:   12/6/21
#   Changed By:     Reagan Kelley
#   Change Details: Initial Implementation
# ================================================================
def create_user2(user_type, username, email, password, wsu_id, first_name, last_name, phone_no, major_name, fields, gpa, graduation_date, courses, languages, prior_research):
    if (user_type == 'Faculty'):
        print('create_user: improper definition of faculty')
        return None
    elif (user_type == 'Student'):
        new_user = Student(username = username, wsu_id = wsu_id, email = email, user_type = 'student')
    else:
        print('create_user: improper user type')
        return None

    new_user.set_password(password)

    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.phone_no = phone_no

    # Get major
    #print(Major.query.filter_by(name = major_name).first())
    if(Major.query.filter_by(name = major_name).first() == None):
        new_user.major = None
    else:
        new_user.major = Major.query.filter_by(name = major_name).first().id

    # Get_fields
    field_list = []
    for field_name in fields:
        field = Field.query.filter_by(field = field_name).first()
        if field is not None:
            field_list.append(field)
    new_user.fields = field_list

    new_user.gpa = gpa
    new_user.expected_grad_date = graduation_date
    new_user.elect_courses = courses
    new_user.languages = languages
    new_user.prior_research = prior_research
    
    return new_user

# ================================================================
#   Name:           Fill Database
#   Description:    If in debug fills database with data
#   Last Changed:   12/6/21
#   Changed By:     Reagan Kelley
#   Change Details: Updated db creation with more efficient 
#                   create functions
# ================================================================
def fill_db():

    # User: andy | Faculty
    new_user = create_user1('Faculty', 'andy', 'aofallon@wsu.edu', 'abc', '444444444')
    db.session.add(new_user)
    print("Debug: Added New Faculty: [andy]")

    # User: sakire | Faculty
    new_user = create_user1('Faculty', 'sakire', 'sakire@wsu.edu', 'abc', '55555555')
    db.session.add(new_user)
    print("Debug: Added New Faculty: [sakire]")

    # User: reagan | Student
    new_user = create_user2('Student', 'reagan', 'reagan.kelley@wsu.edu', 'abc', '11663871', 'Reagan', 'Kelley', '2094804983', 
                            'Computer Science', ['Machine Learning', 'Robotics', 'Circuit Design', 'Unix-Linux Systems'], 
                            4.97, datetime.datetime(2023, 5, 20), 'cs360 - A, cs322 - A, cs223 - A', 'C/C++, Javascript, Haskell, Java', 'None')
    db.session.add(new_user)
    print("Debug: Added New Student: [reagan]")

    # User: bobby | Student
    new_user = create_user2('Student', 'bobby', 'bobby@wsu.edu', 'abc', '232323231', 'Bob', 'Marley', '1123456785', 
                            'Electrical Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            3.67, datetime.datetime(2026, 5, 20), 'Bio102 - C, cs322 - A, cs223 - D', 'C/C++, Javascript, HTML', 'None')
    db.session.add(new_user)
    print("Debug: Added New Student: [bobby]")

    # User: denise | Student
    new_user = create_user2('Student', 'denise', 'denise@wsu.edu', 'abc', '673579425', 'Denise', 'Tanumihardja', '3609871121', 
                            'Computer Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            2.67, datetime.datetime(2023, 5, 20), 'cs360 - C, cs322 - A, cs223 - D', 'C/C++, Haskell, HTML', 'None')
    db.session.add(new_user)
    print("Debug: Added New Student: [denise]")
    
     # User: tay | Student
    new_user = create_user2('Student', 'tay', 'tay@wsu.edu', 'abc', '783625424', 'jing ren', 'tay', '5672341234', 
                            'Computer Engineering', ['Machine Learning', 'Robotics', 'Circuit Design'], 
                            2.67, datetime.datetime(2022, 5, 20), 'cs360 - C, cs322 - A, cs355 - F', 'C/C++, Haskell, HTML', 'None')
    db.session.add(new_user)
    print("Debug: Added New Student: [tay]")
    
    # Post: Database Integrity
    # Posted By: Sakire
    _majors = Major.query.slice(0,2) # Gets first two majors in list (TODO: if you can find a better way of sorts majors please change)
    fields = _majors.first().fields
    faculty_user = User.query.filter_by(username = 'sakire').first()
    newPost = Post(user_id = faculty_user.id, title= 'Database Integrity', 
            body = 'We are looking for 3-4 year undergrad students who enjoy working in the fields of networking and cybersecurity. We are teaming up with Amazon to make penetration software that will test the integrity of their AWS systems. You do not need to be an expert on databases nor security, but it would be very helpful.', 
            majors = _majors,
            fields = fields,
            time_commitment = '25',
            start_date = datetime.datetime(2022, 1, 10),
            end_date = datetime.datetime(2022, 5, 21)
            )
    db.session.add(newPost)
    print("Debug: Added New Post: [Database Integrity]")

    _majors = Major.query.all()
    fields = _majors[2].fields
    faculty_user = User.query.filter_by(username = 'sakire').first()
    newPost = Post(user_id = faculty_user.id, title = 'Robots are cool!', body = 'Post description.', majors = _majors, fields = fields, 
                  time_commitment = '20-30', start_date = datetime.datetime(2022, 6, 2), end_date = datetime.datetime(2022, 12, 19))
    db.session.add(newPost)
    print("Debug: Added New Post: [Robots are cool!]")

    _majors = Major.query.slice(2, 3)
    fields = _majors.first().fields
    faculty_user = User.query.filter_by(username = 'sakire').first()
    newPost = Post(user_id = faculty_user.id, title = 'Next Generation Robots', body = 'Post Description.', majors = _majors, fields = fields, 
                   time_commitment = '12-29', start_date = datetime.datetime(2021, 10, 28), end_date = datetime.datetime(2021, 10, 29))
    db.session.add(newPost)
    print("Debug: Added New Post: [Next Generation Robots]")

    # Post: Checkers AI
    # Posted By: Andy
    _majors = Major.query.all()
    fields = _majors[3].fields
    faculty_user = User.query.filter_by(username = 'andy').first()
    newPost = Post(user_id = faculty_user.id, title= 'Everyone Loves Checkers', 
            body = 'If you are interested in machine learning, do I have a lab position for you. We are teaming up with the International Association for Professional Checkers Players to create a machine learning AI that will test the skills of the best checker players across the world. Applicants who have taken intro to machine learning courses and further will have a competitive advantage in receiving a position for this lab.', 
            majors = _majors,
            fields = fields,
            time_commitment = '10-20',
            start_date = datetime.datetime(2022, 6, 2),
            end_date = datetime.datetime(2022, 8, 28)
            )
    print("Debug: Added New Post: [Everyone Loves Checkers]")

    _majors = Major.query.slice(2, 4)
    fields = _majors.first().fields
    faculty_user = User.query.filter_by(username = 'andy').first()
    newPost = Post(user_id = faculty_user.id, title = 'Computer to Machine Designs', body = 'Post description.', majors = _majors, fields = fields,
                   time_commitment = '10-15', start_date = datetime.datetime(2021, 12, 8), end_date = datetime.datetime(2021, 12, 9))
    db.session.add(newPost)
    print("Debug: Added New Post: [Computer to Machine Designs]")

    _majors = Major.query.all()
    fields = _majors[2].fields
    faculty_user = User.query.filter_by(username = 'andy').first()
    newPost = Post(user_id = faculty_user.id, title = 'Test Post 4', body = 'Post description.', majors = _majors, fields = fields,
                   time_commitment = '20-30', start_date = datetime.datetime(2020, 5, 28), end_date = datetime.datetime(2020, 10, 20))
    db.session.add(newPost)
    print("Debug: Added New Post: [Test Post 4]")


    db.session.add(newPost)
    print("Debug: Added New Post: [Everyone Loves Checkers]")


    # Commit changes to database
    db.session.commit()
    print("Debug: Committing Changes ...")

