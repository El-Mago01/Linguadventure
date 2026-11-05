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

from models import db, Adventure, Persona, Student_Adventure



