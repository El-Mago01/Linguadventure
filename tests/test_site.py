import pytest
import app
import os
from data_manager import DataManager, StudentStorageError

"""
Test cases for site landing:
1 A user lands on the site
1.1 user receives welcoming site page 
1.2 New user registers as Student
    1.2.1 Data of new user is retrieved
    
1.3 New user register as student with existing email address
1.4 New user register without an email address
1.5 New user register without a first name
1.6 New user registers without a last name


2. A registered user logs on
2.1 A registered student logs on to the web-page.
2.2 
2.3 
2.4 
2.5 

3 A new user registers
3.1 new user clicks new user registration and receives a form where he can register with
3.2 
3.3 
3.4 
3.5 
"""


@pytest.fixture
def test_init(test_app):
    test_app, test_db = test_app
    print("\n>>> ENTERING TEST_INIT")
    client = test_app.test_client()
    database_file = "data/test_db.sqlite"
    # if os.path.exists(database_file):
    #     os.remove(database_file)
    registration_info = {
        "first_name": "First",
        "last_name": "Last",
        "email": "Martin@example.com",
        "gender": "Male",
        "age": 18,
        "occupation": "",
        "original_language": "English",
        "target_language": "Portuguese",
        "current_level": "0"
    }
    # app.app_context


    yield test_app, client, database_file, registration_info

    test_db.drop_all()
    test_db.create_all()
    print('The Test is over!')


def test_1_1_a_user_on_site(test_init):
    test_app, client, database_file, registration_info = test_init
    response = client.get("/")
    html = response.data.decode()
    print(type(response))
    print(type(response.data))
    assert os.path.exists(database_file)
    assert response.status_code == 200
    assert "Login" in html
    assert "Email" in html

def test_1_2_store_new_student(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    new_student = dm.add_student(registration_info=registration_info)
    print("INSTANCE PATH:", test_app.instance_path)
    print("DB URI:", test_app.config["SQLALCHEMY_DATABASE_URI"])
    assert new_student is not None
    assert new_student.student_id == 1
    assert os.path.exists(database_file)
    assert new_student.email == registration_info["email"]
    assert dm.student_exists(new_student.student_id) == True    #This time using the student_id

def test_1_2_1_fetch_stored_student_info(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    new_student = dm.add_student(registration_info=registration_info)
    assert new_student is not None
    assert dm.student_exists(new_student.email) == True    #This time using the email address
    verified_stored_student = dm.get_student(registration_info["email"])
    assert new_student is not None
    assert verified_stored_student is not None
    assert new_student.student_id == verified_stored_student.get("student_id","-1")
    assert os.path.exists(database_file)
    assert new_student.email == registration_info["email"]

def test_1_3_store_new_student_with_existing_email(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    new_student = dm.add_student(registration_info=registration_info)

    print("INSTANCE PATH:", test_app.instance_path)
    print("DB URI:", test_app.config["SQLALCHEMY_DATABASE_URI"])
    assert new_student is not None
    assert new_student.student_id == 1
    assert os.path.exists(database_file)
    assert dm.student_exists(new_student) == False   #This time using the student object
    assert dm.student_exists(registration_info["email"]) == True   #This time using the student object
    assert new_student.email == registration_info["email"]
    with pytest.raises(StudentStorageError, match="Email address already exists in StudentDB"):
        another_student = dm.add_student(registration_info=registration_info)
        assert another_student is None

def test_1_4_store_new_student_without_an_email(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    registration_info["email"] = ""
    with pytest.raises(StudentStorageError, match="No valid email address received"):
        new_student = dm.add_student(registration_info=registration_info)
        assert new_student is None
    assert os.path.exists(database_file)

def test_1_5_store_new_student_without_a_first_name(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    registration_info["first_name"] = ""
    with pytest.raises(StudentStorageError, match="No valid first or last name received"):
        new_student = dm.add_student(registration_info=registration_info)
        assert new_student is None
    assert os.path.exists(database_file)

def test_1_6_store_new_student_without_a_last_name(test_init):
    test_app, client, database_file, registration_info = test_init
    print(type(registration_info))
    dm = DataManager()
    registration_info["last_name"] = ""
    with pytest.raises(StudentStorageError, match="No valid first or last name received"):
        new_student = dm.add_student(registration_info=registration_info)
        assert new_student is None
    assert os.path.exists(database_file)

# @pytest.fixture
# def test_init():
#     initial_blog_posts = [
#         {
#             "id": 1,
#             "author": "John Doe",
#             "title": "First Post",
#             "content": "This is my first post.",
#         },
#         {
#             "id": 2,
#             "author": "Jane Doe",
#             "title": "Second Post",
#             "content": "This is another post.",
#         },
#     ]
#     json_data_file = "data/We Love Ajax.json"
#     if os.path.exists(json_data_file):
#         os.remove(json_data_file)
#     test_blog = app.Blog("We Love Ajax")
#     app.blog = test_blog  # This is needed to make the 'blog' variable in app to the test_blog here
#     for test_post in initial_blog_posts:
#         test_blog.set(test_post)
#     app.app.config["TESTING"] = True
#     with app.app.test_client() as client:
#         yield client, test_blog
#         # print('The Test is over!')
#
#
# def test_1_1_create_blog_with_2_posts_1(test_init):
#     client, test_blog = test_init
#     response = client.get("/")
#     html = response.data.decode()
#     print(type(response))
#     print(type(response.data))
#     assert len(test_blog.get_all_posts()) == 2
#     assert response.status_code == 200
#     assert test_blog.get_name() == "We Love Ajax"
#     assert "<title>We Love Ajax</title>" in html
#     assert "John" in html
#     assert "Jane" in html