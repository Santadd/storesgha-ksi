from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, DataRequired


class AddItemsForm(FlaskForm):
    descr = StringField('Description', validators=[DataRequired()])
    card = StringField('Card No.', validators=[DataRequired()])
    usrv = StringField('U.S.R.V & W.B', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    fr_om = StringField('From', validators=[DataRequired()])
    inp_ut = IntegerField('Input', validators=[InputRequired(), NumberRange(min=1)])
    balance = IntegerField('Balance', validators=[InputRequired(),NumberRange(min=0)])
    cedis = IntegerField('Cedis', validators=[InputRequired(),NumberRange(min=1)])
    pesewas = IntegerField('Pesewas', validators=[InputRequired(),NumberRange(min=0)]) 
    
    submit = SubmitField('Submit')

    

class SendItemsForm(FlaskForm):
    descr = StringField('Description', validators=[DataRequired()])
    card = StringField('Card No.', validators=[DataRequired()])
    requisit = StringField('S.I.V', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    t_o = StringField('To', validators=[DataRequired()])
    out_put = IntegerField('Out', validators=[InputRequired(), NumberRange(min=1)])
    balance = IntegerField('Current Balance', validators=[InputRequired(), NumberRange(min=0)])
    
    submit = SubmitField('Submit')
