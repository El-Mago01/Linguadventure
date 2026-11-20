"""
This module contains the handling of adventure and Student data which is modeled in model-module
It creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of adventure related data externally by adventure_data_fetcher-module
The service requests will come from the app-module. The data_manager takes of the fulfillment
of these requests by using the partners models and adventure_data_fetcher.
"""

import logging

from sqlalchemy.exc import IntegrityError, OperationalError
from src.errors import AdventureStorageError
from src.adventures.data_manager import AdventureDataManager
from src.site_landing.data_manager import StudentDataManager
from sqlalchemy import and_
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from src.models import db, Adventure, Student, Student_Adventure, Persona, Scene, Session, Message
from src.play.state import State
from flask_login import  login_required, current_user

from wrapup.routes import session_evaluation


# =========================================================================
# -------------------------------------------------------------------------
# ************************** SessionDataManager *************************
# -------------------------------------------------------------------------
# =========================================================================

class SessionDataManager:
    """
    Data manager class.
    Data manager controls all the db services and the fetching of the required data
    and storing them in the right format

    A session is the data created by the student and the AI-actor when doing scene. This
    includes the evaluation and correction data. As such
    a session is always connected to an adventure/scene/student.
    A datamanager:
    Knows HOW to retrieve adventure/scene/session/student information
    Knows HOW to store adventure/scene/session/student data
    Knows HOW to update adventure/scene/session/student data
    Knows HOW to delete adventure/scene/session/student data
    """

    def __init__(self):
        pass

    # =========================================================================
    # All method  definitions related to session management
    # =========================================================================

    @staticmethod
    def get_session_data_by_id(adventure_id:int, scene_id:int, session_id:int) -> Session|None:
        """
         returns a session object with the provided session_id or none if the session_id is not found.
         :param session_id:
         :return:
         """
        if isinstance(session_id, int):
            if SessionDataManager.session_exists(session_id):
                stmt = db.select(Session).where(
                    Session.session_id == session_id)
            else:
                return None
        else:
            return None
        session = db.session.execute(stmt).scalars().one()
        a_session = session.serialize()
        a_session["messages"] = MessageDataManager.get_all_messages(session)
        return a_session


    @staticmethod
    def session_exists(session_id:int) -> bool:
        """
        Checks if the received session_id represents a session  in the database, i.e. the session table
        :param session_id:

        :return: boolean -> True if the session exists, False otherwise
        """
        if not isinstance(session_id, int):
            return False
        stmt = db.select(Session).where(Session.session_id == session_id)
        existing_session = db.session.execute(stmt).scalars().all()

        if len(existing_session) == 1:
            return True
        return False


    @staticmethod
    def store_session_data(adventure_id:int, scene_id:int, student_id:int, session_data:State)->None|Session:
        """
        Stores the session received data and per message in the session data the following data is stored:
        - human message
        - the ai answer
        - the ai correction
        :param adventure_id:
        :param scene_id:
        :param student_id:
        :param session_data:
        :return:
        """
        if not session_data:
            return None
        if not "messages" in session_data:
            return None
        if len(session_data["messages"]) == 0:
            return None
        if not "corrections" in session_data:
            return None
        if len(session_data["corrections"]) == 0:
            return None
        if not "session_evaluation" in session_data:
            return None
        if len(session_data["session_evaluation"]) == 0:
            return None
        goal_achieved = session_data.get("goal_achieved", False)
        student_message = []
        persona_message = []
        correction = []
        if len(session_data["messages"]) == 0 or len(session_data["corrections"]) == 0:
            return None
        if len(session_data["messages"]) != len(session_data["corrections"]):
            return None
        for index in range(1, len(session_data["messages"])):
            if index % 2 == 1:
                if session_data["messages"][index].type == "human":
                    print(session_data["messages"][index].content)
                    student_message.append(session_data["messages"][index].content)
                else:
                    print("Data inconsistency! Check state content")
                    return None
            else:
                if session_data["messages"][index].type == "ai":
                    persona_message.append(session_data["messages"][index].content)
                    print(session_data["messages"][index].content)

                else:
                    print("Data inconsistency! Check state content")
                    return None
                if session_data["corrections"][index].type == "ai":
                    correction.append(session_data["corrections"][index].content)
                    print(session_data["corrections"][index].content)
                else:
                    print("Data inconsistency! Check state content")
                    return None
        if not correction or not student_message or not persona_message:
            return None
        session_achievement = session_data.get("session_evaluation").get("session_achievement", "")
        used_words = session_data.get("session_evaluation").get("words_successfully_used", "")
        used_phrases = session_data.get("session_evaluation").get("phrases_successfully_used", "")
        grammar_tips = session_data.get("session_evaluation").get("grammar_tips", "")
        improve_next = ""
        estimated_CEFR_level = session_data.get("session_evaluation").get("estimated_CEFR_level", "")
        scene_status = "Not achieved yet"
        if goal_achieved:
            scene_status = "Achieved"
        new_session = Session(
            adventure_id = adventure_id,
            scene_id = scene_id,
            student_id = student_id,
            session_achievement = session_achievement,
            scene_status = scene_status,
            used_words = used_words,
            used_phrases = used_phrases,
            grammar_tips = grammar_tips,
            improve_next = improve_next,
            estimated_CEFR_level = estimated_CEFR_level,
        )
        db.session.add(new_session)
        db.session.flush()

        session_id=new_session.session_id
        stored_message = MessageDataManager.store_message_data(session_id, student_message, persona_message, correction)
        if not stored_message:
            return None
        db.session.commit()

        return new_session


    @staticmethod
    def get_all_adventure_session_data_of_student(adventure_id:int, scene_id:int)->list[dict] | None:
        pass

    @staticmethod
    def get_all_session_data(adventure_id:int, scene_id:int, student_id:int) -> None | list[dict]:
        """
         Checks if the received session_id represents a session  in the database, i.e. the session table
         :param session_id:

         :return: boolean -> True if the session exists, False otherwise
         """
        if not isinstance(scene_id, int):
            return False
        stmt = (db.select(Session)
                .join(Scene, Scene.scene_id == scene_id)
                .where(Scene.adventure_id == adventure_id,
                       Session.student_id == student_id)).order_by(Scene.scene_order_nr)
        all_sessions = db.session.execute(stmt).scalars().all()
        all_session_data = [session.serialize() for session in all_sessions]
        if len(all_sessions) < 1:
            return None
        return all_session_data





    @staticmethod
    def get_all_sessions_for_scene(adventure_id, scene_id):
        pass


    @staticmethod
    def get_number_of_sessions_for_scene(adventure_id: int, scene_id:int) -> int:
        """
        Derive the number of scenes that exists for a specific adventure.
        :param adventure_id:
        :param scene_id:
        :return:
        """

        if not isinstance(adventure_id, int):
            return -1

        stmt = db.select(Session).where(and_(Session.adventure_id == adventure_id, Session.scene_id == scene_id))
        sessions = db.session.execute(stmt).all()
        return len(sessions)

