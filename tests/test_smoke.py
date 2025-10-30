import pytest
from Aplicacion_Web.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_smoke(client):
    """Smoke test: verifica que la página principal responde"""
    response = client.get('/')
    assert response.status_code == 200
