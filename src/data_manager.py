"""
This module contains the handling of movie and Student data which is modeled in the models-module.
It creates an abstraction layer for the app-module by providing an interface tailored for
the storage of the data or fetching of movie related data externally by movie_data_fetcher-module
The service requests will come from the app-module. The data_manager takes of the fulfillment
of these requests by using the partners models and movie_data_fetcher.
"""

import logging

from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError, OperationalError

import re
from models import db, Adventure, Student, Student_Adventure
# from movie_data_fetcher import fetch_movie_general_data, fetch_movie_data


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

class StudentStorageError(Exception):
    pass


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

    def __init__(self):
        self.is_active = True

    # =========================================================================
    # All class definitions related to Student management
    # =========================================================================
    def get_all_students(self) -> list[Student]:
        """
        derive all Students from the db.
        :return: a list of Students
        """
        stmt = db.select(Student).order_by(Student.last_name.asc())
        students = db.session.execute(stmt).scalars().all()
        return list(students)

    def get_student(self, received_student_data) -> dict|None:
        """
        Returns the student information based on received student data.
        :param received_student_data:
                - a str: received_student_data contains the email address
                - an int: recieved_student_data contains the student_id
                - a Student object: received_student_data contains a Student object
        :return:
        """
        all_students = self.get_all_students()
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

    def student_exists(self, received_student_data) -> bool:
        """
        Checks if the received student exists in the student table
        :param received_student_data: data can be:
        - a string to compare on email address
        - an int to compare on Student_id
        - a student object to compare the object

        comparison with the existing Student objects in the DB
        :return:
        """
        all_students = self.get_all_students()
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

    def add_student(self, registration_info: dict) -> Student|None:
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
        logging.info(f"Request received to add a new user to the DB with email address: {registration_info.get('email_address','')}")
        email_address = registration_info.get("email", "")
        if not email_address:
            logging.warning(
                f"Request received to add a new user without a valid email address.")

            raise StudentStorageError("No valid email address received")
        new_student = Student(email=email_address)
        stmt = db.select(Student).where(Student.email == email_address)
        existing_students = db.session.execute(stmt).scalars().all()
        for student in existing_students:
            if email_address == student.email:
                logging.warning(f"Email address already exists in StudentDB: {student.email}")
                raise StudentStorageError("Email address already exists in StudentDB")
        # store the new Student_name
        new_student.first_name = registration_info.get("first_name", "")
        new_student.last_name = registration_info.get("last_name", "")
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
        return new_student

    def delete_student(self, student_data: int | str | Student) -> tuple:
        """
        Deletes the provided Student from the db. Associated movies will be automatically
        deleted due to cascade mapping on Student.movies relationship.
        """
        if isinstance(student_data, int):     # expect
            student_to_delete = student_data
        elif isinstance(student_data, str):   # expect email address as input
            student_to_delete = self.get_student(student_data)
        else:
            return (
                None,
                f"Programming error, received {student_data} should be an integer or a string."
            )
        try:
            stmt = db.select(Student).where(Student.student_id == student_id_to_delete)
            student_to_delete = db.session.execute(stmt).scalars().one_or_none()
            if student_to_delete is None:
                return None, f"No Student found with the provided Student ID: {student_id_to_delete}"
            
            db.session.delete(student_to_delete)
            db.session.commit()
            return student_to_delete, f"Student {student_to_delete.first_name} deleted successfully!"

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error while deleting Student: {e}")
            return None, "Error while deleting Student and associated movies. Rollback executed"


    def update_Student(self, student_id: int, updated_info: dict) -> Student | None:
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

        student_to_update[0].first_name = updated_info.get("first_name","")
        student_to_update[1].last_name = updated_info.get("last_name", "")
        student_to_update[2].target_language = updated_info.get("target_language", "")
        student_to_update[3].original_language = updated_info.get("original_language", "")
        student_to_update[4].age = updated_info.get("age", "")
        student_to_update[5].gender = updated_info.get("gender", "")
        student_to_update[6].occupation = updated_info.get("occupation", "")
        student_to_update[7].current_level = updated_info.get("current_level", "")
        db.session.commit()
        return student_to_update

    # =========================================================================
    # All class definitions related to movie management
    # =========================================================================

    def fetch_adventures(self, student_id) -> list[Adventure]:
        """
        Interface function for searching for movies with a specific title within the imdb web-site.
        The search is actually performed by the movie_data_fetcher module.
        :param movie_title:
        :return:
        """
        if not isinstance(student_id, int):
            return []
        if student_id < 0:
            return []
        all_adventures = fetch_all_adventures(student_id)
        return all_adventures

    def create_movie(self, imdbID: str) -> tuple:
        """
        Creates a new movie object without the movie_id as this is established the moment the
        movie is stored in the DB.
        Fetch relevant details for the received imdbID which will be used to create the movie.
        if movie details are received, create a movie object and return it.

        :param imdbID:
        :return: If no movie details are received return None. Otherwise return the movie object
        with a result string.
        """
        if not isinstance(imdbID, str):
            return None, "received imdbID is not a string"
        movie_details = fetch_movie_data(imdbID)
        Student = self.get_active_Student()
        if Student is None:
            return None, "Error: active Student is not set. Please select an active Student first"
        Student_id = Student.Student_id
        if len(movie_details) != 0:
            new_movie = Movie(
                title=movie_details.get("Title", ""),
                director=movie_details.get("Director", ""),
                IMDB_id=imdbID,
                year=normalize_year(movie_details.get("Year", "")),
                poster_url=movie_details.get("Poster", ""),
                Student_id=Student_id
            )
            return (
                new_movie, f"Movie {
                    new_movie.title} by {
                    new_movie.director} created successfully!", )
        return None, "Error: Movie details could not be fetched. Please try again later"

    def movie_exists(self, a_movie_id:int|str) -> bool:
        """
        Checks if the received movie_id or imdbID exists in the database
        :param a_movie_id: as int -> movie_id
                           as str -> imdb_id

        :return: boolean -> True if movie exists, False otherwise
        """

        act_usr = self.get_active_Student()
        if act_usr is None:
            return False
        if isinstance(a_movie_id, int):
            stmt = db.select(Movie).where(Movie.movie_id == a_movie_id)
        elif isinstance(a_movie_id, str):
            stmt = db.select(Movie).where(
                Movie.IMDB_id == a_movie_id,
                Movie.Student_id == act_usr.Student_id
            )
        else:
            return False
        existing_movies = db.session.execute(stmt).scalars().all()


        if len(existing_movies) != 0:
            return True
        return False

    def title_exists(self, title: str, active_Student_id: int) -> bool:
        """
        Checks if the received title exists in the database. Only used for manually added movies
        :param title
        :param active_Student_id: Is needed to check if the title exists in the db for THIS specific Student
        :return: boolean -> True if movie with this title exists, False otherwise
        """
        if not isinstance(active_Student_id, int) or active_Student_id < 0:
            return False
        if not isinstance(title, str) or len(title) == 0:
            return False
        stmt = (
            db.select(Movie)
            .where(
                Movie.Student_id == active_Student_id,
                Movie.title == title,
            )
        )
        existing_movies = db.session.execute(stmt).scalars().all()
        if len(existing_movies) != 0:
            return True
        return False

    def store_movie(self, movie: Movie):
        """
        Store the received movie into the database.
        :param movie of type Movie
        :return:
        """
        imdb_id = movie.IMDB_id
        if not isinstance(imdb_id, str) or len(imdb_id) == 0:
            return None, "received imdb_id is not a string"
        if self.movie_exists(movie.IMDB_id):
            return None, f"Movie {movie.title} already exists in the database"
        db.session.add(movie)
        db.session.commit()
        print("added movie:", movie)
        return (
            movie,
            f"Movie successfully stored in the DB: {movie.title}, {movie.director}")

    def store_manually_added_movie(self, movie: dict) -> tuple:
        """
        Store the manually added movie into the database.
        :param movie:
        :return:
        """
        if len(movie.get("title", "")) == 0:
            return None, "Movie can not be stored: Movie title can not be empty"
        if self.title_exists(movie.get("title", ""), self.active_Student.Student_id):
            return None, "Movie can not be stored: Movie title already exists"
        Student = self.get_active_Student()
        if Student is None:
            return None, "Error: active Student is not set. Please select an active Student first"
        new_movie = Movie(
            title=movie.get("title", ""),
            director=movie.get("director", ""),
            IMDB_id=movie.get("IMDB_id", ""),
            year=normalize_year(movie.get("year", "")),
            poster_url=movie.get("poster_url", ""),
            Student_id=Student.Student_id,
        )
        try:
            db.session.add(new_movie)
            db.session.commit()
        except IntegrityError as e:
            logging.info("Movie can not be stored due to error: %s", e)
            return new_movie, f"Movie can not be stored due to error: {e}"
        print("added movie:", new_movie)
        return None, "Manually added movie stored successfully"

    def get_all_movies_of_student(
        self, Student_id:int, sorting_command: dict
    ) -> list[Student | None]:
        """
        returns a list of all movies for the active Student
        :return:
        """
        if not isinstance(Student_id, int):
            return []
        if not self.student_exists(Student_id):
            return []
        sort_by = sorting_command.get("sort_by", "movies")
        direction = sorting_command.get("direction", "asc")
        
        stmt = db.select(Adventure).where(Student_Adventure.student_id == Student_id)
        if sort_by == "movies":
            if direction == "asc":
                stmt = stmt.order_by(Adventure.title.asc())
            else:
                stmt = stmt.order_by(Adventure.title.desc())
        else:
            if direction == "asc":
                stmt = stmt.order_by(Adventure.creator.asc())
            else:
                stmt = stmt.order_by(Adventure.creator.desc())
                
        movies = db.session.execute(stmt).scalars().all()
        return list(movies)

    def get_movie(self, movie_id: int) -> Movie | None:
        """
        returns a movie object with the provided movie_id or none if the movie_id is not found.
        :param movie_id:
        :return:
        """
        if isinstance(movie_id, int):
            if self.movie_exists(movie_id):
                stmt = db.select(Movie).where(
                    Movie.movie_id == movie_id)
            else:
                return None
        else:
            return None
        movie = db.session.execute(stmt).scalars().one()
        return movie



    def delete_adventure(self, adventure_id:int, commit:bool=True) -> Adventure | None:
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
        movie_to_delete = db.session.execute(stmt).scalars().one_or_none()
        if movie_to_delete is None:
            return None
        try:
            db.session.delete(movie_to_delete)
            if commit:
                db.session.commit()
        except OperationalError:
            logging.error(
                f"Fatal error while deleting movie {adventure_id} from database")
            db.session.rollback()
            return None

        return movie_to_delete
