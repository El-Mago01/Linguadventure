import re
import os
from src.data_manager import DataManager, logging

dm = DataManager()

def is_valid_email_address(email:str) -> bool:
    """
    This function checks if the given email address is a valid one.
    :param email:
    :return:
    """
    pattern = r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*"
    return re.fullmatch(pattern, email) is not None

def check_admin_user(email:str) -> bool:
    """
    This function checks if this user's email address is located in the .admin file.
    If it is, True is returned, otherwise False. Typically, the client application can then use
    'promote_to_admin' to promote users to admins.
    :param email:
    :return:
    """
    if not is_valid_email_address(email):
        return False
    if os.path.exists("../.admin"):
        with open("../.admin", 'r') as file:
            admin_mail_addresses = file.readlines()
            if email in admin_mail_addresses:
                return True
            return False
    return False

def promote_admin_users():
    """
    Upon startup of the app, each line within the .admin file is scanned.
    if the line contains an email address, it is checked in the database if
    a student with that email address exists. If it does, it is promoted to admin
    :return:
    """
    print("This is the current directory: ",os.getcwd())
    if os.path.exists("../.admin"):
        with open("../.admin", 'r') as file:
            admin_mail_addresses = file.readlines()
            list_valid_admin_addresses = []
            for email in admin_mail_addresses:
                if is_valid_email_address(email):
                    list_valid_admin_addresses.append(email)
            if len(list_valid_admin_addresses) > 0:
                for email in list_valid_admin_addresses:
                    if dm.student_exists(email):
                        dm.make_admin(email)
                        logging.info(f"User with {email} has been promoted to admin")


def promote_to_admin(email):

    if check_admin_user(email):
        if dm.student_exists(email):
            dm.make_admin(email)
            logging.info(f"User with {email} has been promoted to admin")
            return True
    return False