""""
How does class instantiation work when you don't use the __init__ method?

"""
from flask_sqlalchemy import SQLAlchemy

# from app import app

db = SQLAlchemy()
#

class WorkingClass():

    test = True
    def __init__(self):
        pass
    @staticmethod
    def test_true():
        return test

    @staticmethod
    def test_of_test_true():
        return WorkingClass.test_true()

test = WorkingClass()
test.test=False
print(test.test_of_test_true())
