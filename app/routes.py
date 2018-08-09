from flask import render_template, flash
from app import app
from app.forms import WebInput

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])

def index():
	form = WebInput()
	if form.validate_on_submit():
		flash('Running Sentiment Analysis')

	return render_template('index.html', title = 'Home', form=form)

