pipeline {

    agent any

    environment {
        PYTHON_EXE = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: [
                'all',
                'smoke',
                'regression',
                'ddt',
                'api'
            ],
            description: 'Select Test Suite'
        )
    }

    triggers {
        cron('H 9 * * *')
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Build Information') {
            steps {
                echo """
                =========================================
                Enterprise Ecommerce ETL Framework
                Sprint 10 Enterprise Dashboard
                =========================================

                Build Number : ${BUILD_NUMBER}
                Branch       : ${GIT_BRANCH}
                Commit       : ${GIT_COMMIT}
                Job Name     : ${JOB_NAME}

                =========================================
                """
            }
        }

        stage('Prepare Workspace') {
            steps {
                echo "Cleaning workspace..."
                bat """
                if exist allure-results rmdir /s /q allure-results
                if exist allure-report rmdir /s /q allure-report

                if not exist reports mkdir reports
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."

                bat """
                %PYTHON_EXE% --version

                %PYTHON_EXE% -m pip install --upgrade pip

                %PYTHON_EXE% -m pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "Executing Test Suite : ${params.TEST_SUITE}"

                    withCredentials([
                        string(credentialsId: 'oracle-host',     variable: 'ORACLE_HOST'),
                        string(credentialsId: 'oracle-port',     variable: 'ORACLE_PORT'),
                        string(credentialsId: 'oracle-sid',      variable: 'ORACLE_SID'),
                        string(credentialsId: 'oracle-user',     variable: 'ORACLE_USER'),
                        string(credentialsId: 'oracle-password', variable: 'ORACLE_PASSWORD'),
                        string(credentialsId: 'mysql-host',      variable: 'MYSQL_HOST'),
                        string(credentialsId: 'mysql-port',      variable: 'MYSQL_PORT'),
                        string(credentialsId: 'mysql-database',  variable: 'MYSQL_DATABASE'),
                        string(credentialsId: 'mysql-user',      variable: 'MYSQL_USER'),
                        string(credentialsId: 'mysql-password',  variable: 'MYSQL_PASSWORD')
                    ]) {

                        if (params.TEST_SUITE == 'all') {

                            bat """
                            echo ================================
                            echo Running ALL Tests
                            echo ================================

                            %PYTHON_EXE% -m pytest tests ^
                            --alluredir=allure-results ^
                            --html=reports\\pytest-report.html ^
                            --self-contained-html ^
                            --junitxml=reports\\junit.xml
                            """

                        } else {

                            bat """
                            echo ================================
                            echo Running ${params.TEST_SUITE} Tests
                            echo ================================

                            %PYTHON_EXE% -m pytest tests ^
                            -m ${params.TEST_SUITE} ^
                            --alluredir=allure-results ^
                            --html=reports\\pytest-report.html ^
                            --self-contained-html ^
                            --junitxml=reports\\junit.xml
                            """

                        }
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo "Generating Allure HTML Report..."
                bat """
                allure generate allure-results ^
                -o allure-report ^
                --clean
                """
            }
        }

        stage('Generate Enterprise Dashboard') {
            steps {
                echo "Generating Enterprise Dashboard..."
                bat """
                %PYTHON_EXE% scripts\\generate_dashboard.py

                %PYTHON_EXE% scripts\\generate_html_dashboard.py
                """
            }
        }

        stage('Validate Reports') {
            steps {
                echo "Checking generated reports..."
                bat """
                echo ==========================
                echo Reports Folder
                echo ==========================

                dir reports

                echo ==========================
                echo Allure Results
                echo ==========================

                dir allure-results

                echo ==========================
                echo Dashboard
                echo ==========================

                dir reports\\enterprise_dashboard.html
                """
            }
        }

    }

    post {

        always {
            echo "Publishing Enterprise Reports..."

            allure(
                includeProperties: false,
                jdk: '',
                results: [
                    [path: 'allure-results']
                ]
            )

            publishHTML(
                target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'enterprise_dashboard.html',
                    reportName: 'Enterprise Ecommerce Dashboard'
                ]
            )

            publishHTML(
                target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'pytest-report.html',
                    reportName: 'Pytest HTML Report'
                ]
            )

            archiveArtifacts(
                artifacts: '''
                reports/**
                allure-results/**
                allure-report/**
                ''',
                fingerprint: true,
                allowEmptyArchive: true
            )

            junit(
                allowEmptyResults: true,
                testResults: 'reports/junit.xml'
            )

            echo """
            =====================================
            Enterprise Reports Published

            ✔ Allure Report
            ✔ Enterprise Dashboard
            ✔ Pytest HTML Report
            ✔ JUnit Report

            =====================================
            """
        }

        success {
            echo """
            =====================================
            BUILD SUCCESSFUL

            Sprint 10 Completed

            =====================================
            """
        }

        failure {
            echo """
            =====================================
            BUILD FAILED

            Check Jenkins Console Logs

            =====================================
            """
        }

    }

}