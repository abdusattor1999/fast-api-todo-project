from .utils import *
from src.app.router.auth import get_db, authenticate, ALGORITHM, SECRET_KEY, get_token_for_user, get_current_user
from datetime import timedelta
from jose import jwt
import pytest

app.dependency_overrides[get_db] = override_get_db

def test_authenticate(test_user):
    db = TestSessionLocal()
    authenticated_user = authenticate(test_user.username, "password1313", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username


    non_exist_user = authenticate("Random username", "password1313", db)
    assert non_exist_user is None

    wrong_password_user = authenticate(test_user.username, "wrong password", db)
    assert wrong_password_user is None

def test_create_access_token(test_user):
    expires_delta = timedelta(days=3)
    token = get_token_for_user(test_user, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature':False})

    assert decoded_token['sub'] == test_user.username
    assert decoded_token['id'] == test_user.id

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
        tt_user = {'id':1, "username":"testtt", "role":"user"}
        token = jwt.encode(tt_user, SECRET_KEY, ALGORITHM)
        user = await get_current_user()
        
        assert user.id == tt_user['id'] 
        assert user.username == tt_user['username']