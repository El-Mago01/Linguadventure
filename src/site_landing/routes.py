from flask import Blueprint, render_template, request, abort
from src.data_manager import DataManager, StudentStorageError
from helper_functions import is_valid_email_address, check_admin_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import Student


site_landing = Blueprint("site_landing", __name__, static_folder="static", template_folder="../templates")
dm = DataManager()
@site_landing.route("/", methods=["GET"])
def index():
    """
    A landing on this route will ask the user to either log on or register as a new student.
    For loging on, the user will need to provide her/his email address and click the logon button.
    :return:
    """
    return render_template("site_landing/index.html", app_name="LinguAdventure")


@site_landing.route("/login", methods=["GET", "POST"])
def login():
    """
    After the user provided her/his email address and clicked login, this route is activated.
    If the provided email address is registered, the user is forwarded to the user_home, with all
    relevant information about progress on adventures take and a possibility to select a new adventure
    or continue an ongoing one.
    :return:
    """

    email = request.form.get("email", "").strip().lower()
    if not is_valid_email_address(email) or not dm.student_exists(email):
        flash("received email is not valid", "login_error")
        return redirect(url_for("site_landing.index"))
    password = request.form.get("password", "")
    student = dm.get_student_object(email)

    if (
            student is None
            or not student.password_hash
            or not check_password_hash(student.password_hash, password)
    ):
        flash("Invalid email address or password.", "login_error")
        return redirect(url_for("site_landing.index"))

    if not student.is_active:
        flash("This account is inactive.", "login_error")
        return redirect(url_for("site_landing.index"))
    login_user(student)
    print(student)

    return render_template("site_landing/user_home.html", student=student)

@site_landing.route("/register", methods=["GET","POST"])
def register():
    """
    When the user clicks to register , the user get's a form. This request is received as a GET request.
    As a result, the user will receive the registration form.

    After the user filled the form this route is activated with a POST request. The received data is analyzed and
    if all is ok, the entry is stored in the DB.
    :return:
    """
    if request.method == "GET":
        return render_template("site_landing/registration.html")
    email = request.form.get("email","")
    if not is_valid_email_address(email):
        return render_template("site_landing/registration.html", message="Invalid email address")
    password = request.form.get("password", "")

    if not password:
        return render_template("site_landing/registration.html", message="Password is required")
    if len(password) < 8 or len(password) > 128:
        return render_template("site_landing/registration.html", message="Password must be between 12 and 128 characters")

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    new_student = {}
    new_student["password_hash"] = generate_password_hash(password)
    new_student["first_name"] = first_name
    new_student["last_name"] = last_name
    new_student["email"] = email
    new_student["target_language"] = request.form.get("target_language")
    new_student["original_language"] = request.form.get("original_language")
    new_student["age"] = request.form.get("age")
    new_student["gender"] = request.form.get("gender")
    new_student["occupation"] = request.form.get("occupation")
    new_student["current_level"] = request.form.get("current_level")
    if check_admin_user(email,at_registration=True):
        new_student["is_admin"] = True
    try:
        stored_student = dm.add_student(new_student)
    except StudentStorageError as e:
        return render_template("site_landing/registration.html", message=str(e))
    login_user(stored_student)
    return render_template("site_landing/user_home.html", student=stored_student)

@site_landing.route("/logout", methods=["POST"])
@login_required
def logout():

    """
    After the user clicked logout, this route is activated and the flash is contact to release this user.
    logout_user() removes the Flask-Login authentication information from the session
    :return:
    """

    logout_user()
    return redirect(url_for("site_landing.index"))


@site_landing.route("/<user_id>", methods=["POST"])
def user_home(user_id:int):
    """
    A confirmed registered student will gain access via this route to the students home page
    :param user_id:
    :return:
    """
    return render_template("site_landing/user_home.html")


@site_landing.route("/view_profile/<user_id>", methods=["GET"])
def view_profile(user_id:int):
    """
    Student gets the possibility to view her/his profile page and the possibility to click change profile.
    :param user_id:
    :return:
    """
    return render_template("site_landing/user_home.html")


@site_landing.route("/update_profile/<user_id>", methods=["POST"])
def update_profile(user_id:int):
    """
    The student or admin can change the items in the profile (e.g. profession, email-address etc)
    :param user_id:
    :return:
    """
    return render_template("site_landing/user_home.html")


@site_landing.route("/delete_user/<int:user_id>/", methods=["DELETE"])
def delete_profile(user_id:int):
    """
    In case the user wants to de-register her/him-self. Or in case an admin chooses to de-register a student.
    All progress is lost
    :param user_id:
    :return:
    """

    if not isinstance(user_id, int):
        abort(400)

    if user_id < 0:
        abort(404)

    dm.delete_student(user_id)
    return render_template("site_landing/index.html")
