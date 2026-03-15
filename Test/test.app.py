import sys
sys.path.insert(0, './app')
from app import app

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

def test_greet():
    client = app.test_client()
    response = client.get('/greet?name=Alice')
    assert response.status_code == 200
    assert b'Alice' in response.data
