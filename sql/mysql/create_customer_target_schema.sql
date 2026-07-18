-- ============================================================
-- Enterprise E-commerce Automation Framework
-- MySQL Target Schema
-- ============================================================

USE ecommerce_target_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS customer_xref;
DROP TABLE IF EXISTS customer_address;
DROP TABLE IF EXISTS customer_golden;
DROP TABLE IF EXISTS etl_rejected_record;
DROP TABLE IF EXISTS etl_batch_control;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE etl_batch_control (
    batch_id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_name          VARCHAR(100) NOT NULL,
    source_system       VARCHAR(50) NOT NULL,
    target_system       VARCHAR(50) NOT NULL,
    batch_status        VARCHAR(20) NOT NULL DEFAULT 'STARTED',
    source_count        INT DEFAULT 0,
    target_count        INT DEFAULT 0,
    rejected_count      INT DEFAULT 0,
    started_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP NULL,
    error_message       VARCHAR(1000),

    CONSTRAINT chk_batch_status
        CHECK (
            batch_status IN (
                'STARTED',
                'COMPLETED',
                'FAILED',
                'PARTIAL'
            )
        )
);

CREATE TABLE customer_golden (
    golden_customer_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    full_name           VARCHAR(120) NOT NULL,
    email_address       VARCHAR(120),
    phone_number        VARCHAR(20),
    date_of_birth       DATE,
    gender              VARCHAR(10),
    customer_status     VARCHAR(20) DEFAULT 'ACTIVE',
    source_system       VARCHAR(50) NOT NULL,
    source_record_count INT DEFAULT 1,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NULL DEFAULT NULL,

    CONSTRAINT uq_customer_email_phone
        UNIQUE (email_address, phone_number),

    CONSTRAINT chk_customer_status
        CHECK (
            customer_status IN (
                'ACTIVE',
                'INACTIVE',
                'BLOCKED'
            )
        )
);

CREATE TABLE customer_address (
    target_address_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    golden_customer_id  BIGINT NOT NULL,
    address_type        VARCHAR(20) DEFAULT 'HOME',
    address_line_1      VARCHAR(150) NOT NULL,
    address_line_2      VARCHAR(150),
    city                VARCHAR(80) NOT NULL,
    state_name          VARCHAR(80),
    postal_code         VARCHAR(20),
    country_name        VARCHAR(80) DEFAULT 'INDIA',
    is_primary          CHAR(1) DEFAULT 'Y',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_address_golden_customer
        FOREIGN KEY (golden_customer_id)
        REFERENCES customer_golden(golden_customer_id),

    CONSTRAINT chk_target_is_primary
        CHECK (is_primary IN ('Y', 'N'))
);

CREATE TABLE customer_xref (
    xref_id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    golden_customer_id   BIGINT NOT NULL,
    source_customer_id   BIGINT NOT NULL,
    source_system        VARCHAR(50) NOT NULL,
    match_rule           VARCHAR(100),
    match_score          DECIMAL(5,2),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_xref_golden_customer
        FOREIGN KEY (golden_customer_id)
        REFERENCES customer_golden(golden_customer_id),

    CONSTRAINT uq_source_customer
        UNIQUE (source_system, source_customer_id)
);

CREATE TABLE etl_rejected_record (
    rejection_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_id             BIGINT,
    source_table         VARCHAR(100) NOT NULL,
    source_record_id     VARCHAR(100),
    rejection_reason     VARCHAR(500) NOT NULL,
    rejected_payload     JSON,
    rejected_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rejection_batch
        FOREIGN KEY (batch_id)
        REFERENCES etl_batch_control(batch_id)
);

CREATE INDEX idx_golden_email
    ON customer_golden(email_address);

CREATE INDEX idx_golden_phone
    ON customer_golden(phone_number);

CREATE INDEX idx_xref_source_customer
    ON customer_xref(source_customer_id);