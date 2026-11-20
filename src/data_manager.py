"""
This module contains the handling of movie and Student data which is modeled in the models-module.
It creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes of the fulfillment
of these requests by using the partners models and movie_data_fetcher.
"""

import logging
from sqlalchemy.exc import IntegrityError, OperationalError
from src.models import db, Adventure, Student, Student_Adventure, login_manager, Persona, Scene, Session
from src.errors import StudentStorageError, AdventureStorageError
from src.site_landing.data_manager import StudentDataManager
from src.adventures.data_manager import AdventureDataManager, PersonaDataManager
from src.play.data_manager import SessionDataManager

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

class DataManager:
    """
    Data manager class.
    Data manager controls all the db services and the fetching of the required data
    and storing them in the right format

    Knows HOW to retrieve adventure/scene/session/student information
    Knows HOW to store adventure/scene/session/student data
    Knows HOW to update adventure/scene/session/student data
    Knows HOW to delete adventure/scene/session/student data
    """

    # =========================================================================
    # All class definitions related to Student management
    # See also in site_landing BluePrint (src.site_landing)
    # =========================================================================
    @staticmethod
    def get_all_students() -> list[Student]:
        return StudentDataManager.get_all_students()

    @staticmethod
    def get_student(received_student_data) -> dict | None:
        return StudentDataManager.get_student(received_student_data)

    @staticmethod
    def get_student_object(received_student_data) -> Student | None:
        return StudentDataManager.get_student_object(received_student_data)

    @staticmethod
    def student_exists(received_student_data) -> bool:
        return StudentDataManager.student_exists(received_student_data)

    @staticmethod
    def add_student(registration_info: dict) -> Student | None:
        return StudentDataManager.add_student(registration_info)

    @staticmethod
    def student_is_active(student_id: int) -> bool:
        return StudentDataManager.student_is_active(student_id)

    @staticmethod
    def delete_student(student_data: int | str | Student) -> tuple:
        return StudentDataManager.delete_student(student_data)

    @staticmethod
    def update_student(student_id: int, updated_info: dict) -> Student | None:
        return StudentDataManager.update_student(student_id, updated_info)

    @staticmethod
    def make_admin(email: str) -> bool:
        return StudentDataManager.make_admin(email)

    # =========================================================================
    # All class definitions related to adventure storage management
    # See also in adventures BluePrint (src.adventures)
    # =========================================================================

    @staticmethod
    def get_all_adventures() -> list[dict]|None:
        return AdventureDataManager.get_all_adventures()


    @staticmethod
    def get_all_student_adventures(student_id: int) -> list[dict] | None:
        return AdventureDataManager.get_all_student_adventures(student_id)


    @staticmethod
    def get_adventure(adventure_id: int) -> dict | None:
        return AdventureDataManager.get_adventure(adventure_id)


    @staticmethod
    def create_adventure(adventure: dict, creator) -> tuple[Adventure|None, str]:
        return AdventureDataManager.create_adventure(adventure,creator)


    @staticmethod
    def adventure_exists(adventure_id: int) -> bool:
        return AdventureDataManager.adventure_exists(adventure_id)


    @staticmethod
    def act_deact_adventure(adventure_id: int, act_deact: bool) -> bool | None:
        return AdventureDataManager.act_deact_adventure(adventure_id, act_deact)


    @staticmethod
    def update_adventure(adventure_id: int, updated_adventure_data: dict) -> Adventure | None:
        return AdventureDataManager.update_adventure(adventure_id, updated_adventure_data)


    @staticmethod
    def delete_adventure(adventure_id: int, commit: bool = True) -> Adventure | None:
        return AdventureDataManager.delete_adventure(adventure_id, commit)


    @staticmethod
    def reserve_adventure(adventure_id:int, student_id:int) -> tuple[list[Student_Adventure] | None, str]:
        return  AdventureDataManager.reserve_adventure(adventure_id, student_id)


    @staticmethod
    def get_full_student_adventure_data(adventure_id, student_id) -> tuple[dict|None, str]:
        return AdventureDataManager.get_full_student_adventure_data(adventure_id, student_id)


    @staticmethod
    def change_adventure_status(adventure_id:int, student_id:int, new_status: str) -> tuple[bool, str]:
        return AdventureDataManager.change_adventure_status(adventure_id, student_id, new_status)


    @staticmethod
    def student_adventure_exists(adventure_id: int, student_id: int) -> bool:
        return AdventureDataManager.student_adventure_exists(adventure_id, student_id)


    @staticmethod
    def get_student_adventure(adventure_id: int, student_id: int, sorting_command:dict|None=None) -> list[Student_Adventure] | None:
        return AdventureDataManager.get_student_adventure(adventure_id, student_id)

    @staticmethod
    def complete_and_unlock_scene(adventure_id: int, current_scene_id: int, student_id: int) -> tuple[bool|None, str]:
        return AdventureDataManager.complete_and_unlock_scene(adventure_id, current_scene_id, student_id)

    @staticmethod
    def scene_exists(adventure_id: int, scene_id: int) -> bool:
        return AdventureDataManager.scene_exists(adventure_id, scene_id)


    @staticmethod
    def set_current_scene(adventure_id: int, student_id: int, current_scene: int) -> tuple[bool, str]:
        return AdventureDataManager.set_current_scene(adventure_id, student_id, current_scene)

    @staticmethod
    def get_number_of_scenes(adventure_id: int) -> int:
        return AdventureDataManager.get_number_of_scenes(adventure_id)

    @staticmethod
    def get_all_scenes(adventure_id:int)-> list[dict|None]:
        return AdventureDataManager.get_all_scenes(adventure_id)

    @staticmethod
    def get_scene_status(adventure_id:int, scene_id:int, student_id:int)->tuple[bool|None, str]:
        return AdventureDataManager.get_scene_status(adventure_id, scene_id, student_id)
    # =============================================================================================
    # ======================********* Persona Data Management ********=============================
    # =============================================================================================

    @staticmethod
    def create_persona(persona: dict) -> tuple[Persona|None, str]:
        return PersonaDataManager.create_persona(persona)

    @staticmethod
    def get_all_personas() -> list[Persona|None]:
        return PersonaDataManager.get_all_personas()


    @staticmethod
    def update_persona(persona_id: int, updated_persona_data: dict) -> Persona|None:
        return PersonaDataManager.update_persona(persona_id, updated_persona_data)


    @staticmethod
    def delete_persona(persona_id: int, commit: bool = True) -> Persona | None:
        return PersonaDataManager.delete_persona(persona_id, commit)


    # =============================================================================================
    # ======================********* Session Data Management ********=============================
    # =============================================================================================

    @staticmethod
    def get_session_data_by_id(adventure_id: int, scene_id: int, session_id: int) -> Session:
        return SessionDataManager.get_session_data_by_id(adventure_id, scene_id, session_id)


    @staticmethod
    def session_exists(session_id:int) -> bool:
        return SessionDataManager.session_exists(session_id)


    @staticmethod
    def store_session_data(adventure_id:int, scene_id: int, student_id, session_data) -> Session | None:
        return SessionDataManager.store_session_data(adventure_id, scene_id, student_id, session_data)


    @staticmethod
    def get_all_adventure_session_data_of_student(adventure_id: int, scene_id: int) -> list[dict] | None:
        return SessionDataManager.get_all_adventure_session_data_of_student(adventure_id, scene_id)


    @staticmethod
    def get_all_session_data(adventure_id: int, scene_id: int, student_id: int)-> list[dict] | None:
        return SessionDataManager.get_all_session_data(adventure_id, scene_id, student_id)


    @staticmethod
    def get_all_sessions_for_scene(adventure_id: int, scene_id: int)-> list[dict] | None:
        return SessionDataManager.get_all_sessions_for_scene(adventure_id, scene_id)


    @staticmethod
    def get_number_of_sessions_for_scene(adventure_id: int, scene_id: int)->int:
        return SessionDataManager.get_number_of_sessions_for_scene(adventure_id, scene_id)



