"""
This module handles all user requests. It outsourced all the data handling to the data_manager,
which creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes care of the fulfillment
of these requests by using the partners models and movie_data_fetcher.

Important clarification. The jargon in this application distinguishes 3 types of 'users':
1. USER: An entity that is not yet registered, or did not yet logged-on to the system
2. STUDENT: An entity that has a valid profile stored in the system and logged-on
3. ADMIN: An entity that has a valid profile which has "is_admin" set as True, and logged-on
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template
from data_manager import DataManager, db
from src.site_landing import site_landing
from src.adventures import adventures
from src.admin import admin
from src.play import play
from src.learning import learning
from src.wrapup import wrapup


dm = DataManager()
def create_app(database_uri=None):
    """
    This turns the app creation into an app-factory. E.g. For testing you'd like to use a different database
    then for a production environment. Therefor, using create_app("sqlite:///test_db.db") will create a specific
    db for testing only, separated from the default production environment.
    :param database_uri:
    :return:
    """
    this_app = Flask(__name__, template_folder="../templates")
    if database_uri:
        this_app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    else:
        this_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../../data/linguadventure.sqlite"
    print("DB inside create_app:", id(db))

    db.init_app(this_app)
    # Blueprints
    this_app.register_blueprint(site_landing)
    # this_app.register_blueprint(site_landing, url_prefix="/user")

    this_app.register_blueprint(adventures)
    this_app.register_blueprint(play)
    this_app.register_blueprint(wrapup)
    this_app.register_blueprint(learning)
    this_app.register_blueprint(admin)

    return this_app

app = create_app()
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()  # Load environment variables from .env file
app.secret_key = os.getenv("OPENAI_API_KEY")

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

