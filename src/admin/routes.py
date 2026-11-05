from flask import Blueprint, render_template, request, abort, jsonify
from src.data_manager import DataManager as dm
from helper_functions import is_valid_email_address
from flask_login import  login_required, current_user
admin = Blueprint("admin", __name__)


@admin.route("/adventure_admin/", methods=["GET"])
@login_required
def adventure_admin():
    """
    Upon request, the admin is presented with an adventure administration page where adventures can be added, changed,
    deleted, activated/deactivated etc. If the admin indicate to create a new adventure, he'll be redirected to a form
    where the new adventure can be shaped and added. For deletion, a confirmation is required.

    :param user_id:
    :return:
    """
    if not current_user.is_admin:
        abort(403, message="You are not authorized to access this page")
    email = current_user.email
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            print(student)
            adventures = dm.get_all_adventures()
            return render_template("admin/adventure_admin.html", adventures=adventures, student=student)

    abort(404, message="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE


@admin.route("/admin/adventures/new", methods=["POST"])
@login_required
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
@login_required
def act_deact_adventure(adventure_id:int):
    """
    The administrator decided to deactivate or activate an adventure
    :param adventure_id:
    :return:
    """
    return render_template("index.html")

@admin.route("/adventure_admin/update/<user_id>/<adventure_id>/'", methods=["GET", "POST"])
@login_required
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

@admin.route("/admin/personas/new", methods=["GET","POST"])
@login_required
def create_persona():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        persona_data = request.get_json()

        persona, result = dm.create_persona(persona_data)

        return jsonify({
            "id": persona.persona_id,
            "message": "Persona saved successfully"
        }), 201
    else:
        return render_template("admin/persona_admin.html")


@admin.route("/api/personas", methods=["GET"])
@login_required
def list_personas():
    if not current_user.is_admin:
        abort(403)

    all_personas = dm.get_all_personas()
    serialized_personas = [persona.serialize() for persona in all_personas]
    return jsonify(serialized_personas)

@admin.route("/api/personas/<int:persona_id>", methods=["PUT"])
@login_required
def update_persona(persona_id:int):
    if not current_user.is_admin:
        abort(403)

    persona_data = request.get_json()
    persona = dm.update_persona(persona_id, persona_data)
    if persona is None:
        abort(404, message="Persona not found")
    return jsonify({
        "id": persona.persona_id,
        "message": "Persona updated successfully"
    }), 200

@admin.route("/api/personas/<int:persona_id>", methods=["DELETE"])
@login_required
def delete_persona(persona_id:int):
    if not current_user.is_admin:
        abort(403)


    persona = dm.delete_persona(persona_id)
    if persona is None:
        abort(404, message="Persona not found")
    return jsonify({
        "id": persona.persona_id,
        "message": "Persona updated successfully"
    }), 200