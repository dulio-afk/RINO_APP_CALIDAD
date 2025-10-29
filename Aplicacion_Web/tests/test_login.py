import pytest
from Aplicacion_Web.app import create_app
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.usuario import Usuario
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        # Crear usuario de prueba
        if Usuario.query.filter_by(correo='admin@demo.com').first() is None:
            hash_compatible = generate_password_hash('123456', method='pbkdf2:sha256')
            usuario = Usuario(
                nombre='Admin',
                correo='admin@demo.com',
                contrasena_hash=hash_compatible
            )
            db.session.add(usuario)
            db.session.commit()

        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_valido(client):
    """Test login con credenciales correctas"""
    response = client.post('/login', data={
        'correo': 'admin@demo.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Bienvenido' in response.data or b'Dashboard' in response.data

def test_login_invalido(client):
    """Test login con credenciales incorrectas"""
    response = client.post('/login', data={
        'correo': 'admin@demo.com',
        'contrasena': 'incorrecta'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Usuario o contraseña incorrecta' in response.data.decode('utf-8')
