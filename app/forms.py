from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = StringField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = StringField('Password: ', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    query = StringField('Search: ', validators=[DataRequired()])
    search_type = SelectField('Search Type: ', choices=[('library', 'Library'), ('rutracker', 'RuTracker')])
    submit = SubmitField('Submit')
