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



        stage('Install Dependencies') {

            steps {

                echo "Installing Python dependencies..."

                bat """
                echo Python Version:
                %PYTHON_EXE% --version

                echo Installing packages...

                %PYTHON_EXE% -m pip install --upgrade pip

                %PYTHON_EXE% -m pip install -r requirements.txt
                """

            }
        }



        stage('Run Tests') {

            steps {

                echo "Running Test Suite: ${params.TEST_SUITE}"


                bat """
                %PYTHON_EXE% -m pytest tests ^
                -m ${params.TEST_SUITE} ^
                --alluredir=allure-results ^
                --html=reports\\pytest-report.html ^
                --self-contained-html
                """

            }
        }



        stage('Generate Test Summary') {

            steps {

                echo "Generating test summary..."

                bat """

                dir allure-results

                """

            }
        }


    }



    post {


        always {


            echo "Publishing Allure Report..."


            allure(
                includeProperties: false,
                jdk: '',
                results: [
                    [
                        path: 'allure-results'
                    ]
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

        }



        success {

            echo "Pipeline completed successfully."

        }



        failure {

            echo "Pipeline failed. Check console logs."

        }

    }

}