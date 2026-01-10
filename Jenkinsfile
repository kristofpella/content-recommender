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
                withCredentials([file(credentialsId: 'content-recommender-system-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''
                    . ${VENV_DIR}/bin/activate
                    # Configure DVC remote if it doesn't exist or update credential path
                    if ! dvc remote list | grep -q myremote; then
                        echo "Configuring DVC remote..."
                        dvc remote add -d myremote gs://my-dvc-bucket-28/
                    fi
                    dvc remote modify myremote credentialpath ${GOOGLE_APPLICATION_CREDENTIALS}
                    dvc remote default myremote
                    echo "Pulling DVC data..."
                    dvc pull
                    '''
                }
            }
        }
    }
}