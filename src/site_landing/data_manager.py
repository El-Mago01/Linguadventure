"""
This module contains the handling of movie and Student data which is modeled in the models-module.
It creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes of the fulfillment
of these requests by using the partners models and movie_data_fetcher.
"""

import logging
from src.errors import StudentStorageError
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError, OperationalError

import re
from models import db, Adventure, Student, Student_Adventure


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

class StudentDataManager:
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
    # All class definitions related to Student management
    # =========================================================================

    @staticmethod
    def get_all_students() -> list[Student]:
        """
        derive all Students from the db.
        :return: a list of Students
        """
        stmt = db.select(Student).order_by(Student.last_name.asc())
        students = db.session.execute(stmt).scalars().all()
        return list(students)

    @staticmethod
    def get_student(received_student_data) -> dict | None:
        """
        Returns the student information based on received student data.
        :param received_student_data:
                - a str: received_student_data contains the email address
                - an int: recieved_student_data contains the student_id
                - a Student object: received_student_data contains a Student object
        :return:
        """
        all_students = StudentDataManager.get_all_students()
        for student in all_students:
            if isinstance(received_student_data, Student):
                if student.student_id == received_student_data.student_id:
                    return student.serialize()
            if isinstance(received_student_data, int):
                if student.student_id == received_student_data:
                    return student.serialize()
            if isinstance(received_student_data, str):
                if student.email == received_student_data:
                    return student.serialize()
        return None

    @staticmethod
    def student_exists(received_student_data) -> bool:
        """
        Checks if the received student exists in the student table
        :param received_student_data: data can be:
        - a string to compare on email address
        - an int to compare on Student_id
        - a student object to compare the object

        comparison with the existing Student objects in the DB
        :return:
        """
        all_students = StudentDataManager.get_all_students()
        if isinstance(received_student_data, int):
            for student in all_students:
                if student.student_id == received_student_data:
                    return True
        if isinstance(received_student_data, str):
            for student in all_students:
                if student.email == received_student_data:
                    return True
        if isinstance(received_student_data, Student):
            for student in all_students:
                if Student.student_id == received_student_data.student_id:
                    return True
        return False

    @staticmethod
    def add_student(registration_info: dict) -> Student | None:
        """
        Upon request to add a new Student to the db, first it is checked if perhaps the
        email address already exists in the db. if so, return with result code -1

        if it is a new student, the student will be stored in the db and the new_Student object
        will be returned
        :param registration_info (which includes the email address)
        :return:
        """
        if not isinstance(registration_info, dict):
            raise StudentStorageError("Received registration info is not a dict")
        logging.info(
            f"Request received to add a new user to the DB with email address: {registration_info.get('email', '')}")
        email_address = registration_info.get("email", "")
        if not email_address:
            logging.warning(
                f"Request received to add a new user without a valid email address.")

            raise StudentStorageError("No valid email address received")
        if StudentDataManager.student_exists(email_address):
            logging.warning(f"Email address already exists in StudentDB: {email_address}")
            raise StudentStorageError("Email address already exists in StudentDB")
        # store the new Student_name
        new_student = Student()
        new_student.first_name = registration_info.get("first_name", "")
        new_student.last_name = registration_info.get("last_name", "")
        new_student.email = email_address
        new_student.target_language = registration_info.get("target_language", "")
        new_student.original_language = registration_info.get("original_language", "")
        if new_student.first_name == "" or new_student.last_name == "":
            logging.warning("No valid first or last name received")
            raise StudentStorageError("No valid first or last name received")
        if new_student.target_language == "" or new_student.original_language == "":
            logging.warning("No valid first or last name received")
            raise StudentStorageError("No valid first or last name received")
        new_student.age = registration_info.get("age", "")
        new_student.gender = registration_info.get("gender", "")
        new_student.occupation = registration_info.get("occupation", "")
        new_student.current_level = registration_info.get("current_level", "")
        db.session.add(new_student)
        db.session.commit()
        logging.info(
            f"Successfull storage of new user with email address {registration_info.get('email', '')} has user id {new_student.student_id}.")
        return new_student

    @staticmethod
    def delete_student(student_data: int | str | Student) -> tuple:
        """
        Deletes the provided Student from the db. Associated movies will be automatically
        deleted due to cascade mapping on Student.movies relationship.
        """
        if isinstance(student_data, int):  # expect student_id as input
            student_id_to_delete = student_data
        elif isinstance(student_data, str):  # expect email address as input
            student_id_to_delete = StudentDataManager.get_student(student_data)
        elif isinstance(student_data, Student):
            student_id_to_delete = student_data.student_id
        else:
            return (
                None,
                f"Programming error, received {student_data} should be an integer, string or a Student object."
            )
        logging.info(f"Request received to delete user with student ID: {student_id_to_delete}")

        try:
            stmt = db.select(Student).where(Student.student_id == student_id_to_delete)
            student_to_delete = db.session.execute(stmt).scalars().one_or_none()
            if student_to_delete is None:
                return None, f"No Student found with the provided Student ID: {student_id_to_delete}"

            db.session.delete(student_to_delete)
            db.session.commit()
            logging.info(f"Deletion successful. Student with student ID: {student_to_delete.student_id} is deleted")
            return student_to_delete, f"Student {student_to_delete.student_id} deleted successfully!"

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error while deleting Student: {e}")
            return None, "Error while deleting Student and associated movies. Rollback executed"

    @staticmethod
    def update_student(student_id: int, updated_info: dict) -> Student | None:
        """
        Update the Student_name of the Student object that has the provided Student_id
        :param Student_id:
        :param new_Student_name:
        :return:
        """
        if not isinstance(student_id, int):
            return None
        if not isinstance(updated_info, dict):
            return None
        stmt = db.select(Student).where(Student.student_id == student_id)
        student_to_update = db.session.execute(stmt).scalars().all()
        if len(student_to_update) != 1:
            return None

        student_to_update[0].first_name = updated_info.get("first_name", "")
        student_to_update[1].last_name = updated_info.get("last_name", "")
        student_to_update[2].target_language = updated_info.get("target_language", "")
        student_to_update[3].original_language = updated_info.get("original_language", "")
        student_to_update[4].age = updated_info.get("age", "")
        student_to_update[5].gender = updated_info.get("gender", "")
        student_to_update[6].occupation = updated_info.get("occupation", "")
        student_to_update[7].current_level = updated_info.get("current_level", "")
        db.session.commit()
        return student_to_update

    @staticmethod
    def make_admin(email: str) -> bool:
        """
        Update the Student_name of the Student object that has the provided Student_id
        :param email:
        :return:
        """
        if not isinstance(email, str):
            return False

        stmt = db.select(Student).where(Student.email == email)
        student_to_update = db.session.execute(stmt).scalars().all()
        if len(student_to_update) != 1:
            return False

        student_to_update[0].is_admin = True

        db.session.commit()
        return True
