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

        stage('Checkout Source Code') {
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

            bat '''
            call venv\\Scripts\\activate

            if "%TEST_SUITE%"=="" (
                set TEST_SUITE=api
            )

            echo ===========================================
            echo Enterprise ETL Framework
            echo Selected Test Suite : %TEST_SUITE%
            echo ===========================================

            python scripts\\run_tests.py --suite %TEST_SUITE%
            '''
        }
    }
}