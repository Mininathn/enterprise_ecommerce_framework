from core.etl.customer_etl import CustomerETL


def main() -> None:
    etl = CustomerETL()
    result = etl.run(reset_target=True)

    print("\nCustomer ETL execution result")
    print("--------------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()