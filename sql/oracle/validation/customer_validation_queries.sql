-- ============================================================
-- Oracle customer source validation queries
-- ============================================================

-- name: total_source_count
SELECT COUNT(*)
FROM SRC_CUSTOMER
-- end


-- name: valid_source_count
SELECT COUNT(*)
FROM SRC_CUSTOMER
WHERE REGEXP_LIKE(
    EMAIL_ADDRESS,
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
AND REGEXP_LIKE(
    PHONE_NUMBER,
    '^[0-9]{10}$'
)
AND FIRST_NAME IS NOT NULL
AND LAST_NAME IS NOT NULL
-- end


-- name: invalid_source_count
SELECT COUNT(*)
FROM SRC_CUSTOMER
WHERE NOT REGEXP_LIKE(
    EMAIL_ADDRESS,
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
OR NOT REGEXP_LIKE(
    PHONE_NUMBER,
    '^[0-9]{10}$'
)
OR FIRST_NAME IS NULL
OR LAST_NAME IS NULL
-- end


-- name: distinct_valid_customer_count
SELECT COUNT(*)
FROM (
    SELECT
        LOWER(TRIM(EMAIL_ADDRESS)),
        TRIM(PHONE_NUMBER)
    FROM SRC_CUSTOMER
    WHERE REGEXP_LIKE(
        EMAIL_ADDRESS,
        '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )
    AND REGEXP_LIKE(
        PHONE_NUMBER,
        '^[0-9]{10}$'
    )
    AND FIRST_NAME IS NOT NULL
    AND LAST_NAME IS NOT NULL
    GROUP BY
        LOWER(TRIM(EMAIL_ADDRESS)),
        TRIM(PHONE_NUMBER)
)
-- end


-- name: valid_customer_records
SELECT
    CUSTOMER_ID,
    INITCAP(TRIM(FIRST_NAME)) AS FIRST_NAME,
    INITCAP(TRIM(LAST_NAME)) AS LAST_NAME,
    INITCAP(TRIM(FIRST_NAME))
        || ' '
        || INITCAP(TRIM(LAST_NAME)) AS FULL_NAME,
    LOWER(TRIM(EMAIL_ADDRESS)) AS EMAIL_ADDRESS,
    TRIM(PHONE_NUMBER) AS PHONE_NUMBER,
    DATE_OF_BIRTH,
    UPPER(TRIM(GENDER)) AS GENDER,
    UPPER(TRIM(CUSTOMER_STATUS)) AS CUSTOMER_STATUS,
    UPPER(TRIM(SOURCE_SYSTEM)) AS SOURCE_SYSTEM
FROM SRC_CUSTOMER
WHERE REGEXP_LIKE(
    EMAIL_ADDRESS,
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
AND REGEXP_LIKE(
    PHONE_NUMBER,
    '^[0-9]{10}$'
)
AND FIRST_NAME IS NOT NULL
AND LAST_NAME IS NOT NULL
ORDER BY CUSTOMER_ID
-- end


-- name: duplicate_customer_groups
SELECT
    LOWER(TRIM(EMAIL_ADDRESS)) AS EMAIL_ADDRESS,
    TRIM(PHONE_NUMBER) AS PHONE_NUMBER,
    COUNT(*) AS SOURCE_RECORD_COUNT
FROM SRC_CUSTOMER
WHERE REGEXP_LIKE(
    EMAIL_ADDRESS,
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
AND REGEXP_LIKE(
    PHONE_NUMBER,
    '^[0-9]{10}$'
)
AND FIRST_NAME IS NOT NULL
AND LAST_NAME IS NOT NULL
GROUP BY
    LOWER(TRIM(EMAIL_ADDRESS)),
    TRIM(PHONE_NUMBER)
HAVING COUNT(*) > 1
ORDER BY EMAIL_ADDRESS, PHONE_NUMBER
-- end


-- name: invalid_customer_records
SELECT
    CUSTOMER_ID,
    EMAIL_ADDRESS,
    PHONE_NUMBER
FROM SRC_CUSTOMER
WHERE NOT REGEXP_LIKE(
    EMAIL_ADDRESS,
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
OR NOT REGEXP_LIKE(
    PHONE_NUMBER,
    '^[0-9]{10}$'
)
OR FIRST_NAME IS NULL
OR LAST_NAME IS NULL
ORDER BY CUSTOMER_ID
-- end