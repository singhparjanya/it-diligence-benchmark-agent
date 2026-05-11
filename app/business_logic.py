from data_loader import load_excel_data


def apply_filters(dataframe, filters):
    """
    Applies multiple filters to a dataframe.

    Example:
    filters = {
        "Sector": "Retail",
        "Target Geography": "UK"
    }
    """

    filtered_data = dataframe.copy()

    for column_name, filter_value in filters.items():

        if column_name not in filtered_data.columns:
            print(f"Warning: Column '{column_name}' not found. Skipping this filter.")
            continue

        filtered_data = filtered_data[
            filtered_data[column_name].astype(str).str.lower() == str(filter_value).lower()
        ]

    return filtered_data


def get_average_metric(metric_name, filters):
    """
    Calculates the average of a selected metric after applying filters.

    Examples:

    get_average_metric(
        metric_name="IT Spend (m)",
        filters={"Sector": "Healthcare"}
    )

    get_average_metric(
        metric_name="IT Spend (m)",
        filters={"Target Geography": "UK"}
    )

    get_average_metric(
        metric_name="IT Standalone Cost (m)",
        filters={"Sector": "Retail", "Target Geography": "UK"}
    )
    """

    data = load_excel_data()

    primary_kpis = data["primary_kpis"]

    if metric_name not in primary_kpis.columns:
        print(f"Error: Metric '{metric_name}' was not found in Primary_KPIs.")
        print("Available columns are:")
        print(list(primary_kpis.columns))
        return

    filtered_data = apply_filters(primary_kpis, filters)

    record_count = len(filtered_data)

    print("=" * 80)
    print("Question Type: Average KPI Benchmark Lookup")
    print("=" * 80)

    print("Source sheet: Primary_KPIs")
    print(f"Metric selected: {metric_name}")
    print(f"Filters applied: {filters}")
    print(f"Matching records: {record_count}")
    print(f"Calculation logic: Average of {metric_name} after applying filters")

    if record_count == 0:
        print("Result: No matching records found.")
        return

    average_value = filtered_data[metric_name].mean()

    print(f"Average {metric_name}: {round(average_value, 2)}")

    if record_count < 5:
        print("Note: Small sample size; treat this as directional.")

    print("\nSupporting table:")
    print(
        filtered_data[
            ["Year", "Project Name", "Deal Type", "Sector", "Target Geography", metric_name]
        ]
    )


if __name__ == "__main__":

    get_average_metric(
    metric_name="IT Standalone Cost (m)",
    filters={
        "Deal Type": "ITDD"
    }
)