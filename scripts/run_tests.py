import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_ROOT = PROJECT_ROOT / "reports"

HTML_REPORT_DIR = REPORT_ROOT / "html"
ALLURE_RESULTS_DIR = REPORT_ROOT / "allure-results"
JUNIT_REPORT_DIR = REPORT_ROOT / "junit"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run enterprise framework test suites."
    )

    parser.add_argument(
        "--suite",
        choices=[
            "all",
            "smoke",
            "regression",
            "api",
            "data_quality",
            "database",
        ],
        default="all",
        help="Test suite or marker to execute.",
    )

    return parser.parse_args()


def build_command(suite: str) -> list[str]:
    HTML_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ALLURE_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    JUNIT_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_name = (
        "regression"
        if suite == "all"
        else suite
    )

    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "-v",
        "--tb=short",
        f"--html={HTML_REPORT_DIR / f'{report_name}_report.html'}",
        "--self-contained-html",
        f"--alluredir={ALLURE_RESULTS_DIR}",
        "--clean-alluredir",
        f"--junitxml={JUNIT_REPORT_DIR / 'test-results.xml'}",
    ]

    if suite not in {
        "all",
        "regression",
    }:
        command.extend(
            [
                "-m",
                suite,
            ]
        )

    return command


def main() -> int:
    arguments = parse_arguments()
    command = build_command(arguments.suite)

    print(
        "Executing:",
        " ".join(str(value) for value in command),
    )

    completed_process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    return completed_process.returncode


if __name__ == "__main__":
    raise SystemExit(main())