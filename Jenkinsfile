pipeline {
    agent any

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: [
                'api',
                'all',
                'database',
                'data_quality',
                'regression'
            ],
            description: 'Select the test suite to execute'
        )
    }

    environment {
        PYTHON_EXE = 'C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Version') {
            steps {
                bat '''
                    "%PYTHON_EXE%" --version
                    "%PYTHON_EXE%" -m pip --version
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                    if not exist venv (
                        "%PYTHON_EXE%" -m venv venv
                    )
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Create Report Directories') {
            steps {
                bat '''
                    if not exist reports mkdir reports
                    if not exist reports\\html mkdir reports\\html
                    if not exist reports\\allure-results mkdir reports\\allure-results
                '''
            }
        }

        stage('Run Tests') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'oracle-host',
                        variable: 'ORACLE_HOST'
                    ),
                    string(
                        credentialsId: 'oracle-port',
                        variable: 'ORACLE_PORT'
                    ),
                    string(
                        credentialsId: 'oracle-service',
                        variable: 'ORACLE_SERVICE'
                    ),
                    usernamePassword(
                        credentialsId: 'oracle-credentials',
                        usernameVariable: 'ORACLE_USER',
                        passwordVariable: 'ORACLE_PASSWORD'
                    ),
                    string(
                        credentialsId: 'mysql-host',
                        variable: 'MYSQL_HOST'
                    ),
                    string(
                        credentialsId: 'mysql-port',
                        variable: 'MYSQL_PORT'
                    ),
                    string(
                        credentialsId: 'mysql-database',
                        variable: 'MYSQL_DATABASE'
                    ),
                    usernamePassword(
                        credentialsId: 'mysql-credentials',
                        usernameVariable: 'MYSQL_USER',
                        passwordVariable: 'MYSQL_PASSWORD'
                    )
                ]) {
                    bat '''
                        call venv\\Scripts\\activate
                        python scripts\\run_tests.py --suite %TEST_SUITE%
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )

            junit(
                testResults: 'reports/junit/*.xml',
                allowEmptyResults: true
            )
        }

        success {
            echo 'Enterprise Ecommerce Framework pipeline completed successfully.'
        }

        failure {
            echo 'Enterprise Ecommerce Framework pipeline failed. Check the console logs and reports.'
        }

        cleanup {
            bat '''
                if exist reports\\allure-results (
                    echo Allure results are available.
                )
            '''
        }
    }
}