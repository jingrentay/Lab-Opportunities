from datetime import datetime
from enum import unique
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from app import login

# ================================================================
# Gets User.id for logged in user (updated 10/27/21): fixed int error
# ================================================================
@login.user_loader
def load_user(id):
    return User.query.get(id)

# ================================================================
# Relationship: Every post can have multiple Majors
# ================================================================
postMajors = db.Table('postMajors',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('major_id', db.Integer, db.ForeignKey('major.id')))


# ================================================================
# Relationship: Every post can have multiple fields
# ================================================================
postFields = db.Table('postFields',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('field_id', db.Integer, db.ForeignKey('field.id')))


# ================================================================
# Relationship: Every Research Field can have multiple majors
# ================================================================
majorFields = db.Table('majorFields', 
     db.Column('field_id', db.Integer, db.ForeignKey('field.id')),
     db.Column('major_id', db.Integer, db.ForeignKey('major.id')))


# ================================================================
# Relationship: Every student can have multiple fields
# ================================================================
studentFields = db.Table('studentFields', 
     db.Column('field_id', db.Integer, db.ForeignKey('field.id')),
     db.Column('student_id', db.Integer, db.ForeignKey('student.id')))

     
# ================================================================
#   Name:           User Model
#   Description:    Class Definition for User
#   Last Changed:   11/24/21
#   Changed By:     Reagan Kelley
#   Change Details: Revised User database model
# ================================================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    wsu_id = db.Column(db.String, unique = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(120), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20))

    __mapper_args__ = { # Creates a connection within SQL, allows User to see its children classes
        'polymorphic_identity':'user',
        'polymorphic_on': user_type
    }
    
    def __repr__(self):
        return '<Username: {} - {};>'.format(self.id,self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def get_user_type(self):
        return self.user_type

    def get_user_posts(self):
        return self.posts

    def apply(self, thepost, brief, ref): ##apply to a position
        if not self.has_applied(thepost):
            newApplication = Application(position_for = thepost, 
                                         status = 'Pending', 
                                         personal_statement = brief,
                                         faculty_ref = ref)
            self.applications.append(newApplication)
            db.session.commit()

    def unapply(self, oldpost):
        if self.has_applied(oldpost):
            curApplication = Application.query.filter_by(applicant_id=self.id).filter_by(post_id = oldpost.id).first()
            db.session.delete(curApplication)
            db.session.commit()

    def has_applied(self, newpost):
        return (Application.query.filter_by(applicant_id=self.id).filter_by(post_id = newpost.id).count() > 0)

    def get_status(self, newpost):
        application = Application.query.filter_by(applicant_id=self.id).filter_by(post_id = newpost.id).first()
        return application.status

# ================================================================
#   Name:           Student Model
#   Description:    Class Definition for Student (Child of User)
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Added fields
# ================================================================
class Student(User):

    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # Student Attributes
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(100))
    phone_no = db.Column(db.String(10))
    major = db.Column(db.Integer, db.ForeignKey('major.id'))
    gpa = db.Column(db.Float(precision = 1))
    expected_grad_date = db.Column(db.Date)
    elect_courses = db.Column(db.String(1500))
    fields = db.relationship('Field', secondary = studentFields, back_populates = 'students')
    languages = db.Column(db.String(700))
    prior_research = db.Column(db.String(1500))

    applications = db.relationship('Application', back_populates = 'student_applied')
    __mapper_args__ = {
        'polymorphic_identity':'student',
    }

    def get_major(self):
        return Major.query.filter_by(id = self.major).first().name

    def __repr__(self):
        return '<Username: {} - {}; Type: {}; Class-Object Code: 0>'.format(self.id,self.wsu_id, self.get_user_type())
    
    def can_apply(self): # Students should only be able to apply to position posts if their info is submitted
        if(self.wsu_id is None):
            return False
        return True

