import os

class Configuracion:
    BASE_DIR = os.path.dirname(__file__)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    RETINAS_FOLDER = os.path.join(UPLOAD_FOLDER, 'retinas')
    DOCUMENTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'documentos')
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    IA_MICROSERVICE_URL = 'http://localhost:8000/predict/'

    # Configuración para conexión con MySQL (XAMPP)
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_HOST = 'localhost'
    MYSQL_DB = 'retinopatia_db'
    MYSQL_PORT = 3306

    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def extension_valida(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Configuracion.ALLOWED_EXTENSIONS
