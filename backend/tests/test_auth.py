import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database.database import get_db
from app.database.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def override_get_db(mock_db):
    try:
        yield mock_db
    finally:
        pass

@pytest.fixture(autouse=True)
def dependency_override(override_get_db):
    app.dependency_overrides[get_db] = lambda: override_get_db
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def mock_external_deps():
    with patch("app.handlers.auth.redis_client"), \
         patch("app.handlers.auth.get_password_hash", return_value="hashed"), \
         patch("app.handlers.auth.verify_password", return_value=True), \
         patch("app.handlers.auth.cache_user"):
        yield

# --- Вспомогательная функция настройки мока Query ---
def setup_mock_query(mock_db, first_return_value):
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    
    if isinstance(first_return_value, list):
        mock_query.first.side_effect = first_return_value
    else:
        mock_query.first.return_value = first_return_value
    return mock_query

# ----------------- TESTS -----------------

def test_register_user_success(mock_db):
    setup_mock_query(mock_db, None)
    
    # Настраиваем refresh: он должен проставить ID и дату
    def side_effect_refresh(user_obj):
        user_obj.id = 1
        user_obj.registration_date = "2023-01-01T00:00:00"
        user_obj.is_verified = False
        user_obj.is_admin = False
    
    mock_db.refresh.side_effect = side_effect_refresh
    
    payload = {"name": "newuser", "email": "new@test.com", "password": "StrongPassword1!"}
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]

def test_register_user_email_conflict(mock_db):
    setup_mock_query(mock_db, User(id=1, email="exists@test.com"))

    payload = {
        "name": "unique", 
        "email": "exists@test.com", 
        "password": "StrongPassword1!"
    }
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 409
    assert "email already exists" in response.json()["detail"]

def test_register_user_login_conflict(mock_db):
    setup_mock_query(mock_db, [None, User(id=1, name="exists")])

    payload = {
        "name": "exists",
        "email": "unique@test.com",
        "password": "StrongPassword1!"
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "login already exists" in response.json()["detail"]

def test_login_invalid_credentials(mock_db):
    setup_mock_query(mock_db, None)

    response = client.post("/auth/login", data={"username": "w@w.com", "password": "a"})
    
    assert response.status_code == 401
    assert response.json()["detail"] in ["Incorrect username or password", "Wrong email or password"]

def test_login_success(mock_db):
    user = User(
        id=1, 
        email="test@test.com", 
        hashed_password="hashed",
        is_admin=False, 
        is_verified=True
    )
    setup_mock_query(mock_db, user)

    form_data = {"username": "test@test.com", "password": "P!"}
    response = client.post("/auth/login", data=form_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_validation_error():
    payload = {"name": "user", "email": "test@test.com", "password": "123"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422

def test_logout_success():
    payload = {"refresh_token": "token"}
    response = client.post("/auth/logout", json=payload)
    assert response.status_code == 200
