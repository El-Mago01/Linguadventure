"""
This module contains the handling of the database for the linguadventure model.
The graphical overview of this model can be found here:

It helps the data_manager to create an abstraction layer for the app-module
by providing an interface tailored for the storage of the data or fetching
of movie related data externally by movie_data_fetcher-module.
The service requests will come from the app-module. The data_manager will
take care of the fulfillment of these requests by using the partners models and
movie_data_fetcher.
"""

from flask_sqlalchemy import SQLAlchemy

# from app import app

db = SQLAlchemy()

# ================================================================================
# User class (inheriting from db.Model class)
# ================================================================================
class Student(db.Model):
    """
    Student model

    """

    __tablename__ = "student"
    student_id = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    occupation = db.Column(db.String(100))
    original_language = db.Column(db.String(100))
    target_language = db.Column(db.String(100))
    current_level = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    # movies = db.relationship("Movie", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.student_id}: {self.name},\n"

    def __str__(self):
        return f"{self.student_id}: {self.name},\n"

# ================================================================================
# Movie class (inheriting from db.Model class)
# ================================================================================
class Adventure(db.Model):
    """
    Adventure model
    """

    # Define all the Movie properties
    __tablename__ = "adventure"
    # Link Movie to User
    adventure_id = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True
    )
    title = db.Column(db.String(100), nullable=False)
    creator = db.Column(db.String(1000))
    description_link = db.Column(db.String, nullable=False)
    status = db.Column(db.String(100))
    poster_link = db.Column(db.String(100))
    difficulty_level = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"{
            self.adventure_id}: {
            self.title},\n {
            self.creator},\n {
            self.description_link},\n {
            self.status},\n {
            self.poster_link},\n {
            self.difficulty_level}, \n {
            self.is_active
            }"

    def __str__(self):
        return f"{
            self.adventure_id}: {
            self.title},\n {
            self.creator},\n {
            self.description_link},\n {
            self.status},\n {
            self.poster_link},\n {
            self.difficulty_level}, \n {
            self.is_active
            }"


# user_id = db.Column(
#         db.Integer,
#         db.ForeignKey("users.user_id"),
#         nullable=False)

class Student_Adventure(db.Model):
    """
    Student_Adventure model. This table embodies the N:N relationship between Student and Adventure.
    I.e. an adventure can be used by various students, and a student can use various adventures.
    """

    # Define all the Movie properties
    __tablename__ = "student_adventure"
    # Link Movie to User
    adventure_id = db.Column(
        db.Integer, db.ForeignKey("adventure.adventure_id"), primary_key=True
    )
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), primary_key=True
    )
    current_scene_id = db.Column(
        db.Integer, db.ForeignKey("scene.scene_id")
    )
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{
            self.adventure_id}: {
            self.student_id},\n {
            self.current_scene_id},\n {
            self.completed}"

    def __str__(self):
        return f"{
            self.adventure_id}: {
            self.student_id},\n {
            self.current_scene_id},\n {
            self.completed}"


class Scene(db.Model):
    """
     Scene model. This table holds references to all the available scenes. Together with adventure_id and scene_order_nr,
     it defines the exact adventure and order within that adventure. Note, 1 scene belongs to 1 adventure only.
     the exact
     """

    # Define all the Movie properties
    __tablename__ = "scene"
    # Link Movie to User
    scene_id= db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True
    )
    adventure_id = db.Column(
        db.Integer, db.ForeignKey("adventure.adventure_id")
    )
    persona_id = db.Column(
        db.Integer, db.ForeignKey("persona.persona_id")
    )
    scene_order_nr = db.Column(
        db.Integer, nullable=False, default=0
    )
    scene_description = db.Column(db.String)
    persona_mood = db.Column(db.String)
    stop_criteria = db.Column(db.String)
    scene_poster = db.Column(db.String(100))


    def __repr__(self):
        return f"{
        self.adventure_id}: {
        self.scene_id},\n {
        self.scene_order_nr},\n {
        self.scene_description},\n {
        self.persona_mood}, \n {
        self.stop_criteria} \n{
        self.scene_poster
        }"


    def __str__(self):
        return f"{
        self.adventure_id}: {
        self.scene_id},\n {
        self.scene_order_nr},\n {
        self.scene_description},\n {
        self.persona_mood}, \n {
        self.stop_criteria} \n{
        self.scene_poster
        }"


class Session(db.Model):
    """
     Session model. This table holds references to all the available scenes. Together with adventure_id and scene_order_nr,
     it defines the exact adventure and order within that adventure. Note, 1 scene belongs to 1 adventure only.
     the exact
     """

    # Define all the Movie properties
    __tablename__ = "session"
    # Link Movie to User
    session_id = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True
    )
    scene_id = db.Column(
        db.Integer, db.ForeignKey("scene.scene_id")
    )
    transcript = db.Column(db.String)
    corrected_transcript = db.Column(db.String)
    verbal_feedback_transcript = db.Column(db.String)
    detected_level = db.Column(db.String)

    def __repr__(self):
        return f"{
        self.session_id}: {
        self.scene_id},\n {
        self.feedback_id},\n {
        self.transcript}"

    def __str__(self):
        return f"{
        self.session_id}: {
        self.scene_id},\n {
        self.feedback_id},\n {
        self.transcript}"


class Persona(db.Model):
    """
     Persona model. This table holds references to all the available Personas and their traits and role.
     As such, a persona can be used for multiple scenes
     """

    # Define all the Movie properties
    __tablename__ = "persona"
    # Link Movie to User
    persona_id = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True
    )
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String, nullable=False)
    image = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"{
        self.persona_id}: {
        self.first_name},\n {
        self.last_name},\n {
        self.nationality},\n {
        self.gender},\n {
        self.age},\n {
        self.role},\n {
        self.image}"


    def __str__(self):
        return f"{
        self.persona_id}: {
        self.first_name},\n {
        self.last_name},\n {
        self.nationality},\n {
        self.gender},\n {
        self.age},\n {
        self.role},\n {
        self.image}"


