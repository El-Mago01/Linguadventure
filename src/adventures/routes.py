from flask import Blueprint, render_template

adventures = Blueprint("adventures", __name__)


@adventures.route("/<user_id>/adventures", methods=["GET"])
def adventure_selection(user_id:int):
    """
    This page shows all the adventures available to the user, with image, little description, personas and level.
    The user can either start a new adventure from this screen or continue one that was already started
    :param user_id:
    :return:
    """
    return render_template("adventures.html")


@adventures.route("/<user_id>/<adventure_id>", methods=["GET"])
def show_adventure(user_id:int, adventure_id:int):
    """
    Shows the full overview of all scenes in this adventure, their progress and which scene is now to be done.
    :param user_id:
    :param adventure_id:
    :return:
    """
    return render_template("adventure_overview.html")

