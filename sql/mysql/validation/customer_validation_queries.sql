-- ============================================================
-- MySQL customer target validation queries
-- ============================================================

-- name: golden_customer_count
SELECT COUNT(*)
FROM customer_golden
-- end


-- name: xref_count
SELECT COUNT(*)
FROM customer_xref
-- end


-- name: rejected_record_count
SELECT COUNT(*)
FROM etl_rejected_record
WHERE source_table = 'SRC_CUSTOMER'
-- end


-- name: golden_customer_records
SELECT
    golden_customer_id,
    first_name,
    last_name,
    full_name,
    email_address,
    phone_number,
    date_of_birth,
    gender,
    customer_status,
    source_system,
    source_record_count
FROM customer_golden
ORDER BY golden_customer_id
-- end


-- name: customer_xref_records
SELECT
    golden_customer_id,
    source_customer_id,
    source_system,
    match_rule,
    match_score
FROM customer_xref
ORDER BY source_customer_id
-- end


-- name: duplicate_golden_records
SELECT
    email_address,
    phone_number,
    COUNT(*) AS duplicate_count
FROM customer_golden
GROUP BY
    email_address,
    phone_number
HAVING COUNT(*) > 1
-- end


-- name: orphan_xref_records
SELECT
    x.xref_id,
    x.golden_customer_id,
    x.source_customer_id
FROM customer_xref x
LEFT JOIN customer_golden g
    ON x.golden_customer_id = g.golden_customer_id
WHERE g.golden_customer_id IS NULL
-- end


-- name: orphan_address_records
SELECT
    a.target_address_id,
    a.golden_customer_id
FROM customer_address a
LEFT JOIN customer_golden g
    ON a.golden_customer_id = g.golden_customer_id
WHERE g.golden_customer_id IS NULL
-- end


-- name: rejected_source_ids
SELECT
    source_record_id,
    rejection_reason
FROM etl_rejected_record
WHERE source_table = 'SRC_CUSTOMER'
ORDER BY source_record_id
-- end


-- name: latest_batch_record
SELECT
    batch_id,
    batch_status,
    source_count,
    target_count,
    rejected_count
FROM etl_batch_control
ORDER BY batch_id DESC
LIMIT 1
-- end