from flask import Blueprint, render_template

wrapup = Blueprint("wrapup", __name__)


@wrapup.route("/<user_id>/<adventure_id>/<scene_id>/<session_id>", methods=["POST"])
def session_evaluation(user_id:int, adventure_id:int, scene_id:int, session_id:int):
    """
    The data that was stored during the session is evaluated here and a feedback is provided to the user and documented
    :param user_id:
    :param adventure_id:
    :param scene_id:
    :param session_id:
    :return:
    """
    return render_template("scene_execution.html")