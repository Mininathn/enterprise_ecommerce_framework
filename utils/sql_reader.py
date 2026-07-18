from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SQLReader:
    """Reads named SQL queries from SQL files."""

    @staticmethod
    def read_query(
        relative_file_path: str,
        query_name: str,
    ) -> str:
        """
        Read a named query enclosed by markers.

        Example:

        -- name: customer_count
        SELECT COUNT(*) FROM customer;
        -- end
        """

        file_path = PROJECT_ROOT / relative_file_path

        if not file_path.exists():
            raise FileNotFoundError(
                f"SQL file was not found: {file_path}"
            )

        file_content = file_path.read_text(encoding="utf-8")

        start_marker = f"-- name: {query_name}"
        end_marker = "-- end"

        start_index = file_content.find(start_marker)

        if start_index == -1:
            raise ValueError(
                f"Query '{query_name}' was not found in {file_path}"
            )

        query_start = start_index + len(start_marker)
        end_index = file_content.find(end_marker, query_start)

        if end_index == -1:
            raise ValueError(
                f"End marker was not found for query "
                f"'{query_name}' in {file_path}"
            )

        query = file_content[query_start:end_index].strip()

        if not query:
            raise ValueError(
                f"Query '{query_name}' is empty."
            )

        return query