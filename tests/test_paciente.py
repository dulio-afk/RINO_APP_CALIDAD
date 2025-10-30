import pytest
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.modelos.paciente import Paciente
from flask import Flask
from datetime import datetime

@pytest.fixture
def app():
    # Crear app de Flask para pruebas
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Crear tablas en memoria
        yield app
        db.drop_all()    # Limpiar después de las pruebas

@pytest.fixture
def client(app):
    return app.test_client()

def test_agregar_paciente(app):
    with app.app_context():
        # Crear un paciente de prueba
        paciente = Paciente(
            nombre="Juan",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            edad=50,
            sexo="Masculino",
            dni="12345678",
            fecha_registro=datetime.utcnow()
        )

        db.session.add(paciente)
        db.session.commit()

        # Recuperar paciente
        paciente_db = Paciente.query.filter_by(nombre="Juan").first()
        assert paciente_db is not None
        assert paciente_db.apellido_paterno == "Pérez"
        assert paciente_db.edad == 50
