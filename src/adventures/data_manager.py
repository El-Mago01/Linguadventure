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
from src.site_landing.data_manager import StudentDataManager as sdm
from sqlalchemy import and_

from models import db, Adventure, Student, Student_Adventure, Persona, Scene

# from adventure_data_fetcher import fetch_adventure_general_data, fetch_adventure_data

# =========================================================================
# -------------------------------------------------------------------------
# ************************** AdventureDataManager *************************
# -------------------------------------------------------------------------
# =========================================================================

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
    def create_adventure(adventure: dict, creator) -> tuple[Adventure|None, str]:
        """
        The received adventure needs to be split apart and then stored in the various databases.

        :param : adventure, a dict which includes the adventure and scene details
        :return: 
        """
        if not isinstance(adventure, dict):
            return None, "Error: Invalid adventure details"

        if len(adventure) == 0:
            return None, "Error: Invalid adventure details"

        print(adventure)

        new_adventure = Adventure(
            title = adventure.get("title",""),
            creator = creator,
            language = adventure.get("language",""),
            level = adventure.get("level",""),
            setting = adventure.get("setting",""),
            premise = adventure.get("premise",""),
            objectives = adventure.get("objectives",""),
            story_outline = adventure.get("storyOutline",""),
            cliff_hanger = adventure.get("cliffhanger",""),
            poster_link = adventure.get("poster_link",""),
            is_active = adventure.get("is_active", False)
        )
        db.session.add(new_adventure)

        # db.session.flush sends the INSERT to the database so movie.movie_id is generated,
        # but the transaction is not permanently committed yet. Commitment follows at
        # db.session.commit
        db.session.flush()
        print(new_adventure.adventure_id)
        if not new_adventure.adventure_id:
            return None, "Adventure ID not generated"
        count = 0
        for scene in adventure.get("scenes", []):
            if not scene.get("persona_id", ""):
                return (None,
                    f"Persona ID not provided for scene {count+1} with title: {scene.get('title', 'no title provided')}")
            if not scene.get("title", ""):
                return (None,
                    f"No title provided for scene {count+1}")
            if not scene.get("steps",""):
                return (None,
                        f"No steps provided for scene {count+1}")
            new_scene = Scene(
                adventure_id = new_adventure.adventure_id,
                title = scene.get("title","no title provided"),
                persona_id = scene.get("persona_id", ""),
                scene_order_nr = count+1,
                situation = scene.get("situation", ""),
                goal = scene.get("goal", ""),
                steps = scene.get("steps", ""),
                location = scene.get("location", ""),
                intro = scene.get("intro", ""),
                vocabulary = scene.get("vocabulary", ""),
                grammar = scene.get("grammar", ""),
                must = scene.get("must", ""),
                must_not = scene.get("mustNot", ""),
                exit =scene.get("exit", ""),
                ending = scene.get("ending", ""),
            )
            count += 1
            db.session.add(new_scene)
            db.session.flush()
            print(f"new_scene.scene_id: {new_scene.scene_id}")

        db.session.commit()
        return (
            new_adventure, f"Adventure {new_adventure.adventure_id}: {new_adventure.title} created successfully!",)


    @staticmethod
    def get_all_adventures(sorting_command=None) -> list[dict]  |None:
        """
        Interface function for searching for adventures with a specific title within the imdb web-site.
        The search is actually performed by the adventure_data_fetcher module.
        :param adventure_title:
        :return:
        """

        if sorting_command is None:
            sorting_command = {"sort_by": "title", "direction": "asc"}

        sort_by = sorting_command.get("sort_by", "title")
        direction = sorting_command.get("direction", "asc")

        stmt = db.select(Adventure)
        if sort_by == "title":
            if direction == "asc":
                stmt = stmt.order_by(Adventure.title.asc())
            else:
                stmt = stmt.order_by(Adventure.title.desc())
        else:
            if direction == "asc":
                stmt = stmt.order_by(Adventure.creator.asc())
            else:
                stmt = stmt.order_by(Adventure.creator.desc())

        all_adventures = db.session.execute(stmt).scalars().all()
        all_serialized_adventures = [adventure.serialize() for adventure in all_adventures]
        all_adventures = []
        for a_serialized_adventure in all_serialized_adventures:
            stmt = db.select(Scene).join(Adventure, Adventure.adventure_id == a_serialized_adventure.get("adventure_id",-1))
            scenes = db.session.execute(stmt).scalars().all()
            if len(scenes) < 1:
                return None
            a_serialized_adventure["scenes"] = [scene.serialize() for scene in scenes]
            all_adventures.append(a_serialized_adventure)
        print(all_adventures)
        return all_adventures


    @staticmethod
    def get_all_student_adventures(student_id: int, sorting_command: dict|None=None) -> list[dict] | None:
        """
        returns a list of all adventures for the active Student
        :return:
        """
        if sorting_command is None:
            sorting_command = {"sort_by": "title", "direction": "asc"}

        sort_by = sorting_command.get("sort_by", "title")
        direction = sorting_command.get("direction", "asc")

        stmt = db.select(Adventure).join(Student_Adventure, Student.student_id==student_id)
        if sort_by == "title":
            if direction == "asc":
                stmt = stmt.order_by(Adventure.title.asc())
            else:
                stmt = stmt.order_by(Adventure.title.desc())
        else:
            if direction == "asc":
                stmt = stmt.order_by(Adventure.creator.asc())
            else:
                stmt = stmt.order_by(Adventure.creator.desc())

        all_adventures = db.session.execute(stmt).scalars().all()
        all_serialized_adventures = [adventure.serialize() for adventure in all_adventures if adventure.is_active]
        all_adventures = []
        for a_serialized_adventure in all_serialized_adventures:
            stmt = db.select(Scene).join(Adventure,
                Adventure.adventure_id == a_serialized_adventure.get("adventure_id", -1))
            scenes = db.session.execute(stmt).scalars().all()
            if len(scenes) < 1:
                return None
            a_serialized_adventure["scenes"] = [scene.serialize() for scene in scenes]
            all_adventures.append(a_serialized_adventure)
        print(all_adventures)
        return all_adventures


    @staticmethod
    def get_adventure(adventure_id: int) -> dict | None:
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
        an_adventure = adventure.serialize()
        an_adventure["scenes"] = AdventureDataManager.get_all_scenes(adventure_id)
        return an_adventure


    @staticmethod
    def adventure_exists(adventure_id: int) -> bool:
        """
        Checks if the received adventure_id exists in the database
        :param adventure_id: 

        :return: boolean -> True if the adventure exists, False otherwise
        """
        if not isinstance(adventure_id, int):
            return False
        stmt = db.select(Adventure).where(Adventure.adventure_id == adventure_id)
        existing_adventures = db.session.execute(stmt).scalars().all()

        if len(existing_adventures) == 1:
            return True
        return False


    @staticmethod
    def update_adventure(adventure_id: int, updated_adventure_data:dict) -> Adventure | None:
        """
        Update the user_name of the User object that has the provided user_id
        :param adventure_id:
        :param updated_adventure_data:
        :return:
        """
        if not isinstance(adventure_id, int):
            if not isinstance(adventure_id, str):
                return None
        try:
            adventure_id = int(adventure_id)
        except ValueError:
            return None
        if not isinstance(updated_adventure_data, dict):
            return None
        if not AdventureDataManager.adventure_exists(adventure_id):
            return None
        stmt = db.select(Adventure).where(Adventure.adventure_id == adventure_id)
        adventure_to_update = db.session.execute(stmt).scalars().all()
        if len(adventure_to_update) != 1:
            return None

        adventure_to_update[0].title = updated_adventure_data.get("title",adventure_to_update[0].title)
        adventure_to_update[0].creator = updated_adventure_data.get("creator", adventure_to_update[0].creator)
        adventure_to_update[0].language = updated_adventure_data.get("language", adventure_to_update[0].language)
        adventure_to_update[0].minutes = updated_adventure_data.get("minutes", adventure_to_update[0].minutes)
        adventure_to_update[0].premise = updated_adventure_data.get("premise", adventure_to_update[0].premise)
        adventure_to_update[0].intro = updated_adventure_data.get("intro", adventure_to_update[0].intro)
        adventure_to_update[0].objectives = updated_adventure_data.get("objectives", adventure_to_update[0].objectives)
        adventure_to_update[0].story_outline = updated_adventure_data.get("storyOutline", adventure_to_update[0].story_outline)
        adventure_to_update[0].cliff_hanger = updated_adventure_data.get("cliffhanger", adventure_to_update[0].cliff_hanger)
        adventure_to_update[0].scenes = []

        for scene in updated_adventure_data.get("scenes", []):
            adventure_to_update[0].scenes.append(scene)

        db.session.commit()
        return adventure_to_update[0]


    @staticmethod
    def act_deact_adventure(adventure_id: int, act_deact: bool) -> bool:
        """
        Activates or deactivates the adventure indicated via the adventure_id

        :param adventure_id: adventure identifier
        :param act_deact: boolean -> True if the adventure should be activated, False otherwise
        :return: The Adventure object fitting the adventure_id or None if the adventure does not exist in the DB
        """

        if not isinstance(adventure_id, int):
            return False
        if not isinstance(act_deact, bool):
            return False
        stmt = db.select(Adventure).where(Adventure.adventure_id == adventure_id)
        selected_adventure = db.session.execute(stmt).scalars().one_or_none()

        if not selected_adventure:
            return False
        selected_adventure.is_active = act_deact
        db.session.commit()
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
        if not AdventureDataManager.adventure_exists(adventure_id):
            return None
        try:
            stmt = db.select(Adventure).where(Adventure.adventure_id == adventure_id)
            adventure_to_delete = db.session.execute(stmt).scalars().one_or_none()
            db.session.delete(adventure_to_delete)
            db.session.flush()
            if adventure_to_delete is None:
                return None

            stmt = db.select(Scene).where(Scene.adventure_id == adventure_id)
            scenes_to_delete = db.session.execute(stmt).scalars().all()
            for scene_to_delete in scenes_to_delete:
                db.session.delete(scene_to_delete)
                db.session.flush()
            if commit:
                db.session.commit()
        except OperationalError:
            logging.error(
                f"Fatal error while deleting adventure {adventure_id} from database")
            db.session.rollback()
            return None

        return adventure_to_delete


    @staticmethod
    def reserve_adventure(adventure_id: int, student_id: int) -> tuple[list[Student_Adventure] | None, str]:
        """
        Reserves an adventure for a student and returns the student adventure object
        The status_code that is stored in the student_adventure object has the following codification:
        Each character in the status_code represents the status of a scene played by a student.
        '0' indicates that the scene is blocked,
        '1' indicates that the scene is available
        '2' indicates that the scene was already played by the student.

        E.g. status_code = "2100" means:
        Scene 0 was already played by the student
        Scene 1 is available to be played by the student
        Scene 2 is blocked
        Scene 3 is blocked

        The initial code for a 4 scene adventure is : "1000
        """
        if not AdventureDataManager.adventure_exists(adventure_id):
            return None, "Adventure does not exist"

        if not sdm.student_exists(student_id):
            return None, "Student does not exist"

        adventure = AdventureDataManager.get_adventure(adventure_id)
        if adventure is None:
            return None, f"Adventure with id {adventure_id} is not found"
        if not adventure.get("is_active", False):
            return None, "Adventure is not active"

        if not sdm.student_is_active(student_id):
            return None, "Student is not active"

        # check if the student has already reserved this adventure
        if AdventureDataManager.student_adventure_exists(student_id, adventure_id):
            student_adventure = AdventureDataManager.get_student_adventure(student_id, adventure_id)
            return student_adventure, "Student has already reserved this adventure"

        nr_of_scenes=AdventureDataManager.get_number_of_scenes(adventure_id)
        status_code = "1"
        for i in range(1, nr_of_scenes):
            status_code += "0"

        new_student_adventure = Student_Adventure(
            adventure_id=adventure_id,
            student_id=student_id,
            current_scene_id=-1,  # No current_scene selected yet
            status=status_code,
        )
        try:
            db.session.add(new_student_adventure)
            db.session.commit()
        except OperationalError as e:
            return None, f"New student_adventure could not be stored in table: {e}"

        return [new_student_adventure], "Storage successful!"

    @staticmethod
    def get_full_student_adventure_data(adventure_id, student_id) -> tuple[dict | None, str]:

        if not AdventureDataManager.adventure_exists(adventure_id):
            return None, "Adventure does not exist"

        if not sdm.student_exists(student_id):
            return None, "Student does not exist"

        try:
            stmt = (
                db.select(Student_Adventure, Student, Adventure)
                .select_from(Student_Adventure)
                .join(Student, Student_Adventure.student_id == Student.student_id)
                .join(Adventure, Student_Adventure.adventure_id == Adventure.adventure_id)
                .where(
                    Student_Adventure.adventure_id == adventure_id,
                    Student_Adventure.student_id == student_id,
                )
            )
            full_student_overview = db.session.execute(stmt).all()

        except OperationalError as e:
            return {}, f"Could not fetch the data from the database: See also error description\n {e}"
        student_adventure, student, adventure = full_student_overview[0]


        print(f"{student_adventure}\n\n\n{student}\n\n\n {adventure}")
        student_adventure_d = student_adventure.serialize()
        student_d = student.serialize()
        adventure_d = adventure.serialize()
        all_scenes = AdventureDataManager.get_all_scenes(adventure_id)
        all_scenes_status = student_adventure_d.get("status","")
        if len(all_scenes) != len(all_scenes_status):
            return {}, f"Student adventure data retrieval failed: The number of scenes ({len(all_scenes)})do not match with the length of status (len(all_scenes_status))"
        for scene in all_scenes:
            # Decide if this scene should be locked or available and if it can be played
            this_scene_status =  all_scenes_status[0]
            all_scenes_status = all_scenes_status[1:]
            if this_scene_status == "0":
                scene["status"] = "locked"
                scene["can_play"] = False
            elif this_scene_status == "1":
                scene["status"] = "available"
                scene["can_play"] = True
            elif this_scene_status == "2":
                scene["status"] = "completed"
                scene["can_play"] = True
            else:
                return {}, "Student adventure data retrieval failed: Invalid status value"
            # Per scene fetch the persona
            persona_id = scene.get("persona_id", -1)
            persona = PersonaDataManager.get_persona(persona_id)
            if persona:
                scene["persona"] = persona.serialize()
            else:
                scene["persona"] = {}
        adventure_d["scenes"] = all_scenes
        return student_adventure_d | student_d | adventure_d, "Student adventure data retrieval successful"

    @staticmethod
    def change_adventure_status(adventure_id: int, student_id: int, new_status: str) -> tuple[bool, str]:
        """
        the following status are allowed:
        "Reserved", "
        """
        if not AdventureDataManager.adventure_exists(adventure_id):
            return False, "Status not changed: adventure does not exist"

        if not sdm.student_exists(adventure_id):
            return False, "Status not changed: student does not exist"

        if len(new_status) != AdventureDataManager.get_number_of_scenes(adventure_id):
            return False, "Status not changed, new status setting not allowed."

        for char in new_status:
            if char not in ["0", "1", "2"]:
                return False, "Status not changed, new status setting not allowed."

        if not AdventureDataManager.student_adventure_exists(adventure_id, student_id):
            return False, "Status not changed, student_adventure entry does not exist"
        try:
            a_student_adventure = AdventureDataManager.get_student_adventure(adventure_id, student_id)
            a_student_adventure.status = new_status
            db.session.add(a_student_adventure)
            db.session.commit()
        except OperationalError as e:
            return False, "Status not change, could not store the Student_Adventure data"

        return True, "Status changed"


    @staticmethod
    def student_adventure_exists(adventure_id: int, student_id: int) -> bool:

        """
        Checks if the received adventure_id and student_id exists in the database
        :param adventure_id:
        :param student_id:

        :return: boolean -> True if the adventure exists, False otherwise
        """
        if not isinstance(adventure_id, int):
            return False

        if not AdventureDataManager.adventure_exists(adventure_id):
            return False
        if not sdm.student_exists(student_id):
            return False

        stmt = db.select(Student_Adventure).where(and_(
            Student_Adventure.adventure_id == adventure_id,
            Student_Adventure.student_id))
        existing_adventures = db.session.execute(stmt).scalars().all()

        if len(existing_adventures) < 1:
            return False
        return True

    @staticmethod
    def get_student_adventure(adventure_id: int, student_id: int) -> list[Student_Adventure] | None:
        """
        get the specific student_adventure. As such, if more than 1 student_adventures exist, all found elements will
        be returned. If not found and empty
        :param adventure_id:
        :param student_id:
        :return:
        """
        if not isinstance(adventure_id, int):
            return None

        if not isinstance(student_id, int):
            return None

        if not AdventureDataManager.adventure_exists(adventure_id):
            return None

        if not sdm.student_exists(adventure_id):
            return None

        stmt = db.select(Student_Adventure).where(and_(
            Student_Adventure.adventure_id == adventure_id), Student_Adventure.student_id == student_id)
        existing_student_adventures = db.session.execute(stmt).scalars().all()

        return existing_student_adventures


    # =========================================================================
