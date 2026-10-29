"""
This module contains the handling of movie and Student data which is modeled in the models-module.
It creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes of the fulfillment
of these requests by using the partners models and movie_data_fetcher.
"""

import logging

from sqlalchemy.exc import IntegrityError, OperationalError

from models import db, Adventure, Student, Student_Adventure
from src.errors import StudentStorageError, AdventureStorageError
from src.site_landing.data_manager import StudentDataManager
from src.adventures.data_manager import AdventureDataManager

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
    def student_exists(received_student_data) -> bool:
        return StudentDataManager.student_exists(received_student_data)

    @staticmethod
    def add_student(registration_info: dict) -> Student | None:
        return StudentDataManager.add_student(registration_info)

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
    def get_all_adventures(student_id) -> list[Adventure]:
        return AdventureDataManager.get_all_adventures(student_id)


    @staticmethod
    def get_all_adventures_of_student(student_id: int, sorting_command: dict) -> list[Adventure | None]:
        return AdventureDataManager.get_all_adventures(student_id, sorting_command)

    @staticmethod
    def get_adventure(adventure_id: int) -> Adventure | None:
        return AdventureDataManager.get_adventure(adventure_id)

    @staticmethod
    def store_adventure(adventure: dict) -> Adventure:
        return AdventureDataManager.store_adventure(adventure)

    @staticmethod
    def adventure_exists(adventure_id: int) -> bool:
        return AdventureDataManager.adventure_exists(adventure_id)

    @staticmethod
    def delete_adventure(adventure_id: int, commit: bool = True) -> Adventure | None:
        return AdventureDataManager.delete_adventure(adventure_id, commit)
