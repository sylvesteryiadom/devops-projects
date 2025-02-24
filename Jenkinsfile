pipeline {
    agent any

    stages {
        stage('Connect to EC2 instance') {
            steps {
                echo "🚀 Deploying application to EC2..."

                sshagent(['ec-user-ssh']) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ubuntu@54.87.26.116 docker pull welcome-to-docker:latest
                    """
                }

                echo "✅ Deployment to EC2 Completed!"
            }
        }
    }
}