# -------------------------------------------------------------------------
# *************************** SCENE RELATED DATA **************************
# -------------------------------------------------------------------------
# =========================================================================



    # =========================================================================
    # All method definitions related to scenes management
    # =========================================================================

    @staticmethod
    def get_number_of_scenes(adventure_id: int) -> int:
        """
        Derive the number of scenes that exists for a specific adventure.
        :param adventure_title:
        :return:
        """

        if not isinstance(adventure_id, int):
            return -1

        stmt = db.select(Scene).join(Adventure, Adventure.adventure_id == adventure_id)
        scenes = db.session.execute(stmt).all()
        return len(scenes)

    @staticmethod
    def scene_exists(adventure_id: int, scene_id: int) -> bool:
        """
        Checks if the received adventure_id and student_id exists in the database
        :param adventure_id:

        :return: boolean -> True if the adventure exists, False otherwise
        """
        if not isinstance(adventure_id, int):
            return False

        if not AdventureDataManager.adventure_exists(adventure_id):
            return False

        stmt = db.select(Student_Adventure).where(and_(
            Student_Adventure.adventure_id == adventure_id,
            Scene.scene_id == scene_id))
        existing_adventures = db.session.execute(stmt).scalars().all()

        if len(existing_adventures) < 1:
            return False
        return True


    @staticmethod
    def set_current_scene(adventure_id:int, student_id:int, current_scene: int) -> tuple[bool, str]:
        """
        the following status are allowed:
        "Reserved", "
        """
        if not AdventureDataManager.adventure_exists(adventure_id):
            return False, "Current scene not changed: adventure does not exist"

        if not sdm.student_exists(adventure_id):
            return False, "Current scene not changed: student does not exist"

        if not AdventureDataManager.student_adventure_exists(adventure_id, student_id):
            return False, "The adventure is not yet assigned to this student"

        if not isinstance(current_scene):
            return False, "Current scene not changed, new scene has wrong input type"

        if not AdventureDataManager.scene_exists(current_scene):
            return False, "Current scene not changed, new scene does not exist."

        a_student_adventure = AdventureDataManager.get_student_adventure(adventure_id, student_id)
        a_student_adventure.current_scene = current_scene
        try:
            db.session.add(a_student_adventure)
            db.session.commit()
        except OperationalError as e:
            return False, "Status not change, could not store the Student_Adventure data"

        return True, "current_scene allocated"


    @staticmethod
    def get_all_scenes(adventure_id:int)-> list[dict|None]:
        if not isinstance(adventure_id, int):
            return []

        try:
            stmt = db.select(Scene).where(
                Scene.adventure_id == adventure_id)
            scenes = db.session.execute(stmt).scalars().all()
            if len(scenes) < 1:
                return []
            return [scene.serialize() for scene in scenes]
        except OperationalError as e:
            return []


