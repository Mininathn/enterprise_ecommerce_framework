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