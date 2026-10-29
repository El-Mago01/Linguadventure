import pytest
import helper_functions as hf
import os

"""
Test cases for helper_functions:
1 testing is_valid_email_address
1.1 
1.2 
1.3 
1.4 
1.5 
1.6 


2. 
2.1 
2.2 
2.3 
2.4 
2.5 

3 
3.1 
3.2 
3.3 
3.4 
3.5 
"""


@pytest.fixture
def test_init():
    emails = [
        ("user@example.com", True),
        ("john.doe@gmail.com", True),
        ("alice+newsletter@yahoo.com", True),
        ("bob123@outlook.com", True),
        ("support@company.co.uk", True),
        ("admin@subdomain.example.org", True),
        ("info@my-site.net", True),
        ("test.user+tag@domain.io", True),
        ("name@localhost", False),
        ("contact@long-domain-name.example.museum", True),
        ("a@b.cd", True),
        ("", False),
        ("user_name@domain-name.com", True),
        ("first.last@university.edu", True),
        ("hello@world.info", True),
        ("test123@my-domain.co", True),
        ("user@192.168.1.1", True),
        ("user.name@exam-ple.com", True),
        ("first+last@domain.co", True),
        ("user@xn--e1afmkfd.xn--p1ai", False),
        ("test@co", False),
        ("user@-invalid.com", False),
        ("user@.example.com", False),
        ("user@example..com", False),
        ('"quoted string"@example.com', False),
        ("user@exa mple.com", False)
    ]

    yield emails


    print('The Test is over!')


def test_1_1_a_valid_email_address(test_init):
    test_emails = test_init
    print(type(test_emails))
    for email, valid in test_emails:
        if hf.is_valid_email_address(email) != valid:
            print(email, valid)
        assert hf.is_valid_email_address(email) == valid

