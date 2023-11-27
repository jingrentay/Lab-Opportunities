from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Length, Email
from app.Model.models import User, Major
from flask_login import current_user

# ================================================================
#   Name:           Register form
#   Description:    Class definition for Registering new user
#   Last Changed:   11/30/21
#   Changed By:     Reagan Kelley
#   Change Details: Added validate_domain
# ================================================================
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    wsu_id = StringField('WSU ID', validators=[DataRequired(), Length(min = 8, max = 9)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    type = SelectField('User', choices = [(0, 'Student'), (1, 'Faculty')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('This username has been taken. Please use a different username.')
       
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('This email is used by another account. Please enter a different email.')
        # All emails must have the wsu.edu domain name     
        if "@wsu.edu" not in email.data:
            raise ValidationError('Email must be a WSU email address.')
    



# ================================================================
#   Name:           Login form
#   Description:    Class definition for Login
#   Last Changed:   10/26/21
#   Changed By:     Denise Tanumihardja
#   Change Details: Initial implementation of LoginForm class. (taken from smile project)
# ================================================================
class LoginForm(FlaskForm):
    username = StringField('User', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')