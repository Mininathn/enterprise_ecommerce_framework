pipeline {

    agent any

    environment {
        PYTHON_EXE = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                checkout scm
            }
        }

        stage('Create .env') {
            steps {
                bat '''
                (
                echo ORACLE_HOST=localhost
                echo ORACLE_PORT=1521
                echo ORACLE_SID=XE
                echo ORACLE_USER=C##SOURCE
                echo ORACLE_PASSWORD=Shri911

                echo.

                echo MYSQL_HOST=localhost
                echo MYSQL_PORT=3306
                echo MYSQL_DATABASE=ecommerce_target_db
                echo MYSQL_USER=root
                echo MYSQL_PASSWORD=admin
                ) > .env

                echo ==========================
                echo Generated .env
                echo ==========================
                type .env
                '''
            }
        }

        stage('Verify Python') {
            steps {
                bat '''
                %PYTHON_EXE% --version
                '''
            }
        }

    }

}