# ================================================================
#   Name:           Faculty Model
#   Description:    Class Definition for Faculty (Child of User)
#   Last Changed:   11/24/21
#   Changed By:     Reagan Kelley
#   Change Details: Revised Database Model to allow for user children
# ================================================================
class Faculty(User):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    posts = db.relationship('Post', backref='writer', lazy = 'dynamic')

    __mapper_args__ = {
        'polymorphic_identity':'faculty',
    }
    def __repr__(self):
        return '<Username: {} - {}; Type: {}; Class-Object Code: 1>'.format(self.id,self.username, self.get_user_type())

    def can_apply(self):
        return False # Faculty can never apply to a position post

# ================================================================
#   Name:           Application Model
#   Description:    Class Definition for Application
#   Last Changed:   12/3/21
#   Changed By:     Reagan Kelley
#   Change Details: Added phantom application implementation
#                   Fixed primary restraint bug
# ================================================================
class Application(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    student_applied = db.relationship('User')
    position_for = db.relationship('Post')

    status = db.Column(db.String(20))
    personal_statement = db.Column(db.String(1500))
    faculty_ref = db.Column(db.String(60))

    phantom_name = db.Column(db.String(150), default = "")


    def __repr__(self):
        return '<Application for {} - by {};>'.format(self.post_id,self.applicant_id)

    def make_phantom(self):
        self.status = 'No Longer Available'
        self.post_id = -1

    def get_phantom(self):
        return [self.phantom_name, self.status]

    def get_applicant(self):
        return User.query.filter_by(id = self.applicant_id).first()

    def get_position(self):
        return Post.query.filter_by(id = self.post_id).first().title

    def get_status(self):
        return self.status

# ================================================================
#   Name:           Post Model
#   Description:    Class Definition for Posts
#   Last Changed:   12/1/21
#   Changed By:     Reagan Kelley
#   Change Details: Added Time Commitmen, start & end dates
#                   Added fields to posts.
# ================================================================
class Post(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    title = db.Column(db.String(150))
    body = db.Column(db.String(1500))
    time_commitment = db.Column(db.String(10))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    majors = db.relationship('Major', 
        backref = db.backref('postMajors', lazy='dynamic'), 
        secondary = postMajors, 
        primaryjoin = (postMajors.c.post_id == id),  
        lazy = 'dynamic' 
    )

    fields = db.relationship('Field', 
        backref = db.backref('postFields', lazy='dynamic'), 
        secondary = postFields, 
        primaryjoin = (postFields.c.post_id == id),  
        lazy = 'dynamic' 
    )

    applicants = db.relationship('Application', back_populates = 'position_for')

    def get_applicants(self):
        return self.applicants

    def get_fields(self):
        return self.fields

    def get_majors(self):
        return self.majors

    
# ================================================================
#   Name:           Major Model
#   Description:    Class Definition for Major (Tag)
#   Last Changed:   12/1/21
#   Changed By:     Reagan Kelley
#   Change Details: Created relationship with fields
# ================================================================
class Major(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))

    # A major can have multiple research fields
    fields = db.relationship('Field', secondary = majorFields, back_populates = 'majors')
    def get_major_name(self):
        return self.name
    
    def __repr__(self):
         return "< Major: [{}] - with field(s): {}>".format(self.name, self.get_fields())

    def get_fields(self):
        field_list = []
        for field in self.fields:
            field_list.append(field.get_name())
        return field_list


# ================================================================
#   Name:           Research Field Model
#   Description:    Class Definition for Research Field (Tag)
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Implented with student
# ================================================================
class Field(db.Model):
     __tablename__ = 'field'
     id = db.Column(db.Integer, primary_key = True)
     field = db.Column(db.String(50), primary_key = True)

     # A field can have multiple majors
     majors = db.relationship('Major', secondary = majorFields, back_populates = 'fields')
     students = db.relationship('Student', secondary = studentFields, back_populates = 'fields')

     
     def get_name(self):
        return "{}".format(self.field)

     def get_num_tags(self):
        return len(self.get_name)
    
     def is_for_major(self, major):
        if major in self.majors:
            return True
        return False


     def get_majors(self):
        major_list = []
        for major in self.majors:
            major_list.append(major.get_major_name())
        return major_list

     def __repr__(self):
        return "< Field: [{}] - of major(s): {}>".format(self.field, self.get_majors())






