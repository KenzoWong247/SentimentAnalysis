from sklearn.feature_extraction.text import CountVectorizer
data = []
data_labels = []
with open("./pos_tweets.txt") as f:
    for i in f: 
        data.append(i) 
        data_labels.append('pos')
 
with open("./neg_tweets.txt") as f:
    for i in f: 
        data.append(i)
        data_labels.append('neg')
vectorizer = CountVectorizer(
    analyzer = 'word',
    lowercase = False,
)
features = vectorizer.fit_transform(
    data
)
features_nd = features.toarray()
from sklearn.cross_validation import train_test_split
 
X_train, X_test, y_train, y_test  = train_test_split(features_nd, data_labels, train_size=.96, random_state=1234)

from sklearn.linear_model import LogisticRegression
log_model = LogisticRegression()
log_model = log_model.fit(X_train, y_train)
y_pred = log_model.predict(X_test)

from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, y_pred))
