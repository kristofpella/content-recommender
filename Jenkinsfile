pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    echo 'Cloning repository...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/kristofpella/content-recommender']])
                }
            }
        }

        stage('Making a virtual environment') {
            steps {
                script {
                    echo 'Making a virtual environment...'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage('DVC Pull') {
            steps {
                withCredentials([file(credentialsId: 'grand-principle-480715-v1-bbe44ac95b61.json', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                    . ${VENV_DIR}/bin/activate
                    dvc pull
                    '''
                }
            }
        }
    }
}