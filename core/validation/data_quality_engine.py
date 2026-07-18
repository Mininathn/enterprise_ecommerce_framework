import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from connections.mysql_connection import MySQLDatabase
from connections.oracle_connection import OracleDatabase
from utils.logger import get_logger


logger = get_logger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_RULE_FILE = (
    PROJECT_ROOT
    / "config"
    / "data_quality_rules.yaml"
)

DEFAULT_REPORT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "data_quality_report.json"
)


class DataQualityEngine:
    """Execute configuration-driven data-quality rules."""

    SUPPORTED_DATABASES = {
        "oracle",
        "mysql",
    }

    SUPPORTED_RULE_TYPES = {
        "not_null",
        "unique",
        "allowed_values",
        "regex",
        "length",
        "range",
        "referential_integrity",
        "row_count",
        "custom_sql",
    }

    VALID_IDENTIFIER = re.compile(
        r"^[A-Za-z_][A-Za-z0-9_$#]*$"
    )

    def __init__(
        self,
        rule_file: Path = DEFAULT_RULE_FILE,
    ) -> None:
        """Initialize database clients and load enabled rules."""

        self.rule_file = rule_file
        self.oracle_database = OracleDatabase()
        self.mysql_database = MySQLDatabase()
        self.rules = self.load_rules()

    def load_rules(self) -> list[dict[str, Any]]:
        """Load enabled data-quality rules from YAML."""

        if not self.rule_file.exists():
            raise FileNotFoundError(
                "Data-quality rule file was not found: "
                f"{self.rule_file}"
            )

        with self.rule_file.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file) or {}

        rules = config.get("data_quality_rules")

        if not isinstance(rules, list):
            raise ValueError(
                "The 'data_quality_rules' section must be a list."
            )

        enabled_rules = [
            rule
            for rule in rules
            if rule.get("enabled", True)
        ]

        rule_ids = [
            rule.get("rule_id")
            for rule in enabled_rules
        ]

        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError(
                "Duplicate data-quality rule IDs were found."
            )

        for rule in enabled_rules:
            self.validate_rule_configuration(rule)

        logger.info(
            "Loaded %s enabled data-quality rules.",
            len(enabled_rules),
        )

        return enabled_rules

    def validate_rule_configuration(
        self,
        rule: dict[str, Any],
    ) -> None:
        """Validate the mandatory structure of one rule."""

        mandatory_fields = {
            "rule_id",
            "description",
            "database",
            "rule_type",
        }

        missing_fields = mandatory_fields - rule.keys()

        if missing_fields:
            raise ValueError(
                "Rule is missing mandatory fields: "
                f"{missing_fields}"
            )

        database = str(
            rule["database"]
        ).lower()

        rule_type = str(
            rule["rule_type"]
        ).lower()

        if database not in self.SUPPORTED_DATABASES:
            raise ValueError(
                f"Unsupported database '{database}' in "
                f"rule '{rule['rule_id']}'."
            )

        if rule_type not in self.SUPPORTED_RULE_TYPES:
            raise ValueError(
                f"Unsupported rule type '{rule_type}' in "
                f"rule '{rule['rule_id']}'."
            )

        if (
            rule_type != "custom_sql"
            and not rule.get("table")
        ):
            raise ValueError(
                "Table is required for rule "
                f"'{rule['rule_id']}'."
            )

        if (
            rule_type
            not in {
                "row_count",
                "custom_sql",
            }
            and not rule.get("columns")
        ):
            raise ValueError(
                "Columns are required for rule "
                f"'{rule['rule_id']}'."
            )

        if rule.get("table"):
            self.validate_identifier(
                rule["table"]
            )

        for column in rule.get("columns", []):
            self.validate_identifier(column)

        if rule.get("parent_table"):
            self.validate_identifier(
                rule["parent_table"]
            )

        for column in rule.get(
            "parent_columns",
            [],
        ):
            self.validate_identifier(column)

    def validate_identifier(
        self,
        identifier: str,
    ) -> None:
        """Prevent unsafe table or column identifiers."""

        if not self.VALID_IDENTIFIER.fullmatch(
            str(identifier)
        ):
            raise ValueError(
                f"Invalid SQL identifier: {identifier}"
            )

    @staticmethod
    def quote_literal(
        value: Any,
    ) -> str:
        """Convert a Python value into a SQL literal."""

        if value is None:
            return "NULL"

        if isinstance(value, bool):
            return "1" if value else "0"

        if isinstance(value, (int, float)):
            return str(value)

        escaped_value = str(value).replace(
            "'",
            "''",
        )

        return f"'{escaped_value}'"

    def build_not_null_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a NOT NULL validation query."""

        conditions = [
            f"{column} IS NULL"
            for column in rule["columns"]
        ]

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} "
            f"WHERE {' OR '.join(conditions)}"
        )

    def build_unique_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a duplicate-group validation query."""

        column_list = ", ".join(
            rule["columns"]
        )

        return (
            "SELECT COUNT(*) "
            "FROM ("
            f"SELECT {column_list} "
            f"FROM {rule['table']} "
            f"GROUP BY {column_list} "
            "HAVING COUNT(*) > 1"
            ") duplicate_groups"
        )

    def build_allowed_values_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build an allowed-values validation query."""

        allowed_values = rule.get(
            "allowed_values"
        )

        if not isinstance(
            allowed_values,
            list,
        ):
            raise ValueError(
                "allowed_values must be provided for "
                f"rule '{rule['rule_id']}'."
            )

        formatted_values = ", ".join(
            self.quote_literal(value)
            for value in allowed_values
        )

        conditions = [
            (
                f"{column} IS NULL OR "
                f"UPPER(TRIM({column})) NOT IN "
                f"({formatted_values})"
            )
            for column in rule["columns"]
        ]

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} "
            f"WHERE {' OR '.join(conditions)}"
        )

    def build_regex_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build an Oracle or MySQL regex validation query."""

        pattern = self.quote_literal(
            rule["pattern"]
        )

        database = str(
            rule["database"]
        ).lower()

        conditions: list[str] = []

        for column in rule["columns"]:
            if database == "oracle":
                conditions.append(
                    f"{column} IS NULL OR "
                    f"NOT REGEXP_LIKE("
                    f"{column}, {pattern}"
                    f")"
                )
            else:
                conditions.append(
                    f"{column} IS NULL OR "
                    f"{column} NOT REGEXP {pattern}"
                )

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} "
            f"WHERE {' OR '.join(conditions)}"
        )

    def build_length_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a string-length validation query."""

        minimum_length = int(
            rule["minimum_length"]
        )

        maximum_length = int(
            rule["maximum_length"]
        )

        conditions = [
            (
                f"{column} IS NULL OR "
                f"LENGTH(TRIM({column})) "
                f"< {minimum_length} OR "
                f"LENGTH(TRIM({column})) "
                f"> {maximum_length}"
            )
            for column in rule["columns"]
        ]

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} "
            f"WHERE {' OR '.join(conditions)}"
        )

    def build_range_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a numeric range validation query."""

        minimum_value = self.quote_literal(
            rule["minimum_value"]
        )

        maximum_value = self.quote_literal(
            rule["maximum_value"]
        )

        conditions = [
            (
                f"{column} IS NULL OR "
                f"{column} < {minimum_value} OR "
                f"{column} > {maximum_value}"
            )
            for column in rule["columns"]
        ]

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} "
            f"WHERE {' OR '.join(conditions)}"
        )

    def build_referential_integrity_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a referential-integrity validation query."""

        child_columns = rule["columns"]

        parent_columns = rule.get(
            "parent_columns"
        )

        if not isinstance(
            parent_columns,
            list,
        ):
            raise ValueError(
                "parent_columns are required for rule "
                f"'{rule['rule_id']}'."
            )

        if len(child_columns) != len(parent_columns):
            raise ValueError(
                "Child and parent column counts do not "
                "match for rule "
                f"'{rule['rule_id']}'."
            )

        join_conditions = [
            f"child.{child} = parent.{parent}"
            for child, parent in zip(
                child_columns,
                parent_columns,
            )
        ]

        child_not_null_conditions = [
            f"child.{column} IS NOT NULL"
            for column in child_columns
        ]

        parent_null_condition = (
            f"parent.{parent_columns[0]} IS NULL"
        )

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']} child "
            f"LEFT JOIN {rule['parent_table']} parent "
            f"ON {' AND '.join(join_conditions)} "
            f"WHERE "
            f"{' AND '.join(child_not_null_conditions)} "
            f"AND {parent_null_condition}"
        )

    def build_row_count_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build a row-count validation query."""

        return (
            "SELECT COUNT(*) "
            f"FROM {rule['table']}"
        )

    def build_query(
        self,
        rule: dict[str, Any],
    ) -> str:
        """Build validation SQL for one configured rule."""

        rule_type = str(
            rule["rule_type"]
        ).lower()

        builders = {
            "not_null": self.build_not_null_query,
            "unique": self.build_unique_query,
            "allowed_values": (
                self.build_allowed_values_query
            ),
            "regex": self.build_regex_query,
            "length": self.build_length_query,
            "range": self.build_range_query,
            "referential_integrity": (
                self.build_referential_integrity_query
            ),
            "row_count": self.build_row_count_query,
        }

        if rule_type == "custom_sql":
            sql = rule.get("sql")

            if not sql or not str(sql).strip():
                raise ValueError(
                    "Custom SQL is missing for rule "
                    f"'{rule['rule_id']}'."
                )

            return str(sql).strip()

        builder = builders[rule_type]

        return builder(rule)

    def execute_scalar(
        self,
        database_name: str,
        query: str,
    ) -> Any:
        """Execute a scalar query on Oracle or MySQL."""

        database_name = database_name.lower()

        if database_name == "oracle":
            return (
                self.oracle_database
                .execute_scalar(query)
            )

        if database_name == "mysql":
            return (
                self.mysql_database
                .execute_scalar(query)
            )

        raise ValueError(
            f"Unsupported database: {database_name}"
        )

    def evaluate_rule(
        self,
        rule: dict[str, Any],
        actual_value: int,
    ) -> tuple[str, str]:
        """Evaluate a query result against thresholds."""

        rule_type = str(
            rule["rule_type"]
        ).lower()

        if rule_type == "row_count":
            minimum_count = int(
                rule.get(
                    "minimum_count",
                    0,
                )
            )

            maximum_count = int(
                rule.get(
                    "maximum_count",
                    actual_value,
                )
            )

            passed = (
                minimum_count
                <= actual_value
                <= maximum_count
            )

            message = (
                f"Actual row count={actual_value}; "
                f"expected range="
                f"{minimum_count} to {maximum_count}"
            )

        else:
            max_failed_rows = int(
                rule.get(
                    "max_failed_rows",
                    0,
                )
            )

            passed = (
                actual_value
                <= max_failed_rows
            )

            message = (
                f"Failed rows={actual_value}; "
                f"maximum allowed="
                f"{max_failed_rows}"
            )

        status = (
            "PASSED"
            if passed
            else "FAILED"
        )

        return status, message

    def execute_rule(
        self,
        rule: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute and evaluate one data-quality rule."""

        started_at = datetime.now()

        query = self.build_query(rule)

        logger.info(
            "Executing DQ rule %s on %s.",
            rule["rule_id"],
            rule["database"],
        )

        try:
            query_result = self.execute_scalar(
                database_name=str(
                    rule["database"]
                ),
                query=query,
            )

            actual_value = int(
                query_result or 0
            )

            status, message = self.evaluate_rule(
                rule=rule,
                actual_value=actual_value,
            )

            result = {
                "rule_id": rule["rule_id"],
                "description": (
                    rule["description"]
                ),
                "database": rule["database"],
                "table": rule.get("table"),
                "rule_type": (
                    rule["rule_type"]
                ),
                "status": status,
                "actual_value": actual_value,
                "message": message,
                "query": query,
                "started_at": (
                    started_at.isoformat()
                ),
                "completed_at": (
                    datetime.now().isoformat()
                ),
            }

            logger.info(
                "DQ rule %s completed with "
                "status %s. %s",
                rule["rule_id"],
                status,
                message,
            )

            return result

        except Exception as error:
            logger.exception(
                "DQ rule %s failed during execution.",
                rule["rule_id"],
            )

            return {
                "rule_id": rule["rule_id"],
                "description": (
                    rule["description"]
                ),
                "database": rule["database"],
                "table": rule.get("table"),
                "rule_type": (
                    rule["rule_type"]
                ),
                "status": "ERROR",
                "actual_value": None,
                "message": str(error),
                "query": query,
                "started_at": (
                    started_at.isoformat()
                ),
                "completed_at": (
                    datetime.now().isoformat()
                ),
            }

    def get_rule(
        self,
        rule_id: str,
    ) -> dict[str, Any]:
        """Return one configured rule by ID."""

        for rule in self.rules:
            if rule["rule_id"] == rule_id:
                return rule

        raise KeyError(
            "Data-quality rule was not found: "
            f"{rule_id}"
        )

    def run_rule(
        self,
        rule_id: str,
    ) -> dict[str, Any]:
        """Execute one configured rule by ID."""

        rule = self.get_rule(
            rule_id=rule_id,
        )

        return self.execute_rule(
            rule=rule,
        )

    def run_all(
        self,
    ) -> list[dict[str, Any]]:
        """Execute all enabled rules."""

        results = [
            self.execute_rule(rule)
            for rule in self.rules
        ]

        passed_count = sum(
            result["status"] == "PASSED"
            for result in results
        )

        failed_count = sum(
            result["status"] == "FAILED"
            for result in results
        )

        error_count = sum(
            result["status"] == "ERROR"
            for result in results
        )

        logger.info(
            "Data-quality execution completed. "
            "Total=%s, Passed=%s, Failed=%s, "
            "Errors=%s",
            len(results),
            passed_count,
            failed_count,
            error_count,
        )

        return results

    def create_summary(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create an overall execution summary."""

        return {
            "generated_at": (
                datetime.now().isoformat()
            ),
            "total_rules": len(results),
            "passed_rules": sum(
                result["status"] == "PASSED"
                for result in results
            ),
            "failed_rules": sum(
                result["status"] == "FAILED"
                for result in results
            ),
            "error_rules": sum(
                result["status"] == "ERROR"
                for result in results
            ),
            "results": results,
        }

    def save_report(
        self,
        results: list[dict[str, Any]],
        report_file: Path = DEFAULT_REPORT_FILE,
    ) -> Path:
        """Save data-quality results as a JSON report."""

        report_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        summary = self.create_summary(
            results=results,
        )

        report_file.write_text(
            json.dumps(
                summary,
                indent=4,
                default=str,
            ),
            encoding="utf-8",
        )

        logger.info(
            "Data-quality report saved: %s",
            report_file,
        )

        return report_file