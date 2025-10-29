import pytest
from Aplicacion_Web.app import create_app
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.paciente import Paciente
from Aplicacion_Web.modelos.usuario import Usuario
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Si usas CSRF en forms

    with app.app_context():
        db.create_all()

        # Crear usuario de prueba
        if not Usuario.query.filter_by(correo='test@demo.com').first():
            user = Usuario(
                nombre='Test',
                correo='test@demo.com',
                contrasena_hash=generate_password_hash('123456', method='pbkdf2:sha256')
            )
            db.session.add(user)
            db.session.commit()

        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in_client(client, app):
    """Simula que el usuario está logueado"""
    with client.session_transaction() as session:
        # Ajusta 'user_id' según tu app
        user = Usuario.query.filter_by(correo='test@demo.com').first()
        session['user_id'] = user.id
    return client

def test_post_valido(logged_in_client, app):
    response = logged_in_client.post('/registro_paciente', data={
        'nombre': 'Ana',
        'apellido_paterno': 'Lopez',
        'apellido_materno': 'Perez',
        'edad': '40',
        'sexo': 'Femenino',
        'dni': '87654321'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Paciente registrado correctamente' in response.data.decode('utf-8')

    with app.app_context():
        paciente = Paciente.query.filter_by(nombre='Ana').first()
        assert paciente is not None
        assert paciente.edad == 40

def test_campos_obligatorios_faltantes(logged_in_client):
    response = logged_in_client.post('/registro_paciente', data={
        'nombre': '',
        'apellido_paterno': '',
        'apellido_materno': '',
        'edad': '',
        'sexo': '',
    }, follow_redirects=True)

    assert 'Todos los campos obligatorios deben estar completos.' in response.data.decode('utf-8')

def test_edad_invalida(logged_in_client):
    response = logged_in_client.post('/registro_paciente', data={
        'nombre': 'Luis',
        'apellido_paterno': 'Gomez',
        'apellido_materno': 'Perez',
        'edad': 'abc',
        'sexo': 'Masculino',
    }, follow_redirects=True)

    assert 'Edad no válida' in response.data.decode('utf-8')

def test_metodo_no_permitido(logged_in_client):
    response = logged_in_client.get('/registro_paciente', follow_redirects=True)
    assert response.status_code == 405  # Flask maneja automáticamente
