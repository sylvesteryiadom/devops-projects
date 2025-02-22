pipeline {
    agent any
    
    tools{
        maven 'maven-3.9'
    }

    environment {
        IMAGE_NAME = 'sylvesteryiadom/java-maven-repo'
        IMAGE_TAG = '01'
        DOCKER_CREDENTIALS = credentials('docker-creds') // Jenkins Docker Hub Credentials ID
    }

    stages {
        stage('Build with Maven') {
            steps {
                echo "🔨 Running Maven Package..."
                sh 'mvn clean package'
                echo "✅ Maven Build Completed!"
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker Image..."
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                echo "✅ Docker Image Built Successfully!"
            }
        }

        stage('Login to Docker Hub') {
            steps {
                echo "🔑 Logging into Docker Hub..."
                sh "echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin"
                echo "✅ Docker Login Successful!"
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "📦 Pushing Docker Image to Docker Hub..."
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                echo "✅ Docker Image Pushed Successfully!"
            }
        }
    }
}
