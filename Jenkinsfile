post {

    always {

        echo "Publishing Reports..."

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

        allure([
            includeProperties: false,
            jdk: '',
            properties: [],
            reportBuildPolicy: 'ALWAYS',
            results: [
                [
                    path: 'reports/allure-results'
                ]
            ]
        ])

        echo "Reports Published Successfully."
    }

    success {

        emailext(
            mimeType: 'text/html',
            to: 'nmininath1@gmail.com',
            subject: "SUCCESS - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
<html>
<head>
<style>
table {
    border-collapse: collapse;
}
td, th {
    border:1px solid #cccccc;
    padding:8px;
}
</style>
</head>

<body>

<h2 style="color:green;">
Enterprise Ecommerce ETL Framework
</h2>

<h3>
Build Completed Successfully
</h3>

<table>

<tr>
<th>Job Name</th>
<td>${env.JOB_NAME}</td>
</tr>

<tr>
<th>Build Number</th>
<td>#${env.BUILD_NUMBER}</td>
</tr>

<tr>
<th>Test Suite</th>
<td>${params.TEST_SUITE}</td>
</tr>

<tr>
<th>Status</th>
<td style="color:green;"><b>SUCCESS</b></td>
</tr>

<tr>
<th>Build URL</th>
<td>
<a href="${env.BUILD_URL}">
${env.BUILD_URL}
</a>
</td>
</tr>

</table>

<br>

<b>Pipeline Summary</b>

<ul>
<li>Source Code Checked Out</li>
<li>Python Environment Created</li>
<li>Dependencies Installed</li>
<li>Docker Image Built</li>
<li>Docker Container Executed</li>
<li>JUnit Report Generated</li>
<li>Allure Report Generated</li>
<li>Artifacts Archived</li>
</ul>

</body>
</html>
""",
            attachmentsPattern: 'reports/**/*'
        )

        echo '''
=========================================================
Enterprise Ecommerce ETL Framework

BUILD SUCCESS

Docker Image Built Successfully

Docker Container Executed Successfully

JUnit Report Published

Allure Report Published

Artifacts Archived Successfully
=========================================================
'''
    }

    unstable {

        emailext(
            mimeType: 'text/html',
            to: 'nmininath1@gmail.com',
            subject: "UNSTABLE - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
<html>

<h2 style="color:orange;">
Enterprise Ecommerce ETL Framework
</h2>

<h3>
Build is UNSTABLE
</h3>

<table border="1" cellpadding="8">

<tr>
<td><b>Job</b></td>
<td>${env.JOB_NAME}</td>
</tr>

<tr>
<td><b>Build</b></td>
<td>#${env.BUILD_NUMBER}</td>
</tr>

<tr>
<td><b>Suite</b></td>
<td>${params.TEST_SUITE}</td>
</tr>

<tr>
<td><b>Status</b></td>
<td style="color:orange;"><b>UNSTABLE</b></td>
</tr>

<tr>
<td><b>Build URL</b></td>
<td>
<a href="${env.BUILD_URL}">
${env.BUILD_URL}
</a>
</td>
</tr>

</table>

<p>
Some tests failed. Please review the Allure Report and Jenkins Console Output.
</p>

</html>
""",
            attachmentsPattern: 'reports/**/*'
        )

        echo '''
=========================================================
BUILD UNSTABLE

Some tests failed.

Please review the Allure Report.
=========================================================
'''
    }

    failure {

        emailext(
            mimeType: 'text/html',
            to: 'nmininath1@gmail.com',
            subject: "FAILED - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: """
<html>

<h2 style="color:red;">
Enterprise Ecommerce ETL Framework
</h2>

<h3>
Build FAILED
</h3>

<table border="1" cellpadding="8">

<tr>
<td><b>Job</b></td>
<td>${env.JOB_NAME}</td>
</tr>

<tr>
<td><b>Build</b></td>
<td>#${env.BUILD_NUMBER}</td>
</tr>

<tr>
<td><b>Suite</b></td>
<td>${params.TEST_SUITE}</td>
</tr>

<tr>
<td><b>Status</b></td>
<td style="color:red;"><b>FAILED</b></td>
</tr>

<tr>
<td><b>Build URL</b></td>
<td>
<a href="${env.BUILD_URL}">
${env.BUILD_URL}
</a>
</td>
</tr>

</table>

<p>
Please review:
</p>

<ul>
<li>Jenkins Console Output</li>
<li>Docker Logs</li>
<li>JUnit Report</li>
<li>Allure Report</li>
</ul>

</html>
""",
            attachmentsPattern: 'reports/**/*'
        )

        echo '''
=========================================================
BUILD FAILED

Please review:

• Jenkins Console Output
• Docker Logs
• Allure Report

=========================================================
'''
    }

    cleanup {

        cleanWs(
            deleteDirs: true,
            disableDeferredWipeout: false
        )
    }
}