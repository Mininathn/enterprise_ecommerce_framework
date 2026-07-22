pipeline {

    agent any


    parameters {

        choice(
            name: 'TEST_SUITE',
            choices: [
                'all',
                'smoke',
                'regression',
                'ddt'
            ],
            description: 'Select Test Suite'
        )

    }


    environment {

        IMAGE_NAME = "enterprise-ecommerce-framework"

    }


    stages {


        stage('Checkout Source Code') {

            steps {

                echo "Checking out source code..."

                git(
                    branch: 'main',
                    url: 'https://github.com/Mininathn/enterprise_ecommerce_framework.git'
                )

            }

        }



        stage('Install Dependencies') {

            steps {

                echo "Installing Python dependencies..."

                bat """

                python -m pip install --upgrade pip

                pip install -r requirements.txt

                """

            }

        }



        stage('Build Docker Image') {

            steps {

                echo "Building Docker Image..."

                bat """

                docker build -t %IMAGE_NAME% .

                """

            }

        }



        stage('Run Docker Container') {

            steps {

                echo "Running Tests Inside Docker Container..."

                bat """

                docker run --rm ^
                -e TEST_SUITE=${params.TEST_SUITE} ^
                -v "%WORKSPACE%\\reports:/app/reports" ^
                %IMAGE_NAME%

                """

            }

        }



        stage('Test Result Summary') {

            steps {

                echo """

                =========================================

                Enterprise Ecommerce ETL Framework

                Test Suite : ${params.TEST_SUITE}

                Docker Execution Completed

                Reports Generated

                =========================================

                """

            }

        }


    }



    post {


        always {


            echo "Publishing Test Reports..."



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



            allure(

                includeProperties: false,

                jdk: '',

                properties: [],

                reportBuildPolicy: 'ALWAYS',

                results: [

                    [

                        path: 'reports/allure-results'

                    ]

                ]

            )



            echo "Reports Published Successfully."


        }




        success {


            echo """

            =========================================

            BUILD SUCCESS

            Enterprise Ecommerce ETL Framework

            Docker Image Built Successfully

            Docker Container Executed Successfully

            JUnit Report Published

            Allure Report Published

            =========================================

            """



            emailext(

                mimeType: 'text/html',

                to: 'nmininath1@gmail.com',

                subject: "SUCCESS - ${env.JOB_NAME} #${env.BUILD_NUMBER}",

                body: """

<html>

<body>

<h2 style="color:green">

Enterprise Ecommerce ETL Framework

</h2>


<h3>

Build Completed Successfully

</h3>


<table border="1" cellpadding="8">


<tr>

<td><b>Job Name</b></td>

<td>${env.JOB_NAME}</td>

</tr>


<tr>

<td><b>Build Number</b></td>

<td>${env.BUILD_NUMBER}</td>

</tr>


<tr>

<td><b>Test Suite</b></td>

<td>${params.TEST_SUITE}</td>

</tr>


<tr>

<td><b>Status</b></td>

<td>

SUCCESS

</td>

</tr>


<tr>

<td><b>Build URL</b></td>

<td>

${env.BUILD_URL}

</td>

</tr>


</table>


<br>


<b>Completed Activities:</b>


<ul>

<li>Source Code Checkout</li>

<li>Dependencies Installation</li>

<li>Docker Image Build</li>

<li>Docker Container Execution</li>

<li>JUnit Report Generation</li>

<li>Allure Report Generation</li>

<li>Artifact Archiving</li>

</ul>


</body>

</html>

"""

            )


        }




        unstable {


            echo "BUILD UNSTABLE"



            emailext(

                mimeType: 'text/html',

                to: 'nmininath1@gmail.com',

                subject: "UNSTABLE - ${env.JOB_NAME} #${env.BUILD_NUMBER}",

                body: """

Enterprise Ecommerce ETL Framework

Build is UNSTABLE.

Some tests failed.

Please check Jenkins reports.

Build URL:

${env.BUILD_URL}

"""

            )


        }




        failure {


            echo """

            =========================================

            BUILD FAILED

            Check:

            - Jenkins Console Logs

            - Docker Logs

            - JUnit Report

            - Allure Report

            =========================================

            """



            emailext(

                mimeType: 'text/html',

                to: 'nmininath1@gmail.com',

                subject: "FAILED - ${env.JOB_NAME} #${env.BUILD_NUMBER}",

                body: """

<html>

<body>


<h2 style="color:red">

Enterprise Ecommerce ETL Framework

</h2>


<h3>

Build FAILED

</h3>


<p>

Please check:

</p>


<ul>

<li>Jenkins Console Output</li>

<li>Docker Execution Logs</li>

<li>JUnit Report</li>

<li>Allure Report</li>

</ul>


<p>

Build URL:

${env.BUILD_URL}

</p>


</body>

</html>

"""

            )


        }




        cleanup {


            echo "Cleaning Workspace..."

            cleanWs(

                deleteDirs: true,

                disableDeferredWipeout: false

            )


        }


    }


}