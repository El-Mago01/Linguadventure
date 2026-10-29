from flask import Blueprint, render_template
from data_manager import DataManager
import logging

from play.session import play_scene, Transcript

play = Blueprint("play", __name__)
dm = DataManager()

@play.route("/<user_id>/<adventure_id>/<scene_id>", methods=["GET"])
def scene_execution(user_id:int, adventure_id:int, scene_id:int):
    """
    The student has selected a specific scene that should be played. This route enables the playing of a specific scene.
    Using an LLM, the user is placed within a specific scenario where the student needs the language skills to get
    closer to the specific goal the student has. (e.g. knowing if some has found or seen his backpack).

    During the session, the transcript of both the student and the LLM is stored separately as text. At the end of
    the session, the student receives a wrap-up with feedback on the session. The details of the session as such
    is stored under a specific session_id.
    :param user_id:
    :param adventure_id:
    :param scene_id:
    :return:
    """
    print("scene_execution", user_id, adventure_id, scene_id)
    ai_conversation = play_scene(user_id, adventure_id, scene_id)
    print("ai_conversation: ", ai_conversation)
    return render_template("wrapup/session_wrapup.html")