from flask import Flask
from flask_bootstrap import Bootstrap
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

from app import routes

