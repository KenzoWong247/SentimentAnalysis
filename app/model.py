from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    classifier = db.Column(JSON)

    def __init__(self, classifier):
        self.classifier = classifier

    def __repr__(self):
        return '<id {}>'.format(self.id)
