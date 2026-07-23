pipeline {

    agent any


    environment {

        PYTHON_EXE = "C:\\Users\\Admin\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"

        BUILD_TIME = "${new Date().format('yyyy-MM-dd HH:mm:ss')}"

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
                ================================
                Enterprise Ecommerce Framework
                ================================

                Build Number : ${BUILD_NUMBER}
                Branch       : ${GIT_BRANCH}
                Commit       : ${GIT_COMMIT}
                Build Time   : ${BUILD_TIME}

                ================================
                """


            }

        }





        stage('Install Dependencies') {


            steps {


                echo "Installing Python dependencies..."


                bat """

                echo Python Version

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

                if exist allure-results rmdir /s /q allure-results


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

                if exist allure-results (

                    dir allure-results

                )

                else (

                    echo No allure results found

                )


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





        stage('Validate Dashboard') {


            steps {


                echo "Checking dashboard files..."


                bat """


                dir reports


                """


            }


        }





    }



    post {



        always {


            echo "Publishing All Reports..."



            allure(


                includeProperties: false,

                jdk: '',

                results: [[path: 'allure-results']]


            )





            publishHTML(


                target: [


                    allowMissing: true,


                    alwaysLinkToLastBuild: true,


                    keepAll: true,


                    reportDir: 'reports',


                    reportFiles: 'enterprise_dashboard.html',


                    reportName: 'Enterprise Dashboard'


                ]


            )






            archiveArtifacts(


                artifacts: '''


                reports/**


                allure-results/**


                allure-report/**


                ''' ,


                fingerprint: true


            )





            junit(


                allowEmptyResults: true,


                testResults: 'reports/junit.xml'


            )



            echo "Reports Published Successfully"


        }





        success {


            echo """

            ==================================

            BUILD SUCCESS

            Enterprise Ecommerce Framework

            ==================================

            """

        }





        failure {


            echo """

            ==================================

            BUILD FAILED

            Check Console Logs

            ==================================

            """

        }


    }


}