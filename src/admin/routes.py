"""
Method	    Route              	            Purpose
GET         /admin/adventure_admin/         open the adventure administrator adventure_admin.html
GET         /admin/adventures/new           Open new adventure editor new_adventure.html
GET         /admin/adventures/<id>/edit     Open existing adventure editor
GET	        /api/adventures 	            List adventures
GET	        /api/adventures/<id>	        Retrieve adventure including scenes
POST	    /api/adventures	                Create adventure
PUT	        /api/adventures/<id>	        Update complete adventure
PATCH	    /api/adventures/<id>	        Update activation status
DELETE	    /api/adventures/<id>	        Delete adventure
"""

from flask import Blueprint, render_template, request, abort, jsonify, url_for
from src.data_manager import DataManager as dm
from helper_functions import is_valid_email_address
from flask_login import  login_required, current_user
admin = Blueprint("admin", __name__)


"""
========================================================================================
=========****************** Adventure Administration ************************===========
========================================================================================
"""


@admin.route("/admin/adventure_admin/", methods=["GET"])
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
        abort(403, description="You are not authorized to access this page")
    email = current_user.email
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            print(student)
            adventures = dm.get_all_adventures()
            return render_template("/admin/adventure_admin.html", adventures=adventures, student=student)
            return render_template(url_for("admin.adventure_admin"), adventures=adventures, student=student)

    abort(404, description="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE


@admin.route("/admin/adventures/new", methods=["GET"])
@login_required
def add_adventure():
    """
    After the admin filled out a form to register a new adventure in the system, this function is called to
    ensure that this adventure is checked on validity and that it is added to the database.

    :param adventure:
    :return:
    """
    if not current_user.is_admin:
        abort(404, description="method not allowed by this user")
    email = current_user.email
    if is_valid_email_address(email):
        if dm.student_exists(email):
            student = dm.get_student(email)
            return render_template("admin/adventure_editor.html", student=student)
    abort(404, description="Invalid email address") #XXXX FIND THE RIGHT ERROR CODE


@admin.route("/api/adventures/", methods=["POST"])
@login_required
def create_adventure():
    """
    After the admin filled out a form to register a new adventure in the system, this function is called to
    ensure that this adventure is checked on validity and that it is added to the database. The adventure data
    is received in the request body as JSON.
    :param :
    :return:
    """
    if not current_user.is_admin:
        abort(403, message="You are not authorized to perform this action")
    if is_valid_email_address(current_user.email):
        adventure_data = request.get_json()
        adventure, message = dm.create_adventure(adventure_data, current_user.email)
        if adventure:
            return jsonify({
                "id": adventure.adventure_id,
                "message": f"Adventure saved successfully: {message}"
            }), 201
        else:
            return jsonify({
                "id": -1,
                "message": f"Could not save adventure due to internal issues: {message}"
            }),404
    abort(404, message="wrong email address used in session") #XXXX FIND THE RIGHT ERROR CODE


@admin.route("/api/adventures", methods=["GET"])
@login_required
def list_adventures():
    if not current_user.is_admin:
        abort(403)

    all_adventures = dm.get_all_adventures()
    serialized_adventures = [adventure.serialize() for adventure in all_adventures]
    return jsonify(serialized_adventures)


@admin.route("/api/adventure/<adventure_id>", methods=["PATCH"])
@login_required
def act_deact_adventure(adventure_id:int):
    """
    The administrator decided to deactivate or activate an adventure
    :param adventure_id:
    :return:
    """
    if not current_user.is_admin:
        act_deact = request.get_json()
    if not isinstance(adventure_id, int):
        return jsonify({"id": -1,
                "message": "wrong adventure_id received"
            }), 404
    adventure = dm.get_adventure(adventure_id)
    return jsonify({
                "id": adventure[0].adventure_id,
                "message": "Adventure saved successfully"
            }), 201


@admin.route("/api/adventure/<adventure_id>/'", methods=["PUT"])
@login_required
def update_adventure(adventure_id:int):
    """
    The admin indicated that an adventure needs an update. The admin first receive a pre-filled form (GET) where-after
    the admin can make the updates. After the submit button is pressed, the form is return to this route as POST message
    with the request to store the provided data in the DB.
    :param adventure_id:
    :param user_id:
    :return:
    """
    if not current_user.is_admin:
        abort(403)

    adventure_data = request.get_json()
    adventure = dm.update_persona(adventure_id, adventure_data)
    if adventure[0] is None:
        abort(404, message="Adventure not found")
    return jsonify({
        "id": adventure[0].adventure_id,
        "message": "Adventure updated successfully"
    }), 200
"""
========================================================================================
=========****************** Persona Administration **************************===========
========================================================================================
"""
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