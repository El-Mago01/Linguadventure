"""
Endpoint	                                    Frontend responsibility
GET /play/<adventure_id>/<scene_id>             render the scene_player.html
PUT /api/play_scene/<adventure_id>/<scene_id>	Submit a student turn and receive the persona's response
GET /api/student_adventures	                    Populate the Continue Adventure section
GET /api/all_adventures	                        Populate the Discover Adventures section
GET /api/learning_journey	                    Populate progress and learning insights on student_home.html
GET /api/play_scene/<adventure_id>/<scene_id>   Retrieve the scene context, persona information, vocabulary,
                                                grammar tips, and existing conversation when resuming.
"""

from data_manager import DataManager
import logging

from flask import Blueprint, render_template, request, abort, jsonify, url_for, redirect, flash
from src.data_manager import DataManager as dm
from flask_login import  login_required, current_user


play = Blueprint("play", __name__)


@play.route("/api/all_adventures", methods=["GET"])
@login_required
def all_adventures():
    if not current_user.is_active:
        return jsonify({"id": -1,
                        "message": "User not active."
                        }), 404
    all_the_adventures = dm.get_all_adventures()
    return jsonify(all_the_adventures)


@play.route("/api/all_student_adventures", methods=["GET"])
@login_required
def all_student_adventures():
    if not current_user.is_active:

        return jsonify({"id": -1,
                        "message": "User not active."
                        }), 404
    student_adventures = dm.get_all_student_adventures(current_user.student_id)
    return jsonify(student_adventures)


@play.route("/start_adventure/<int:adventure_id>", methods=["GET"])
@login_required
def start_adventure(adventure_id:int):
    """
    Method	Endpoint	        Purpose
    GET	    /api/play_scene/2/3	Retrieve scene, persona, and existing conversation
    PUT	    /api/play_scene/2/3	Submit a typed or recorded message
    PUT	    /api/play_scene/2/3	Finish the scene and request feedback
    """
    if not current_user.is_active:
        flash("Can't roll the adventure. Student is not active", "login_error")
        return redirect(url_for("site_landing.login"))

    this_student_adventure, reason = dm.reserve_adventure(adventure_id, current_user.student_id)
    if this_student_adventure is None or len(this_student_adventure) < 1:
        flash(f"Can not reserve the adventure for this student. {reason}")
        return redirect(url_for("site_landing.student_home"))

    student_adventure_status, result = dm.get_full_student_adventure_data(adventure_id, current_user.student_id)

    # Your DataManager retrieves this
    print(f"student_adventure_status: {student_adventure_status}")
    print(type(student_adventure_status))
    if student_adventure_status is None or len(student_adventure_status) < 1:
        flash(f"Can not retrieve the adventure status for this student. {result}")
        return redirect(url_for("site_landing.student_home"))
    return render_template(
        "play/adventure_start.html",
        student_adventure_status=student_adventure_status
    )

@play.route("/play_scene/<adventure_id>/<scene_id>", methods=["GET"])
def play_scene(adventure_id: int, scene_id: int):
    if not current_user.is_active:
        flash("You need to be logged in to play a scene.")
        return redirect(url_for("site_landing.login"))
    return render_template("play/scene_player.html")

