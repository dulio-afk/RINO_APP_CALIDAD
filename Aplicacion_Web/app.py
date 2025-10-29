from flask import Flask
from Aplicacion_Web.configuracion import Configuracion
from Aplicacion_Web.modelos.base import db
from Aplicacion_Web.routes.auth_routes import auth_bp
from Aplicacion_Web.routes.main_routes import main_bp
from Aplicacion_Web.routes.paciente_routes import paciente_bp
from Aplicacion_Web.routes.examen_clinico_routes import examen_clinico_bp
from Aplicacion_Web.routes.imagen_routes import imagen_bp
from Aplicacion_Web.routes.documento_routes import documento_bp
from Aplicacion_Web.routes.sandbox_routes import sandbox_bp
from Aplicacion_Web.controladores.historial_controlador import historial_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Configuracion)

    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(examen_clinico_bp)
    app.register_blueprint(imagen_bp)
    app.register_blueprint(documento_bp)
    app.register_blueprint(sandbox_bp)
    app.register_blueprint(historial_bp)

    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Sistema de Retinopatía Diabética</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
                    color: white;
                    text-align: center;
                    padding-top: 80px;
                    font-family: 'Segoe UI', sans-serif;
                }
                .btn-custom {
                    background-color: #17a2b8;
                    border: none;
                    padding: 12px 30px;
                    font-size: 18px;
                    border-radius: 8px;
                    transition: background-color 0.3s;
                }
                .btn-custom:hover {
                    background-color: #138496;
                }
                .logo {
                    width: 100px;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://cdn-icons-png.flaticon.com/512/942/942748.png" class="logo" alt="Logo del sistema">
                <h1 class="display-4 mb-4">👁️ Bienvenido al Sistema de Detección de Retinopatía Diabética</h1>
                <p class="lead mb-5">Una herramienta inteligente para apoyar el diagnóstico clínico y el seguimiento de pacientes.</p>
                <a href="/login" class="btn btn-custom">Iniciar Sesión</a>
            </div>
        </body>
        </html>
        '''

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
