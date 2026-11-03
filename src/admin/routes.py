from flask import Blueprint, render_template, request, abort
from src.data_manager import DataManager as dm, DataManager
from helper_functions import is_valid_email_address
from flask_login import login_required

admin = Blueprint("admin", __name__)

dm=DataManager()

@admin.route("/adventure_admin/", methods=["POST"])
def adventure_admin():
    """
    Upon request, the admin is presented with an adventure administration page where adventures can be added, changed,
    deleted, activated/deactivated etc. If the admin indicate to create a new adventure, he'll be redirected to a form
    where the new adventure can be shaped and added. For deletion, a confirmation is required.

    :param user_id:
    :return:
    """
    email = request.form.get("email","")
    print(email)
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            print(student)
            adventures = dm.get_all_adventures()
            return render_template("admin/adventure_admin.html", adventures=adventures, student=student)

    abort(404, message="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE

@admin.route("/admin/adventures/new", methods=["POST"])
def add_adventure():
    """
    After the admin filled out a form to register a new adventure in the system, this function is called to
    ensure that this adventure is checked on validity and that it is added to the database.

    :param adventure:
    :return:
    """
    print("add_adventure")
    email = request.form.get("email","")
    print(email)
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            print(student)
            return render_template("admin/new_adventure.html", student=student)

    abort(404, message="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE

@admin.route("/adventure_admin/act_deact/<user_id>/<adventure_id>/", methods=["POST"])
def act_deact_adventure(adventure_id:int):
    """
    The administrator decided to deactivate or activate an adventure
    :param adventure_id:
    :return:
    """
    return render_template("index.html")

@admin.route("/adventure_admin/update/<user_id>/<adventure_id>/'", methods=["GET", "POST"])
def update_adventure(user_id:int, adventure_id:int):
    """
    The admin indicated that an adventure needs an update. The admin first receive a pre-filled form (GET) where-after
    the admin can make the updates. After the submit button is pressed, the form is return to this route as POST message
    with the request to store the provided data in the DB.
    :param adventure_id:
    :param user_id:
    :return:
    """
    return render_template("index.html")

@admin.route("/admin/persona_admin", methods=["POST"])
@login_required
def persona_admin():
    """
    After the admin filled out a form to register a new adventure in the system, this function is called to
    ensure that this adventure is checked on validity and that it is added to the database.

    :param adventure:
    :return:
    """
    print("persona_admin")
    email = request.form.get("email","")
    print(email)
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            print(student)
            return render_template("admin/persona_admin.html", student=student)

    abort(404, message="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE