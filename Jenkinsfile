pipeline {
    agent any
    
    tools{
        maven 'maven-3.9'
    }

    // environment {
    //     IMAGE_NAME = 'sylvesteryiadom/java-maven-repo'
    //     IMAGE_TAG = '01'
    //     DOCKER_CREDENTIALS = credentials('dockerhub-creddentials') // Jenkins Docker Hub Credentials ID
    // }

    stages {
        stage('Build with Maven') {
            steps {
                echo "🔨 Running Maven Package..."
                sh 'mvn clean package'
                echo "✅ Maven Build Completed!"
            }
        }
    }
}