# =========================================================================
# -------------------------------------------------------------------------
# *************************** PersonaDataManager **************************
# -------------------------------------------------------------------------
# =========================================================================

class PersonaDataManager:
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
        # All class definitions related to persona handling
        # =========================================================================
        @staticmethod
        def get_all_personas(sorting_command=None) -> list[Persona]:
            """
            Interface function for searching for adventures with a specific title within the imdb web-site.
            The search is actually performed by the adventure_data_fetcher module.
            :param adventure_title:
            :return:
            """
            if sorting_command is None:
                sorting_command = {"sort_by": "title", "direction": "asc"}
            sort_by = sorting_command.get("sort_by", "title")
            direction = sorting_command.get("direction", "asc")
            stmt = db.select(Persona)
            if sort_by == "first_name":
                if direction == "asc":
                    stmt = stmt.order_by(Persona.first_name.asc())
                else:
                    stmt = stmt.order_by(Persona.first_name.desc())
            else:
                if direction == "asc":
                    stmt = stmt.order_by(Persona.last_name.asc())
                else:
                    stmt = stmt.order_by(Persona.last_name.desc())
            all_personas = db.session.execute(stmt).scalars().all()
            return all_personas

        @staticmethod
        def get_persona(persona_id: int) -> Persona | None:
            """
            returns a adventure object with the provided persona_id or none if the persona_id is not found.
            :param persona_id:
            :return:
            """
            if isinstance(persona_id, int):
                if PersonaDataManager.persona_exists(persona_id):
                    stmt = db.select(Persona).where(
                        Persona.persona_id == persona_id)
                else:
                    return None
            else:
                return None
            persona = db.session.execute(stmt).scalars().one()
            return persona

        @staticmethod
        def create_persona(persona: dict) -> tuple[Persona|None, str]:
            """
            Stores a new persona in the database.

            :param :
            :return:
            """
            if not isinstance(persona, dict):
                return None, "received persona is not a string"

            if len(persona) != 0:
                new_persona = Persona(
                    first_name=persona.get("first_name", ""),
                    last_name=persona.get("last_name", ""),
                    nationality=persona.get("nationality", ""),
                    description=persona.get("description", ""),
                    gender=persona.get("gender", ""),
                    age=persona.get("age", ""),
                    role=persona.get("role",""),
                    image=persona.get("image","")
                )
                db.session.add(new_persona)

                # db.session.flush sends the INSERT to the database so movie.movie_id is generated,
                # but the transaction is not permanently committed yet. Commitment follows at
                # db.session.commit
                db.session.flush()
                db.session.commit()
                return (
                    new_persona, f"persona {new_persona.first_name} {new_persona.last_name} created successfully!",)
            return None, "Error: adventure details could not be fetched. Please try again later"

        @staticmethod
        def persona_exists(persona_id: int) -> bool:
            """
            Checks if the received persona_id exists in the database
            :param persona_id:

            :return: boolean -> True if the persona exists, False otherwise
            """

            if isinstance(persona_id, int):
                stmt = db.select(Persona).where(Persona.persona_id == persona_id)
            else:
                return False
            existing_adventures = db.session.execute(stmt).scalars().all()

            if len(existing_adventures) != 0:
                return True
            return False

        @staticmethod
        def delete_persona(persona_id: int, commit: bool = True) -> Persona | None:
            """
            Deletes the persona from the persona table

            :param persona_id: persona identifier
            :param commit: An indicator if the commit should be given or if the commit will be
                           done outside of this function (i.e. commit = False)

            :return: The Persona object fitting the persona_id or None if the persona does not exist in the DB
            """
            if not isinstance(persona_id, int):
                return None
            if not PersonaDataManager.persona_exists(persona_id):
                return None
            stmt = db.select(Persona).where(Persona.persona_id == persona_id)
            persona_to_delete = db.session.execute(stmt).scalars().one_or_none()
            if persona_to_delete is None:
                return None
            try:
                db.session.delete(persona_to_delete)
                if commit:
                    db.session.commit()
            except OperationalError:
                logging.error(
                    f"Fatal error while deleting adventure {persona_id} from database")
                db.session.rollback()
                return None

            return persona_to_delete


        @staticmethod
        def update_persona(persona_id: int, updated_persona_data:dict) -> Persona | None:
            """
            Update the user_name of the User object that has the provided user_id
            :param persona_id:
            :param new_user_name:
            :return:
            """
            if not isinstance(persona_id, int):
                if not isinstance(persona_id, str):
                    return None
            try:
                persona_id = int(persona_id)
            except ValueError:
                return None
            if not isinstance(updated_persona_data, dict):
                return None
            if not PersonaDataManager.persona_exists(persona_id):
                return None
            stmt = db.select(Persona).where(Persona.persona_id == persona_id)
            persona_to_update = db.session.execute(stmt).scalars().all()
            if len(persona_to_update) != 1:
                return None

            persona_to_update[0].first_name = updated_persona_data.get("first_name",persona_to_update[0].first_name)
            persona_to_update[0].last_name = updated_persona_data.get("last_name",persona_to_update[0].last_name)
            persona_to_update[0].age = updated_persona_data.get("age", persona_to_update[0].age)
            persona_to_update[0].role = updated_persona_data.get("role", persona_to_update[0].role)
            persona_to_update[0].nationality = updated_persona_data.get("nationality", persona_to_update[0].nationality)
            persona_to_update[0].description = updated_persona_data.get("description", persona_to_update[0].description)
            persona_to_update[0].gender = updated_persona_data.get("gender", persona_to_update[0].gender)
            persona_to_update[0].last_name = updated_persona_data.get("last_name", persona_to_update[0].last_name)
            db.session.commit()
            return persona_to_update[0]

