-- ============================================================
-- Oracle Customer Source Test Data
-- Includes valid, duplicate and invalid records
-- ============================================================

DELETE FROM SRC_CUSTOMER_ADDRESS;
DELETE FROM SRC_CUSTOMER;

INSERT INTO SRC_CUSTOMER (
    CUSTOMER_ID,
    SOURCE_SYSTEM,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    DATE_OF_BIRTH,
    GENDER,
    CUSTOMER_STATUS,
    ETL_STATUS
)
VALUES (
    1001,
    'ORACLE_ECOM',
    'Mininath',
    'Navdkar',
    'mininath.navdkar@example.com',
    '9876543210',
    DATE '1990-05-15',
    'MALE',
    'ACTIVE',
    'PENDING'
);

INSERT INTO SRC_CUSTOMER (
    CUSTOMER_ID,
    SOURCE_SYSTEM,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    DATE_OF_BIRTH,
    GENDER,
    CUSTOMER_STATUS,
    ETL_STATUS
)
VALUES (
    1002,
    'ORACLE_ECOM',
    'Priya',
    'Sharma',
    'priya.sharma@example.com',
    '9876501234',
    DATE '1992-08-20',
    'FEMALE',
    'ACTIVE',
    'PENDING'
);

INSERT INTO SRC_CUSTOMER (
    CUSTOMER_ID,
    SOURCE_SYSTEM,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    DATE_OF_BIRTH,
    GENDER,
    CUSTOMER_STATUS,
    ETL_STATUS
)
VALUES (
    1003,
    'ORACLE_ECOM',
    'Rahul',
    'Patil',
    'rahul.patil@example.com',
    '9822012345',
    DATE '1988-11-10',
    'MALE',
    'ACTIVE',
    'PENDING'
);

-- Duplicate customer based on email and phone
INSERT INTO SRC_CUSTOMER (
    CUSTOMER_ID,
    SOURCE_SYSTEM,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    DATE_OF_BIRTH,
    GENDER,
    CUSTOMER_STATUS,
    ETL_STATUS
)
VALUES (
    1004,
    'ORACLE_ECOM',
    'Mininath N.',
    'Navdkar',
    'mininath.navdkar@example.com',
    '9876543210',
    DATE '1990-05-15',
    'MALE',
    'ACTIVE',
    'PENDING'
);

-- Invalid email record for rejection testing
INSERT INTO SRC_CUSTOMER (
    CUSTOMER_ID,
    SOURCE_SYSTEM,
    FIRST_NAME,
    LAST_NAME,
    EMAIL_ADDRESS,
    PHONE_NUMBER,
    DATE_OF_BIRTH,
    GENDER,
    CUSTOMER_STATUS,
    ETL_STATUS
)
VALUES (
    1005,
    'ORACLE_ECOM',
    'Amit',
    'Kulkarni',
    'invalid-email',
    '9765432109',
    DATE '1995-03-12',
    'MALE',
    'ACTIVE',
    'PENDING'
);

INSERT INTO SRC_CUSTOMER_ADDRESS (
    ADDRESS_ID,
    CUSTOMER_ID,
    ADDRESS_TYPE,
    ADDRESS_LINE_1,
    CITY,
    STATE_NAME,
    POSTAL_CODE,
    COUNTRY_NAME,
    IS_PRIMARY
)
VALUES (
    501,
    1001,
    'HOME',
    '12 Shivaji Nagar',
    'Pune',
    'Maharashtra',
    '411005',
    'INDIA',
    'Y'
);

INSERT INTO SRC_CUSTOMER_ADDRESS (
    ADDRESS_ID,
    CUSTOMER_ID,
    ADDRESS_TYPE,
    ADDRESS_LINE_1,
    CITY,
    STATE_NAME,
    POSTAL_CODE,
    COUNTRY_NAME,
    IS_PRIMARY
)
VALUES (
    502,
    1002,
    'HOME',
    '45 Baner Road',
    'Pune',
    'Maharashtra',
    '411045',
    'INDIA',
    'Y'
);

INSERT INTO SRC_CUSTOMER_ADDRESS (
    ADDRESS_ID,
    CUSTOMER_ID,
    ADDRESS_TYPE,
    ADDRESS_LINE_1,
    CITY,
    STATE_NAME,
    POSTAL_CODE,
    COUNTRY_NAME,
    IS_PRIMARY
)
VALUES (
    503,
    1003,
    'SHIPPING',
    '21 MG Road',
    'Mumbai',
    'Maharashtra',
    '400001',
    'INDIA',
    'Y'
);

INSERT INTO SRC_CUSTOMER_ADDRESS (
    ADDRESS_ID,
    CUSTOMER_ID,
    ADDRESS_TYPE,
    ADDRESS_LINE_1,
    CITY,
    STATE_NAME,
    POSTAL_CODE,
    COUNTRY_NAME,
    IS_PRIMARY
)
VALUES (
    504,
    1004,
    'HOME',
    '12 Shivaji Nagar',
    'Pune',
    'Maharashtra',
    '411005',
    'INDIA',
    'Y'
);

INSERT INTO SRC_CUSTOMER_ADDRESS (
    ADDRESS_ID,
    CUSTOMER_ID,
    ADDRESS_TYPE,
    ADDRESS_LINE_1,
    CITY,
    STATE_NAME,
    POSTAL_CODE,
    COUNTRY_NAME,
    IS_PRIMARY
)
VALUES (
    505,
    1005,
    'HOME',
    '88 Station Road',
    'Nashik',
    'Maharashtra',
    '422001',
    'INDIA',
    'Y'
);

COMMIT;