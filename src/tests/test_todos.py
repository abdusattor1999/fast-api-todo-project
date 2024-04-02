from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_todos(test_todo):
    response = client.get("/to-do")
    assert response.status_code == 200
    assert response.json() == [{"complete":False, "title":"Test todo title", "description":"test description", "id":1, "priority":3, "owner_id":1, }]

def test_read_one_todo(test_todo):
    response = client.get("/to-do/1")
    assert response.status_code == 200
    assert response.json() == {"complete":False, "title":"Test todo title", "description":"test description", "id":1, "priority":3, "owner_id":1}

def test_read_one_not_found(test_todo):
    response = client.get('/to-do/999')
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found!"}

def test_create_todo(test_todo):
    json_data = {
        "title":"New todo",
        "description":"New todo description",
        "priority":5,
        "complete":False
    }

    response = client.post('/to-do/', json=json_data)
    assert response.status_code == 201
    assert response.json() == {"success":True}

    db = TestSessionLocal()
    model = db.query(Todo).filter(Todo.id==2).first()
    assert model.title == json_data['title']
    assert model.description == json_data['description']
    assert model.priority == json_data['priority']
    assert model.complete == json_data['complete']

def test_update_todo(test_todo):
    json_data = {
        'title':'Changed title',
        'description':"Done !",
        "priority":1,
        "complete":True    
    }

    response = client.put("/to-do/1", json=json_data)
    assert response.status_code == 200
    assert response.json() == {"success":True, "message":"Ish bitdi brat !"}

    db = TestSessionLocal()
    model = db.query(Todo).filter(Todo.id==1).first()
    assert model.title == json_data['title']
    assert model.description == json_data['description']
    assert model.priority == json_data['priority']
    assert model.complete == json_data['complete']

def test_update_todo_not_found(test_todo):
    json_data = {
        'title':'Changed title',
        'description':"Done !!",
        "priority":1,
        "complete":True    
    }

    response = client.put("/to-do/12222", json=json_data)
    assert response.json() == {"detail": "Todo not found!"}
    assert response.status_code == 404

def test_delete_todo(test_todo):
    response = client.delete("/to-do/1")
    assert response.status_code == 204
    db = TestSessionLocal()
    model = db.query(Todo).filter(Todo.id==1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete("/to-do/11111")
    assert response.status_code == 404
    assert response.json() == {'detail':"Todo not found!"}


