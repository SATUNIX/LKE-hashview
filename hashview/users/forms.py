from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Length
from hashview.models import Users

class UsersForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Is Admin')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=14)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    pushover_app_id = StringField('Pushover App Token (optional)')
    pushover_user_key = StringField('Pushover User Key (optional)')
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = Users.query.filter_by(email_address = email.data).first()
        if user:
            raise ValidationError('That email address is taken. Please choose a different one.')

    def validate_pushover(self, pushover_app_id, pushover_user_key):
        if len(pushover_app_id.data) > 0 and len(pushover_user_key.data) == 0:
            raise ValidationError('You must supply both options to use.')
        if len(pushover_app_id.data) == 0 and len(pushover_user_key.data) > 0:
            raise ValidationError('You must supply both options to use.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    pushover_app_id = StringField('Pushover Id (optional)')
    pushover_user_key = StringField('Pushover Key (optional)')
    submit = SubmitField('Update')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=14)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')