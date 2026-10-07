import pytest

from app import create_app
from models import db
from pathlib import Path

# PROJECT_DIR = Path(__file__).resolve().parents[1]
# TEST_DB = PROJECT_DIR / "data" / "test_db.sqlite"

@pytest.fixture
def test_app():
    print("\n>>> ENTERING TEST_APP")
    print("DB inside conftest:", id(db))
    app = create_app(f"sqlite:///../../data/test_db.sqlite")
    app.config["TESTING"] = True

    with app.app_context():

        db.create_all()

        yield app, db

        db.session.remove()
        db.drop_all()