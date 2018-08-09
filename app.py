
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from flask import render_template, request

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

import requests

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

# How Naive Bayes classifier accepts input
def create_word_features(words):
    useful_words = [word for word in words if word not in stopwords.words("english")]
    my_dict = [(word, True) for word in useful_words]
    return my_dict


def loadNegativeReviews():
    neg_reviews = []
    reviews = []
    for fileid in movie_reviews.fileids('neg'):
        print(fileid)
        words = movie_reviews.words(fileid)
        reviews.append(words)
    for review in reviews:
        neg_reviews.append((create_word_features(review), "negative"))
    return neg_reviews


def loadPositiveReviews():
    pos_reviews = []
    reviews = []
    for fileid in movie_reviews.fileids('pos'):
        words = movie_reviews.words(fileid)
        reviews.append(words)
    for review in reviews:
        pos_reviews.append((create_word_features(review), "positive"))
    return pos_reviews


neg = loadNegativeReviews()
pos = loadPositiveReviews()

train_set = neg[:200] + pos[200:]
test_set = neg[200:] + pos[:200]

classifier = NaiveBayesClassifier.train(train_set)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    errors = []
    full_text = ""
    result = ""
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
            sentiment, certainty = getPrediction(text)
            result = "Prediction: " + sentiment + certainty

    return render_template('index.html', errors=errors, full_text=full_text, result=result)


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


def getAccuracy(train_set):
    return nltk.classif.util.accuracy(train_set)


def getPrediction(text, classifier):
    accuracy = getAccuracy(classifier, text) * 100
    sentiment = classifier.classify(text)

    return sentiment, accuracy



if __name__ == '__main__':
    app.run()

