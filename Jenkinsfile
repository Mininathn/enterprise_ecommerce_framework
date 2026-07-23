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


                echo "Preparing workspace..."


                bat """

                if exist allure-results rmdir /s /q allure-results

                if exist allure-report rmdir /s /q allure-report


                if not exist reports mkdir reports


                """

            }

        }








        stage('Install Dependencies') {


            steps {


                echo "Installing dependencies..."


                bat """

                %PYTHON_EXE% --version


                %PYTHON_EXE% -m pip install --upgrade pip


                %PYTHON_EXE% -m pip install -r requirements.txt


                """

            }

        }









        stage('Run Tests') {


            steps {


                echo "Running Test Suite : ${params.TEST_SUITE}"


                bat """

                echo Starting Pytest Execution


                %PYTHON_EXE% -m pytest tests ^

                -m ${params.TEST_SUITE} ^

                --alluredir=allure-results ^

                --html=reports\\pytest-report.html ^

                --self-contained-html


                """

            }

        }









        stage('Generate JUnit Report') {


            steps {


                echo "Generating JUnit XML report..."


                bat """


                %PYTHON_EXE% -m pytest tests ^

                -m ${params.TEST_SUITE} ^

                --junitxml=reports\\junit.xml


                """


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


                echo "Generating Sprint 10 Dashboard..."


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


                echo ===== REPORTS =====

                dir reports


                echo ===== ALLURE =====

                dir allure-results


                echo ===== DASHBOARD =====

                dir reports\\enterprise_dashboard.html


                """

            }

        }





    }





    post {


    always {


        echo "Publishing Enterprise Reports..."



        // Allure Report Publishing

        allure(

            includeProperties: false,

            jdk: '',

            results: [

                [path: 'allure-results']

            ]

        )





        // Enterprise Dashboard Publishing

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





        // Pytest HTML Report Publishing

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





        // Archive Build Artifacts

        archiveArtifacts(

            artifacts: '''

            reports/**

            allure-results/**

            allure-report/**

            ''',

            fingerprint: true,

            allowEmptyArchive: true

        )





        // Publish JUnit Results

        junit(

            allowEmptyResults: true,

            testResults: 'reports/junit.xml'

        )





        echo """

        =====================================


        Enterprise Reports Published Successfully


        ✔ Allure Report

        ✔ Enterprise Dashboard

        ✔ Pytest HTML Report

        ✔ JUnit Report

        ✔ Build Artifacts


        =====================================

        """

    }






    success {


        echo """

        =====================================


        BUILD SUCCESSFUL


        Sprint 10 Completed


        Enterprise Dashboard Available


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