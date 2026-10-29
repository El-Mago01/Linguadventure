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

from models import db, Adventure, Student, Student_Adventure

# from adventure_data_fetcher import fetch_adventure_general_data, fetch_adventure_data




class AdventureDataManager:
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
    # All class definitions related to adventure management
    # =========================================================================
    @staticmethod
    def get_all_adventures(student_id) -> list[Adventure]:
        """
        Interface function for searching for adventures with a specific title within the imdb web-site.
        The search is actually performed by the adventure_data_fetcher module.
        :param adventure_title:
        :return:
        """
        if not isinstance(student_id, int):
            return []
        if student_id < 0:
            return []
        all_adventures = get_all_adventures(student_id)
        return all_adventures

    @staticmethod
    def get_all_adventures_of_student(student_id: int, sorting_command: dict) -> list[Adventure | None]:
        """
        returns a list of all adventures for the active Student
        :return:
        """
        if not isinstance(student_id, int):
            return []
        if not AdventureDataManager.student_exists(student_id):
            return []
        sort_by = sorting_command.get("sort_by", "adventures")
        direction = sorting_command.get("direction", "asc")

        stmt = db.select(Adventure).where(Student_Adventure.student_id == student_id)
        if sort_by == "adventures":
            if direction == "asc":
                stmt = stmt.order_by(Adventure.title.asc())
            else:
                stmt = stmt.order_by(Adventure.title.desc())
        else:
            if direction == "asc":
                stmt = stmt.order_by(Adventure.creator.asc())
            else:
                stmt = stmt.order_by(Adventure.creator.desc())

        adventures = db.session.execute(stmt).scalars().all()
        return list(adventures)

    @staticmethod
    def get_adventure(adventure_id: int) -> Adventure | None:
        """
        returns a adventure object with the provided adventure_id or none if the adventure_id is not found.
        :param adventure_id:
        :return:
        """
        if isinstance(adventure_id, int):
            if AdventureDataManager.adventure_exists(adventure_id):
                stmt = db.select(Adventure).where(
                    Adventure.adventure_id == adventure_id)
            else:
                return None
        else:
            return None
        adventure = db.session.execute(stmt).scalars().one()
        return adventure


    @staticmethod
    def store_adventure(adventure: dict) -> Adventure:
        """


        :param :
        :return: 
        """
        if not isinstance(adventure, dict):
            return None, "received imdbID is not a string"
        adventure_details = AdventureDataManager.get_adventure(adventure)
        Student = self.get_active_Student()
        if Student is None:
            return None, "Error: active Student is not set. Please select an active Student first"
        Student_id = Student.Student_id
        if len(adventure_details) != 0:
            new_adventure = adventure(
                title=adventure_details.get("Title", ""),
                director=adventure_details.get("Director", ""),
                IMDB_id=imdbID,
                year=normalize_year(adventure_details.get("Year", "")),
                poster_url=adventure_details.get("Poster", ""),
                Student_id=Student_id
            )
            return (
                new_adventure, f"adventure {
            new_adventure.title} by {
            new_adventure.director} created successfully!",)
        return None, "Error: adventure details could not be fetched. Please try again later"

    @staticmethod
    def adventure_exists(adventure_id: int) -> bool:
        """
        Checks if the received adventure_id exists in the database
        :param adventure_id: 

        :return: boolean -> True if the adventure exists, False otherwise
        """


        if isinstance(a_adventure_id, int):
            stmt = db.select(adventure).where(adventure.adventure_id == a_adventure_id)
        elif isinstance(a_adventure_id, str):
            stmt = db.select(adventure).where(
                adventure.IMDB_id == a_adventure_id,
                adventure.Student_id == act_usr.Student_id
            )
        else:
            return False
        existing_adventures = db.session.execute(stmt).scalars().all()

        if len(existing_adventures) != 0:
            return True
        return False

    
    @staticmethod
    def delete_adventure(adventure_id: int, commit: bool = True) -> Adventure | None:
        """
        Deletes the adventure from the adventure table

        :param adventure_id: adventure identifier
        :param commit: An indicator if the commit should be given or if the commit will be
                       done outside of this function

        :return: The Adventure object fitting the adventure_id or None if the adventure does not exist in the DB
        """
        if not isinstance(adventure_id, int):
            return None
        stmt = db.select(Adventure).where(Adventure.adventure_id == adventure_id)
        adventure_to_delete = db.session.execute(stmt).scalars().one_or_none()
        if adventure_to_delete is None:
            return None
        try:
            db.session.delete(adventure_to_delete)
            if commit:
                db.session.commit()
        except OperationalError:
            logging.error(
                f"Fatal error while deleting adventure {adventure_id} from database")
            db.session.rollback()
            return None

        return adventure_to_delete
