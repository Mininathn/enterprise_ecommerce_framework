from core.etl.customer_etl import CustomerETL
from core.validation.data_quality_engine import (
    DataQualityEngine,
)


def main() -> None:
    print("Running customer ETL...")
    etl_result = CustomerETL().run(reset_target=True)

    print("\nETL result")
    print("--------------------------------")

    for key, value in etl_result.items():
        print(f"{key}: {value}")

    print("\nRunning data-quality rules...")
    engine = DataQualityEngine()
    results = engine.run_all()
    summary = engine.create_summary(results)
    report_file = engine.save_report(results)

    print("\nData-quality summary")
    print("--------------------------------")
    print(f"Total rules : {summary['total_rules']}")
    print(f"Passed      : {summary['passed_rules']}")
    print(f"Failed      : {summary['failed_rules']}")
    print(f"Errors      : {summary['error_rules']}")
    print(f"Report      : {report_file}")

    print("\nRule results")
    print("--------------------------------")

    for result in results:
        print(
            f"{result['status']:6} | "
            f"{result['rule_id']} | "
            f"{result['message']}"
        )


if __name__ == "__main__":
    main()