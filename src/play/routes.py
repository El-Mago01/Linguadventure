from flask import Blueprint, render_template

play = Blueprint("play", __name__)


@play.route("/<user_id>/<adventure_id>/<scene_id>", methods=["GET"])
def scene_execution(user_id:int, aventure_id:int, scene_id:int):
    """
    The student has selected a specific scene that should be played. This route enables the playing of a specific scene.
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