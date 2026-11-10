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
from src.adventures.data_manager import AdventureDataManager, PersonaDataManager
from src.site_landing.data_manager import StudentDataManager
from sqlalchemy import and_

from models import db, Adventure, Student, Student_Adventure, Persona, Scene



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



    # =========================================================================
    # -------------------------------------------------------------------------
    # ************************** FeedbackDataManager *************************
    # -------------------------------------------------------------------------
    # =========================================================================

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