@play.route("/api/play_scene/<int:adventure_id>/<int:scene_id>", methods=["GET"])
def scene_execution(adventure_id:int, scene_id:int):
    """
    Fields used by the player:
    Field	                Required?	        Usage
    scene.title	            Recommended	        Scene heading
    scene.intro	            Recommended	        Story introduction
    scene.goal	            Recommended	        Student's mission
    scene.vocabulary	    Optional	        Vocabulary panel
    scene.grammar	        Optional	        Grammar panel
    scene.location	        Optional	        Location
    scene.scene_order_nr	Optional	        Scene number
    persona.name	        Recommended	        Character name
    persona.role	        Optional	        Character description
    persona.portrait_url	Optional	        Character image
    can_play	            Recommended	        Whether the student is allowed to enter
    :param adventure_id:
    :param scene_id:
    :return:
    Example:
    {
      "adventure": {
        "title": "The Lost Backpack"
      },
      "can_play": true,
      "scene": {
        "scene_id": 2,
        "scene_order_nr": 1,
        "title": "The Café",
        "location": "Rossio, Lisbon",
        "intro": "You enter a small café. Miguel is behind the counter.",
        "goal": "Discover who took your backpack.",
        "vocabulary": "mochila, mesa, perder",
        "grammar": "você viu; eu vi"
      },
      "persona": {
        "name": "Miguel",
        "role": "Café owner",
        "portrait_url": "/static/personas/miguel.png"
      }
    }
    """
    if not current_user.is_active:
        return jsonify({
            "message": "You need to be logged in to play a scene"
        }), 403

    print(f"adventure_id: {adventure_id}, type: {type(adventure_id)} scene_id: {scene_id}, type: {type(scene_id)}")
    adventure_info, result = dm.get_full_student_adventure_data(adventure_id, current_user.student_id)
    if adventure_info is None or len(adventure_info) < 1:
        return jsonify({
            "message": f"Can not retrieve the scene information for this student. {result}"
        }), 403
    scenes=adventure_info["scenes"]
    if not isinstance(scenes, list) or len(scenes) < 1:
        return jsonify({
            "message": f"Can not retrieve the scene information for this adventure. {result}"
        }), 403

    # Derive the required information for the scene player
    this_scene = {}
    for scene in scenes:
        if scene.get("scene_id", -1) == scene_id:
            this_scene = scene
            break
    if this_scene is None or len(this_scene) == 0:
        return jsonify({
            "message": f"Can not retrieve the scene information for this adventure. {result}"
        }), 403
    can_play = this_scene.get("can_play", False)
    scene_info = {
        "adventure" : {
            "adventure_id" : adventure_id,
            "title" : adventure_info["title"]
        },
        "scene": this_scene,
        "can_play": can_play,
        "persona": this_scene.get("persona", None)

    }
    return jsonify(scene_info), 200


@play.route("/api/play_scene/<int:adventure_id>/<int:scene_id>", methods=["PUT"])
def receive_chat(adventure_id:int, scene_id:int):
    """
    Chat message received from the student in the form of:
    {
        "message" : "<the message>"
    }
    Expected response:
    {
      "student_turn": {
        "role": "student",
        "text": "Bom dia, você viu a minha mochila?"
      },
      "persona_turn": {
        "role": "persona",
        "text": "Bom dia! Sim, vi uma mochila preta.",
        "audio_url": "/static/audio/response123.mp3"
      },
      "scene_finished": false
    }
    """
    if not current_user.is_active:
        return jsonify({
            "message": "You need to be logged in to play a scene."
        }), 403
    print("Received chat message for adventure_id:", adventure_id, "scene_id:", scene_id)
    chat_data = request.get_json()
    print("Received chat data:", chat_data.get("message", ""))

    answer = {
        "student_turn": {
            "role": "student",
            "text": chat_data.get("message", "")
        },
        "persona_turn": {
            "role": "persona",
            "text": "Bom dia! Sim, vi uma mochila preta.",
            "audio_url": ""
        },
        "scene_finished": True
    }
    return jsonify(answer), 200


@play.route("/api/play_scene/<int:adventure_id>/<int:scene_id>/complete", methods=["POST"])
def complete_session(adventure_id:int, scene_id:int):
    """
    Ëxpected response:
    {
      "status": "completed",
      "feedback": {
        "summary": "Well done! You discovered the next clue.",
        "goal_achieved": true,
        "score": 82,
        "strengths": ["Good vocabulary usage"],
        "improvements": ["Practice past tense"]
      },
      "next_scene_id": 3
    }
    """
    if not current_user.is_active:
        return jsonify({
            "message": "You need to be logged in to finalize a scene."
        }), 403
    answer = {
      "status": "completed",
      "feedback": {
        "summary": "Well done! You discovered the next clue.",
        "goal_achieved": True,
        "score": 82,
        "strengths": ["Good vocabulary usage"],
        "improvements": ["Practice past tense"]
      },
      "next_scene_id": 3
    }
    return jsonify(answer), 200