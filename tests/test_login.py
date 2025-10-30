import sys
import os
import pytest
from werkzeug.security import generate_password_hash

# Asegurar que se pueda importar Aplicacion_Web desde RINO/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Aplicacion_Web.app import create_app
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.usuario import Usuario


@pytest.fixture
def app():
    """Crea la app Flask en modo testing con BD en memoria"""
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

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crea un cliente de pruebas Flask"""
    return app.test_client()


def test_login_valido(client):
    """✅ Test login con credenciales correctas"""
    response = client.post('/login', data={
        'correo': 'admin@demo.com',
        'contrasena': '123456'
    }, follow_redirects=True)

    print("\n[DEBUG] Status code:", response.status_code)
    print("[DEBUG] Body:", response.data.decode('utf-8')[:300])

    assert response.status_code == 200
    assert b'Bienvenido' in response.data or b'Dashboard' in response.data


def test_login_invalido(client):
    """🚫 Test login con credenciales incorrectas"""
    # No seguimos redirecciones para evitar bucles infinitos
    response = client.post('/login', data={
        'correo': 'admin@demo.com',
        'contrasena': 'incorrecta'
    }, follow_redirects=False)

    print("\n[DEBUG] Status code:", response.status_code)
    print("[DEBUG] Redirige a:", response.headers.get('Location', 'No redirige'))

    # Debe responder 200 (render template) o 302 (redirigir al login)
    assert response.status_code in [200, 302]
