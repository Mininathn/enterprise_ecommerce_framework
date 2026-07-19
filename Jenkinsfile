pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(
            logRotator(
                numToKeepStr: '10',
                artifactNumToKeepStr: '5'
            )
        )
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: [
                'api',
                'smoke',
                'database',
                'data_quality',
                'regression',
                'all'
            ],
            description: 'Select the test suite to execute'
        )
    }

    environment {
        PYTHON_EXE = 'C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
        VENV_PYTHON = 'venv\\Scripts\\python.exe'
        VENV_PIP = 'venv\\Scripts\\pip.exe'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }

        stage('Python Version') {
            steps {
                bat '''
                echo ===========================================
                echo Python Environment
                echo ===========================================

                "%PYTHON_EXE%" --version
                "%PYTHON_EXE%" -m pip --version
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                echo ===========================================
                echo Creating Virtual Environment
                echo ===========================================

                if not exist venv (
                    "%PYTHON_EXE%" -m venv venv
                ) else (
                    echo Virtual environment already exists.
                )
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                echo ===========================================
                echo Installing Dependencies
                echo ===========================================

                call venv\\Scripts\\activate

                python -m pip install --upgrade pip
                python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Create Report Directories') {
            steps {
                bat '''
                echo ===========================================
                echo Creating Report Directories
                echo ===========================================

                if not exist reports mkdir reports
                if not exist reports\\html mkdir reports\\html
                if not exist reports\\allure-results mkdir reports\\allure-results
                if not exist reports\\junit mkdir reports\\junit
                '''
            }
        }

        stage('Run Test Suite') {
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
                        credentialsId: 'oracle-sid',
                        variable: 'ORACLE_SID'
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
                    script {
                        def selectedSuite = params.TEST_SUITE?.trim()

                        if (!selectedSuite) {
                            selectedSuite = 'api'
                        }

                        echo "Selected test suite: ${selectedSuite}"

                        withEnv([
                            "SELECTED_TEST_SUITE=${selectedSuite}"
                        ]) {
                            bat '''
                            echo ===========================================
                            echo Enterprise Ecommerce ETL Framework
                            echo Selected Test Suite: %SELECTED_TEST_SUITE%
                            echo ===========================================

                            call venv\\Scripts\\activate

                            python scripts\\run_tests.py --suite %SELECTED_TEST_SUITE%
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing Jenkins test reports...'

            archiveArtifacts(
                artifacts: 'reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )

            junit(
                testResults: 'reports/junit/test-results.xml',
                allowEmptyResults: true,
                keepLongStdio: true
            )

            echo 'Reports archived successfully.'
        }

        success {
            echo '''
            =======================================
            Enterprise ETL Pipeline SUCCESS
            All selected tests passed.
            =======================================
            '''
        }

        unstable {
            echo '''
            =======================================
            Enterprise ETL Pipeline UNSTABLE
            Review the published test results.
            =======================================
            '''
        }

        failure {
            echo '''
            =======================================
            Enterprise ETL Pipeline FAILED
            Check the Jenkins Console Output.
            =======================================
            '''
        }

        cleanup {
            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: false
            )
        }
    }
}