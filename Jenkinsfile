pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'grand-principle-480715-v1'
        GCLOUD_PATH = '/var/jenkins_home/google-cloud-sdk/bin'
        KUBECTL_AUTH__PLUGIN = 'usr/lib/google-cloud-sdk/bin'
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

        stage('Build and push image to GCR') {
             steps {
                withCredentials([file(credentialsId: 'content-recommender-system-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    echo 'Building and pushing image to GCR using Cloud Build...'
                    sh '''
                    export PATH=$PATH:${GCLOUD_PATH}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    # Copy credentials file to build context for Dockerfile
                    cp ${GOOGLE_APPLICATION_CREDENTIALS} grand-principle-480715-v1-bbe44ac95b61.json
                    # Build and push using Cloud Build
                    gcloud builds submit --tag gcr.io/${GCP_PROJECT}/content-recommender-system:latest .
                    # Clean up credentials file
                    rm -f grand-principle-480715-v1-bbe44ac95b61.json
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
             steps {
                withCredentials([file(credentialsId: 'content-recommender-system-service-account', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    echo 'Deploying to Kubernetes...'
                    sh '''
                    export PATH=$PATH:${GCLOUD_PATH}
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials recommender-system-cluster --region us-central1
                    kubectl apply -f deployment.yaml
                    '''
                }
            }
        }
    }
}