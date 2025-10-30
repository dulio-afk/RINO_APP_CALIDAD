pipeline {
    agent any

    environment {
        PYTHON = 'python'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📦 Clonando repositorio...'
                git branch: 'main', url: 'https://github.com/dulio-afk/RINO_APP_CALIDAD.git'
            }
        }

        stage('Instalar dependencias') {
            steps {
                echo '⚙️ Creando entorno virtual e instalando dependencias...'
                bat '''
                %PYTHON% -m venv %VENV_DIR%
                call %VENV_DIR%\\Scripts\\activate
                python -m pip install --upgrade pip setuptools wheel
                echo Instalando dependencias principales...
                pip install -r requirements.txt
                '''
            }
        }

        stage('Verificar instalación') {
            steps {
                echo '🔍 Verificando instalación de dependencias...'
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                python -m pip list
                '''
            }
        }

        stage('Ejecutar pruebas') {
            steps {
                echo '🧪 Ejecutando pruebas Pytest...'
                bat '''
                call %VENV_DIR%\\Scripts\\activate
                if not exist tests\\reports mkdir tests\\reports
                pytest -v --maxfail=1 --disable-warnings --junitxml=tests\\reports\\resultados.xml
                '''
            }
        }
    }

    post {
        always {
            echo '📊 Publicando resultados de pruebas...'
            junit 'tests\\reports\\*.xml'
        }
        success {
            echo '✅ Todas las pruebas pasaron correctamente.'
        }
        failure {
            echo '❌ Al menos una prueba falló. Revisa los logs.'
        }
    }
}
