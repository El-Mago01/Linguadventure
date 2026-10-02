"""
This module handles all user requests. It outsourced all the data handling to the data_manager,
which creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes care of the fulfillment
of these requests by using the partners models and movie_data_fetcher.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, abort, flash
from data_manager import DataManager, db, logging

dm = DataManager()
app = Flask(__name__, template_folder="../templates")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, '../data/linguadventure.sqlite')}"
)
db.init_app(app)

load_dotenv()  # Load environment variables from .env file
app.secret_key = os.getenv("OPENAI_API_KEY")

with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def home():
    """
    A landing on this route will ask the user to either log on or register as a new student.
    For loging on, the user will need to provide her/his email address and click the logon button.
    :return:
    """
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    """
    After the user provided her/his email address and clicked login, this route is activated.
    If the provided email address is registered, the user is forwarded to the user_home, with all
    relevant information about progress on adventures take and a possibility to select a new adventure
    or continue an ongoing one.
    :return:
    """
    return render_template("user_home.html")


@app.route("/<new_user>/confirm_registration", methods=["POST"])
def confirm_registration(new_user:int):
    """
    After the new student registered with email address, the student receives a confirmation email with a link.
    Clicking on this link this route is activated and the registration status is changed to confirmed.
    :param new_user:
    :return:
    """
    return render_template("index.html")


@app.route("/<user_id>", methods=["POST"])
def user_home(user_id:int):
    """
    A confirmed registered student will gain access via this route to the students home page
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@app.route("/<user_id>/profile", methods=["GET"])
def view_profile(user_id:int):
    """
    Student gets the possibility to view her/his profile page and the possibility to click change profile.
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@app.route("/<user_id>/update_profile", methods=["POST"])
def update_profile(user_id:int):
    """
    The student or admin can change the items in the profile (e.g. profession, email-address etc)
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@app.route("/<user_id>/delete", methods=["POST"])
def delete_profile(user_id:int):
    """
    In case the user wants to de-register her/him-self. Or in case an admin chooses to de-register a student.
    All progress is lost
    :param user_id:
    :return:
    """
    return render_template("index.html")

@app.route("/<user_id>/adventures", methods=["GET"])
def adventure_selection(user_id:int):
    """
    This page shows all the adventures available to the user, with image, little description, personas and level.
    The user can either start a new adventure from this screen or continue one that was already started
    :param user_id:
    :return:
    """
    return render_template("adventures.html")



@app.route("/<user_id>/<adventure_id>", methods=["GET"])
def update__profile(user_id:int, adventure_id:int):
    """
    Shows the full overview of all scenes in this adventure, their progress and which scene is now to be done.
    :param user_id:
    :param adventure_id:
    :return:
    """
    return render_template("adventure_overview.html")


@app.route("/<user_id>/<adventure_id>/<scene_id>", methods=["GET"])
def start_session(user_id:int, aventure_id:int, scene_id:int):
    """
    The student has selected a specific scene that shall be run. This route enables the running of a specific scene.
    Using an LLM, the user is placed within a specific scenario where the student needs the language skills to get
    closer to the specific goal the student has. (e.g. knowing if some has found or seen his backpack).

    During the session, the transcript of both the student and the LLM is stored separately as text. At the end of
    the session, the student receives a wrap-up with feedback on the session. The details of the session as such
    is stored under a specific session_id.
    :param user_id:
    :param aventure_id:
    :param scene_id:
    :return:
    """
    return render_template("session_handling.html")


@app.route("/<user_id>/<adventure_id>/<scene_id>/<session_id>", methods=["POST"])
def scene_execution(user_id:int, adventure_id:int, scene_id:int, session_id:int):
    return render_template("scene_execution.html")


@app.route("/run_scene/all_users", methods=["GET"])
def all_users(user_id:int):
    return render_template("user_admin.html")


@app.route("/<adventure_id>/act_deact", methods=["POST"])
def act_deact_adventure(adventure_id:int):
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

