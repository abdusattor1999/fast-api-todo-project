from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_health_check():
    response = client.get("/healthy")
    assert response.json() == {"status":"Healthy"}
    assert response.status_code == 200

