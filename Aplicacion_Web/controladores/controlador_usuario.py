from Aplicacion_Web.modelos.usuario import Usuario
from Aplicacion_Web.modelos.base import db

def autenticar_usuario(correo, contrasena):
    usuario = Usuario.query.filter_by(correo=correo).first()
    if usuario and usuario.check_password(contrasena):
        return usuario
    return None

def registrar_usuario(nombre, correo, contrasena):
    nuevo_usuario = Usuario(nombre=nombre, correo=correo)
    nuevo_usuario.set_password(contrasena)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return nuevo_usuario
