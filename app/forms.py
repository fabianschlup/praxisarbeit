from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User

# Übernommen aus den Beispielen von Miguel Grinberg
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Übernommen aus den Beispielen von Miguel Grinberg
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Übernommen aus den Beispielen von Miguel Grinberg
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

# Eigenentwicklung
class TodoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired(), Length(min=1, max=140)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('todo', 'To Do'), ('inprogress', 'In Progress'), ('done', 'Done')], validators=[DataRequired()])
    assigned_to = SelectField('Assigned To', coerce=int)
    submit = SubmitField('Submit')

# Eigenentwicklung
class EditTodoStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('todo', 'To Do'), ('inprogress', 'In Progress'), ('done', 'Done')], validators=[DataRequired()])

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# Übernommen aus den Beispielen von Miguel Grinberg
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Submit')
