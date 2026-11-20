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

from uuid import uuid4
from src.play.session import get_persona_reply, State, dm
import logging

from flask import Blueprint, render_template, request, abort, jsonify, url_for, redirect, flash, session
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

    When the student selected an adventure to work on, it will receive a screen where it will be able
    to select a scene to play. Scenes might be enabled or locked. If locked, it can be played. An earlier
    session needs to be played first to unlock the current one. The data forwarded to FE includes the
    scenes and their availability (locked/unlocked) which is then displayed to the student

    The following steps are done to prepare the data to be provided to this screen:
    1. check if the student logged on and if the student is active
    2. reserve the adventure for the student by creating a new entry in the student_adventure table with an initial
       status_code, enabling the first scene on the list
    3. fetch all the available adventure data including the scenes
    4. set the values for fields "completed" and "unlocked. These fields are used for the FE to determine which
       scenes are available for the student.
    """
    if not current_user.is_active:
        flash("Can't roll the adventure. Student is not active", "login_error")
        return redirect(url_for("site_landing.login"))

    this_student_adventure, reason = dm.reserve_adventure(adventure_id, current_user.student_id)
    if this_student_adventure is None or len(this_student_adventure) < 1:
        flash(f"Can not reserve the adventure for this student. {reason}")
        return redirect(url_for("site_landing.student_home"))

    student_adventure_data, result = dm.get_full_student_adventure_data(adventure_id, current_user.student_id)

    print(f"student_adventure_status: {student_adventure_data}")
    print(type(student_adventure_data))
    if student_adventure_data is None or len(student_adventure_data) < 1:
        flash(f"Can not retrieve the adventure status for this student. {result}")
        return redirect(url_for("site_landing.student_home"))
    if "scenes" not in student_adventure_data:
        flash(f"Can not retrieve the scenes status for this student. {result}")
        return redirect(url_for("site_landing.student_home"))
    scenes = student_adventure_data["scenes"]
    for index in range(len(scenes)):
        scene_id = scenes[index].get("scene_id",-1)
        if not dm.get_scene_status(adventure_id, scene_id, current_user.student_id):
            student_adventure_data["scenes"][index]["completed"] = False
            student_adventure_data["scenes"][index]["unlocked"] = False
            if index == 0:
                student_adventure_data["scenes"][index]["unlocked"] = True

    return render_template(
        "play/adventure_start.html",
        student_adventure_status=student_adventure_data
    )


@play.route("/play_scene/<int:adventure_id>/<int:scene_id>", methods=["GET"])
def play_scene(adventure_id: int, scene_id: int):
    if not current_user.is_active:
        flash("You need to be logged in to play a scene.")
        return redirect(url_for("site_landing.login"))
    session['cycle_count'] = 0

    return render_template("play/scene_player.html")


@play.route("/api/play_scene/<int:adventure_id>/<int:scene_id>", methods=["GET"])
def scene_execution(adventure_id:int, scene_id:int):
    """
    Fetches all relevant information for the use of a scene and displays this to the adventure_start.html before
    kicking of the scene_player.

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
    A audio or chat message received from the student in the form of:
    {
        "message" : "<the message>"
    }

    From here, the system checks if the call is ligit and if the request contains an audio or chat message.
    The call to session module is prepared and made. The outcome is formatted and forwarded to FE. See
    expected response:
    {
      "student_turn": {
        "role": "student",
        "text": "Bom dias, você vi a minha mochila?"
        "correction": Bom dia, você viu a minha mochila?"
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
    # Differentiate between text and audio input
    print(f"CYCLE_COUNT {session['cycle_count']}")
    if request.is_json:
        data = request.get_json()
        message = data.get("message","")

    elif "audio" in request.files:
        audio_file = request.files["audio"]
        message = "ola"
        # message = transcribe(audio_file)  # Your speech-to-text function

    else:
        return jsonify({"message" : "Expected a text message or audio file."})

    if "thread_id" not in session:
        session["thread_id"] = str(uuid4())
    if "cycle_count" not in session:
        session["cycle_count"] = 0

    persona_reply, state = get_persona_reply(adventure_id, scene_id, message, session["thread_id"])
    if persona_reply is None:
        return jsonify({"message" : "Could not derive persona information."}), 500

    corrected_text = state["corrections"][-1]
    all_scenes = dm.get_all_scenes(adventure_id)
    if all_scenes is None:
        return jsonify({"message": "Could not derive scene information."}), 500
    next_scene_id = -1
    for index in range(len(all_scenes)):
        if all_scenes[index]["scene_id"] == scene_id:
            if index == len(all_scenes)-1:
                next_scene_id = -1
            else:
                next_scene_id = all_scenes[index+1]["scene_id"]

    session_achievement = "Unknown"
    estimated_level = "Not yet measured"
    phrases_successfully_used = []
    phrases_to_improve = ["Eu quero → Eu queria"]
    grammar_tips = []
    words_unlocked = []
    words_successfully_used = "-"
    next_scene_unlocked = True
    scene_completed = state.get("goal_achieved", False)
    if "session_evaluation" in state:
        if "estimated_CEFR_level" in state["session_evaluation"]:
            estimated_level = state["session_evaluation"]["estimated_CEFR_level"]
        if "session_achievement" in state["session_evaluation"]:
            session_achievement = state["session_evaluation"]["session_achievement"]
        if "words_successfully_used" in state["session_evaluation"]:
            words_successfully_used = state["session_evaluation"]["words_successfully_used"]
            words_successfully_used = words_successfully_used.split(";")
        if "words_unlocked" in state["session_evaluation"]:
            words_unlocked = state["session_evaluation"]["words_unlocked"]
        if "phrases_successfully_used" in state["session_evaluation"]:
            phrases_successfully_used = state["session_evaluation"]["phrases_successfully_used"]
            phrases_successfully_used = phrases_successfully_used.split(";")
        if "phrases_to_improve" in state["session_evaluation"]:
            phrases_to_improve = state["session_evaluation"]["phrases_to_improve"]
            phrases_to_improve = phrases_to_improve.split(";")
        if "grammar_tips" in state["session_evaluation"]["grammar_tips"]:
            grammar_tips = state["session_evaluation"]["grammar_tips"]
            grammar_tips = grammar_tips.split(";")
    answer = {
        # "state": state,
        "student_turn": {
            "role": "student",
            "text": message,
            'correction':  corrected_text.content
        },
        "persona_turn": {
            "role": "persona",
            "text": persona_reply,
            "audio_url": ""
        },
        "feedback": {
            "summary": session_achievement,
            "goal_achieved": True,
            "estimated_level": estimated_level,
            "words_used": words_successfully_used,
            "phrases_well": phrases_successfully_used,
            "phrases_to_improve": phrases_to_improve,
            "grammar_tips": grammar_tips,
            "practice_next": "Practice polite ordering."
        },
        "next_scene_id": next_scene_id,
        "next_scene_unlocked": True,
        "scene_completed": scene_completed
    }
    session["cycle_count"] = session["cycle_count"] + 1
    print(f"CYCLE_COUNT: {session['cycle_count']}")
    if scene_completed:
        session["cycle_count"] = 0
        result, reason = dm.complete_and_unlock_scene(adventure_id, scene_id, current_user.student_id)
        if result is None:
            print(f"Could not complete the unlocking of the next scene: {reason}")
    print(answer)
    return jsonify(answer), 200

