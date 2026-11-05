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
    def get_all_adventures(sorting_command=None) -> list[Adventure]:
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
        sort_by = sorting_command.get("sort_by", "title")
        direction = sorting_command.get("direction", "asc")

        stmt = db.select(Adventure).where(Student_Adventure.student_id == student_id)
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

        # return None, "Error: adventure details could not be fetched. Please try again later"
        #     return new_adventure

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
        if not AdventureDataManager.adventure_exists(adventure_id):
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

    @staticmethod
    def update_adventure(adventure_id: int, updated_adventure_data:dict) -> Persona | None:
        """
        Update the user_name of the User object that has the provided user_id
        :param adventure_id:
        :param updated_adventure_data:
        :return:
        """
        if not isinstance(adventure_id, int):
            return None
        if not isinstance(updated_adventure_data, dict):
            return None
        if not AdventureDataManager.adventure_exists(adventure_id):
            return None
        stmt = db.select(Persona).where(Adventure.adventure_id == adventure_id)
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
        ad
        db.session.commit()
        return persona_to_update[0]

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
