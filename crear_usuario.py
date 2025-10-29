from flask import Flask
from configuracion import Configuracion
from modelos.base import db
from modelos.usuario import Usuario
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Configuracion)
db.init_app(app)

with app.app_context():
    # Crear tablas si no existen
    db.create_all()
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe# Verificar si el usuario ya existe
    # Verificar si el usuario ya existe

    # Verificar si el usuario ya existe


    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(correo='admin@demo.com').first() is None:
        contrasena_plana = '123456'

        # Utilizar pbkdf2:sha256 en lugar de scrypt
        hash_compatible = generate_password_hash(contrasena_plana, method='pbkdf2:sha256')

        nuevo_usuario = Usuario(
            nombre='Admin',
            correo='admin@demo.com',
            contrasena_hash=hash_compatible  # Guardamos directamente el hash
        )

        db.session.add(nuevo_usuario)
        db.session.commit()
        print("✅ Usuario creado exitosamente con hash compatible")
    else:
        print("⚠️ El usuario ya existe")
