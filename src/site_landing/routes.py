from flask import Blueprint, render_template, request

site_landing = Blueprint("site_landing", __name__, static_folder="static", template_folder="../templates")

@site_landing.route("/", methods=["GET"])
def index():
    """
    A landing on this route will ask the user to either log on or register as a new student.
    For loging on, the user will need to provide her/his email address and click the logon button.
    :return:
    """
    return render_template("site_landing/index.html")


@site_landing.route("/login", methods=["GET", "POST"])
def login():
    """
    After the user provided her/his email address and clicked login, this route is activated.
    If the provided email address is registered, the user is forwarded to the user_home, with all
    relevant information about progress on adventures take and a possibility to select a new adventure
    or continue an ongoing one.
    :return:
    """
    return render_template("user_home.html")

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
    email = request.form.get("email")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    print(email, first_name, last_name)
    return render_template("site_landing/user_home.html")

@site_landing.route("/<new_user>/confirm_registration", methods=["POST"])
def confirm_registration(new_user:int):
    """
    After the new student registered with email address, the student receives a confirmation email with a link.
    Clicking on this link this route is activated and the registration status is changed to confirmed.
    :param new_user:
    :return:
    """
    return render_template("index.html")


@site_landing.route("/<user_id>", methods=["POST"])
def user_home(user_id:int):
    """
    A confirmed registered student will gain access via this route to the students home page
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@site_landing.route("/<user_id>/profile", methods=["GET"])
def view_profile(user_id:int):
    """
    Student gets the possibility to view her/his profile page and the possibility to click change profile.
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@site_landing.route("/<user_id>/update_profile", methods=["POST"])
def update_profile(user_id:int):
    """
    The student or admin can change the items in the profile (e.g. profession, email-address etc)
    :param user_id:
    :return:
    """
    return render_template("user_home.html")


@site_landing.route("/<user_id>/delete", methods=["POST"])
def delete_profile(user_id:int):
    """
    In case the user wants to de-register her/him-self. Or in case an admin chooses to de-register a student.
    All progress is lost
    :param user_id:
    :return:
    """
    return render_template("index.html")