# ========================================================================
# ------------------------------------------------------------------------
# ************************** MessageDataManager *************************
# ------------------------------------------------------------------------
# ========================================================================
class MessageDataManager:

    def __init__(self):
        pass

    @staticmethod
    def message_exists(message_id:int) -> bool:
        """
        Checks if the received message_id represents a session  in the database, i.e. the message table
        :param message_id:

        :return: boolean -> True if the session exists, False otherwise
        """
        if not isinstance(message_id, int):
            return False
        stmt = db.select(Message).where(Message.message_id == message_id)
        existing_message = db.session.execute(stmt).scalars().all()

        if len(existing_message) == 1:
            return True
        return False


    @staticmethod
    def store_message_data(session_id:int, student_message:list[str], persona_message:list[str], correction:list[str]):
        if len(student_message) == 0:
            return None
        if len(student_message) != len(persona_message) or len(student_message) != len(correction):
            return None
        message_sequence_nr = 0
        for index in range(0, len(student_message)):
            message = Message(
                session_id = session_id,
                student_message = student_message[index],
                persona_message = persona_message[index],
                sequence_nr=message_sequence_nr,
                correction = correction[index],
                source = "text",
                audio_link = "no link. function not working yet",
                audio_content="Not working yet"
            )
            message_sequence_nr += 1
            db.session.add(message)
            db.session.flush()
        return message

    @staticmethod
    def get_all_messages(session_id:int)-> list[dict|None]:
        if not isinstance(session_id, int):
            return []
        try:
            stmt = db.select(Message).where(
                Message.session_id == session_id)
            messages = db.session.execute(stmt).scalars().all()
            if len(messages) < 1:
                return []
            return [message.serialize() for message in messages]
        except OperationalError as e:
            return []

# ========================================================================
# ------------------------------------------------------------------------
# ************************** FeedbackDataManager *************************
# ------------------------------------------------------------------------
# ========================================================================

class FeedbackDataManager:
    """
    Data manager class.
    Data manager controls all the db services and the fetching of the required data
    and storing them in the right format

    Knows HOW to retrieve adventure/scene/session/student information
    Knows HOW to store adventure/scene/session/student data
    Knows HOW to update adventure/scene/session/student data
    Knows HOW to delete adventure/scene/session/student data
    """

    def __init__(self):
        pass

    # =========================================================================
    # All method definitions related to feedback management
    # =========================================================================