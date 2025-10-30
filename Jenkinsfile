pipeline {
    agent any

    environment {
        PYTHON = 'python3'
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
                sh '''
                ${PYTHON} -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Ejecutar pruebas') {
            steps {
                echo '🧪 Ejecutando pruebas Pytest...'
                sh '''
                . venv/bin/activate
                pytest --maxfail=1 --disable-warnings -q --junitxml=tests/reports/resultados.xml
                '''
            }
        }
    }

    post {
        always {
            junit 'tests/reports/*.xml'
        }
        success {
            echo '✅ Todas las pruebas pasaron correctamente.'
        }
        failure {
            echo '❌ Al menos una prueba falló. Revisa los logs.'
        }
    }
}
