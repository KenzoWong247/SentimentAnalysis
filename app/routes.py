from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from flask import render_template, request
from app import app
import requests

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])

def index():
	errors = []
	full_text = []
	results = ""
	if request.method == "POST":
		# get url that the person has entered
		try:
			url = request.form['url']
			r = requests.get(url)
		except:
			errors.append(
				"Unable to get URL. Please make sure it's valid and try again."
			)
			return render_template('index.html', errors=errors)
		if r:
			text = sentimentAnalysis(r)
			full_text = convertToSentenceArray(text)
	return render_template('index.html', errors=errors, results=full_text)

def convertToSentenceArray(paragraph):
	sentences = []
	while paragraph.find('.') != -1:
		index = paragraph.find('.')
		sentences.append(paragraph[:index + 1])
		paragraph = paragraph[index+1:]
	return sentences

def sentimentAnalysis(siteUrl):
	soup = BeautifulSoup(siteUrl.text, 'html.parser')
	[s.extract() for s in soup(['script', 'style', 'meta', 'link', 'class', 'a', 'span', 'link', 'li'])]
	visible_text = soup.getText()
	return visible_text