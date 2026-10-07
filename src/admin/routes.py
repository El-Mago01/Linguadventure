from flask import Blueprint, render_template

admin = Blueprint("admin", __name__)


@admin.route("/<user_id>/adventure_admin", methods=["GET", "POST"])
def adventure_admin(user_id:int):
    """
    Upon request, the admin is presented with an adventure administration page where adventures can be added, changed,
    deleted, activated/deactivated etc. If the admin indicate to create a new adventure, he'll be redirected to a form
    where the new adventure can be shaped and added. For deletion, a confirmation is required.

    :param user_id:
    :return:
    """
    return render_template("adventure_admin.html")



@admin.route("/<user_id>/<adventure_id>/act_deact", methods=["POST"])
def act_deact_adventure(adventure_id:int):
    """
    The administrator decided to deactivate or activate an adventure
    :param adventure_id:
    :return:
    """
    return render_template("index.html")

@admin.route("/<user_id>/<adventure_id>/update'", methods=["GET", "POST"])
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