from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class WebInput(FlaskForm):
	webAddress = StringField('Site Address', validators=[DataRequired()])
	submit = SubmitField('Start')

