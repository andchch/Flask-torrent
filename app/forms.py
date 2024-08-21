from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    """
    Форма регистрации пользователя

    Attributes:
        username (StringField): The username field, required.
        password (StringField): The password field, required.
        submit (SubmitField): The submit button.
    """
    username = StringField('Username: ', validators=[DataRequired()])
    password = StringField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    """
    Форма авторизации пользователя

    Attributes:
        username (StringField): The username field, required.
        password (StringField): The password field, required.
        remember (BooleanField): The remember me checkbox.
        submit (SubmitField): The submit button.
    """
    username = StringField('Username: ', validators=[DataRequired()])
    password = StringField('Password: ', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    """
    Форма для поиска книг

    Attributes:
        query (StringField): The search query field, required.
        search_type (SelectField): The search type dropdown with options for library and RuTracker.
        submit (SubmitField): The submit button.
    """
    query = StringField('Search: ', validators=[DataRequired()])
    search_type = SelectField('Search Type: ', choices=[('library', 'Library'), ('rutracker', 'RuTracker')])
    submit = SubmitField('Submit')
