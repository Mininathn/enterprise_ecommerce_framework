import json
import os
from datetime import datetime

# ---------------------------------------------------
# Jenkins Environment Variables
# ---------------------------------------------------
build_number = os.getenv("BUILD_NUMBER", "Local")
job_name = os.getenv("JOB_NAME", "Enterprise-Ecommerce-Framework")
branch = os.getenv("GIT_BRANCH", "main")
commit = os.getenv("GIT_COMMIT", "Unknown")
build_url = os.getenv("BUILD_URL", "")
workspace = os.getenv("WORKSPACE", os.getcwd())

# ---------------------------------------------------
# Paths
# ---------------------------------------------------
allure_dir = os.path.join(workspace, "allure-results")

dashboard_dir = os.path.join(workspace, "reports", "dashboard")
os.makedirs(dashboard_dir, exist_ok=True)

summary_file = os.path.join(dashboard_dir, "summary.json")

# ---------------------------------------------------
# Counters
# ---------------------------------------------------
total = 0
passed = 0
failed = 0
skipped = 0

api_passed = 0
db_passed = 0
etl_passed = 0

api_failed = 0
db_failed = 0
etl_failed = 0

# ---------------------------------------------------
# Read Allure Result Files
# ---------------------------------------------------
if os.path.exists(allure_dir):

    for file in os.listdir(allure_dir):

        if file.endswith("-result.json"):

            total += 1

            path = os.path.join(allure_dir, file)

            with open(path, encoding="utf-8") as f:

                result = json.load(f)

            status = result.get("status", "")

            name = result.get("name", "").lower()

            if status == "passed":
                passed += 1

                if "api" in name:
                    api_passed += 1
                elif "db" in name:
                    db_passed += 1
                else:
                    etl_passed += 1

            elif status == "failed":
                failed += 1

                if "api" in name:
                    api_failed += 1
                elif "db" in name:
                    db_failed += 1
                else:
                    etl_failed += 1

            else:
                skipped += 1

# ---------------------------------------------------
# Summary
# ---------------------------------------------------
summary = {

    "project": "Enterprise Ecommerce ETL Framework",

    "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    "build": {
        "number": build_number,
        "job": job_name,
        "branch": branch,
        "commit": commit,
        "url": build_url
    },

    "tests": {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped
    },

    "api": {
        "passed": api_passed,
        "failed": api_failed
    },

    "database": {
        "passed": db_passed,
        "failed": db_failed
    },

    "etl": {
        "passed": etl_passed,
        "failed": etl_failed
    },

    "docker": {
        "status": "Healthy"
    }

}

with open(summary_file, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print("=" * 60)
print("Enterprise Dashboard Generated")
print(summary_file)
print("=" * 60)
print(f"Total Tests : {total}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")
print(f"Skipped     : {skipped}")