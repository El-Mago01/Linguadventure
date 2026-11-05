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
import datetime
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

# from app import app

db = SQLAlchemy()              #initialize SQLAlchemy
login_manager = LoginManager() #Initialize Flask-Login

# ================================================================================
# User class (inheriting from db.Model class)
# ================================================================================
class Student(UserMixin, db.Model):
    """
    Student model

    """

    __tablename__ = "student"
    student_id = db.Column(
        db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10))
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    age = db.Column(db.Integer)
    occupation = db.Column(db.String(100))
    original_language = db.Column(db.String(100))
    target_language = db.Column(db.String(100))
    current_level = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    # movies = db.relationship("Movie", backref="user", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.student_id)

    def __repr__(self):
        return f"{self.student_id}: {self.first_name} {self.last_name},\n"

    def __str__(self):
        return f"{self.student_id}: {self.first_name} {self.last_name},\n"

    def serialize(self):
        student_data = {}
        student_data["first_name"] = self.first_name
        student_data["last_name"] = self.last_name
        student_data["email"] = self.email
        student_data["password_hash"] = self.password_hash
        student_data["gender"] = self.gender
        student_data["age"] = self.age
        student_data["occupation"] = self.occupation
        student_data["original_language"] = self.original_language
        student_data["target_language"] = self.target_language
        student_data["current_level"] = self.current_level
        student_data["registration_date"] = self.registration_date
        student_data["is_admin"] = self.is_admin
        student_data["is_active"] = self.is_active
        student_data["student_id"] = self.student_id
        return student_data

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(Student, int(user_id))
    except (TypeError, ValueError):
        return None
# ================================================================================
# Adventure class (inheriting from db.Model class)
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
    creator = db.Column(db.String(100))
    language = db.Column(db.String(100))
    level = db.Column(db.String(10))
    setting = db.Column(db.String(200))
    premise = db.Column(db.String(200))
    intro = db.Column(db.String(200))
    objectives = db.Column(db.String(200))
    story_outline = db.Column(db.String(500))
    cliff_hanger = db.Column(db.String(200))
    poster_link = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"{
            self.adventure_id}: {
            self.title},\n {
            self.creator},\n {
            self.language},\n {
            self.level},\n {
            self.setting},\n {
            self.premise}, \n {
            self.objectives}, \n {
            self.story_outline}, \n {
            self.cliff_hanger}, \n {
            self.poster_link}, \n {
            self.is_active
            }"

    def __str__(self):
        return f"{
            self.adventure_id}: {
            self.title},\n {
            self.creator},\n {
            self.language},\n {
            self.level},\n {
            self.setting},\n {
            self.premise}, \n {
            self.objectives}, \n {
            self.story_outline}, \n {
            self.cliff_hanger}, \n {
            self.poster_link}, \n {
            self.is_active
            }"

    def serialize(self)->dict:
        adventure = {}
        adventure["adventure_id"] = self.adventure_id
        adventure["title"] = self.title
        adventure["creator"] = self.creator
        adventure["language"] = self.language
        adventure["level"] = self.level
        adventure["setting"] = self.setting
        adventure["premise"] = self.premise
        adventure["objectives"] = self.objectives
        adventure["story_outline"] = self.story_outline
        adventure["cliff_hanger"] = self.cliff_hanger
        adventure["poster_link"] = self.poster_link
        adventure["is_active"] = self.is_active
        return adventure

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
    title = db.Column(db.String(150))
    situation = db.Column(db.String)
    goal = db.Column(db.String)
    steps = db.Column(db.String)
    location = db.Column(db.String(100))
    intro = db.Column(db.String)
    vocabulary = db.Column(db.String(400))
    grammar = db.Column(db.String(400))
    must=db.Column(db.String(400))
    must_not=db.Column(db.String(400))
    exit = db.Column(db.String(400))
    ending=db.Column(db.String(400))

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
    description = db.Column(db.String(400), nullable=False)
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

    def serialize(self)->dict:
        persona_data = {}
        persona_data["persona_id"] = self.persona_id
        persona_data["first_name"] = self.first_name
        persona_data["last_name"] = self.last_name
        persona_data["nationality"] = self.nationality
        persona_data["description"] = self.description
        persona_data["gender"] = self.gender
        persona_data["age"] = self.age
        persona_data["role"] = self.role
        persona_data["image"] = self.image
        return persona_data


