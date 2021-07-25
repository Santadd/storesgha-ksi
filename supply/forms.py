from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import Email, EqualTo, DataRequired, InputRequired, Length, NumberRange, ValidationError
from supply.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already taken!. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class AddItemsForm(FlaskForm):
    descr = StringField('Description', validators=[DataRequired()])
    card = StringField('Card No.', validators=[DataRequired()])
    usrv = StringField('U.S.R.V & W.B', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    fr_om = StringField('From', validators=[DataRequired()])
    inp_ut = IntegerField('Input', validators=[DataRequired(message="Please enter a valid number"), 
                                    NumberRange(min=0, message="Input cannot be negative")])
    balance = IntegerField('Balance', validators=[DataRequired(message="Please enter a valid number"),
                                    NumberRange(min=0, message="Balance cannot be negative")])
    cedis = IntegerField('Cedis', validators=[InputRequired(message="Please enter a valid amount")])
    pesewas = IntegerField('Pesewas', validators=[InputRequired(message="Please enter a valid amount")])
    
    submit = SubmitField('Submit')


class SendItemsForm(FlaskForm):
    descr = StringField('Description', validators=[DataRequired()])
    card = StringField('Card No.', validators=[DataRequired()])
    requisit = StringField('Requisit No.', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    t_o = StringField('To', validators=[DataRequired()])
    out_put = IntegerField('Output', validators=[DataRequired(message="Please enter a valid number"),
                            NumberRange(min=0, message="Negative values are not accepted")])
    balance = IntegerField('Current Balance', validators=[DataRequired(message="Please enter a valid number"),
                            NumberRange(min=0, message="Balance cannot be negative")])
    
    submit = SubmitField('Submit')


class RequestResetForm(FlaskForm):
    email = StringField('Email Address', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')

    #Check if user already exist or not
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register first')
        
class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
