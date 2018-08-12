import string
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from flask import render_template, request

from itertools import chain

from nltk.corpus import movie_reviews as mr
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier
import nltk

import requests

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os

from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
Bootstrap(app)

q = Queue(connection=conn)


def create_word_features(words):
    useful_words = [word for word in words if word not in stopwords.words("english")]
    my_dict = [(word, True) for word in useful_words]
    return my_dict


def loadNegativeReviews():
    neg_reviews = []
    for fileid in mr.fileids('neg')[:200]:
        words = mr.words(fileid)
        neg_reviews.append((create_word_features(words), "negative"))
        print(fileid)
    return neg_reviews


def loadPositiveReviews():
    pos_reviews = []
    for fileid in mr.fileids('pos')[:200]:
        words = mr.words(fileid)
        pos_reviews.append((create_word_features(words), "positive"))
        print(fileid)
    return pos_reviews


neg = loadNegativeReviews()
pos = loadPositiveReviews()

train_set = neg[:150] + pos[:150]
test_set = neg[150:] + pos[150:]

classifier = NaiveBayesClassifier.train(train_set)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    errors = []
    full_text = ""
    result = ""
    if request.method == "POST":
        url = request.form['url']
        job = q.enqueue_call(func=getUrlFromSite, args=(url,), result_ttl=5000)
        print(job.get_id())
        while result == "":
            result = getResults(job.get_id())
        return render_template('index.html', errors=errors)
    return render_template('index.html', errors=errors, full_text=full_text, result=result)


def getResults(job_key):
    job = Job.fetch(job_key, connection=conn)
    if job.is_finished:
        return str(job.result), 200
    else:
        return "", 202


def getUrlFromSite(url):
    errors = []
    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    text = sentimentAnalysis(r)
    sentiment, certainty = getPrediction(text)
    result = "Prediction: " + sentiment + certainty
    return result


def convertToSentenceArray(paragraph):
    sentences = []
    while paragraph.find('.') != -1:
        index = paragraph.find('.')
        sentences.append(paragraph[:index + 1])
        paragraph = paragraph[index + 1:]
    return sentences


def sentimentAnalysis(siteUrl):
    soup = BeautifulSoup(siteUrl.text, 'html.parser')
    [s.extract() for s in soup(['script', 'style', 'meta', 'link', 'class', 'a', 'span', 'link', 'li'])]
    visible_text = soup.getText()
    return visible_text


def getAccuracy():
    return nltk.classify.accuracy(classifier, train_set)


def getPrediction(text):
    accuracy = getAccuracy(classifier) * 100
    sentiment = classifier.classify(text)

    return sentiment, accuracy


if __name__ == '__main__':
    app.run()
