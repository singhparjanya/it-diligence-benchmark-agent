from data_loader import load_excel_data


# ------------------------------------------------------------
# 1. BASIC FILTERING FUNCTION
# ------------------------------------------------------------

def apply_filters(dataframe, filters):
    """
    Applies filters like Sector, Deal Type, Target Geography, Year.
    """

    filtered_data = dataframe.copy()

    for column_name, filter_value in filters.items():

        if filter_value is None:
            continue

        if column_name not in filtered_data.columns:
            print(f"Warning: Column '{column_name}' not found. Skipping this filter.")
            continue

        filtered_data = filtered_data[
            filtered_data[column_name].astype(str).str.lower() == str(filter_value).lower()
        ]

    return filtered_data


# ------------------------------------------------------------
# 2. DERIVED METRICS
# ------------------------------------------------------------

def prepare_primary_kpis():
    """
    Loads Primary_KPIs and adds calculated KPI columns.
    """

    data = load_excel_data()
    primary_kpis = data["primary_kpis"].copy()

    primary_kpis["IT Spend % Revenue"] = primary_kpis["IT Spend (m)"] / primary_kpis["Revenue (m)"]
    primary_kpis["IT Standalone Cost % Revenue"] = primary_kpis["IT Standalone Cost (m)"] / primary_kpis["Revenue (m)"]
    primary_kpis["IT Spend per Employee"] = (primary_kpis["IT Spend (m)"] * 1_000_000) / primary_kpis["Org Size"]
    primary_kpis["IT Spend per IT FTE"] = (primary_kpis["IT Spend (m)"] * 1_000_000) / primary_kpis["IT Team"]
    primary_kpis["Revenue per IT FTE"] = (primary_kpis["Revenue (m)"] * 1_000_000) / primary_kpis["IT Team"]
    primary_kpis["IT Team % Org Size"] = primary_kpis["IT Team"] / primary_kpis["Org Size"]

    return primary_kpis


# ------------------------------------------------------------
# 3. SIMPLE TEXT UNDERSTANDING
# ------------------------------------------------------------

def detect_filters(user_question):
    """
    Detects basic filters from the user's question.
    This is a simple rule-based version.
    Later, Azure AI Foundry agent will do this better.
    """

    question = user_question.lower()

    filters = {}

    # Sector filters
    if "healthcare" in question:
        filters["Sector"] = "Healthcare"
    elif "retail" in question:
        filters["Sector"] = "Retail"
    elif "logistics" in question:
        filters["Sector"] = "Logistics"
    elif "automotive" in question or "automobile" in question or "auto" in question:
        filters["Sector"] = "Automobiles & Components"
    elif "consumer" in question:
        filters["Sector"] = "Consumer Products"
    elif "software" in question:
        filters["Sector"] = "Software & Services"
    elif "pharma" in question or "life science" in question:
        filters["Sector"] = "Pharma, Biotech and Lifescience"

    # Geography filters
    if "uk" in question:
        filters["Target Geography"] = "UK"
    elif "us" in question or "usa" in question:
        filters["Target Geography"] = "US"
    elif "india" in question:
        filters["Target Geography"] = "India"
    elif "europe" in question:
        filters["Target Geography"] = "Europe"
    elif "apac" in question:
        filters["Target Geography"] = "APAC"

    # Deal type filters
    if "itdd" in question or "it dd" in question:
        filters["Deal Type"] = "ITDD"
    elif "carve" in question:
        filters["Deal Type"] = "Carve-out"
    elif "integration" in question:
        filters["Deal Type"] = "Integration"
    elif "transformation" in question:
        filters["Deal Type"] = "Transformation"
    elif "standalone" in question:
        filters["Deal Type"] = "Standalone"
    elif "product dd" in question:
        filters["Deal Type"] = "Product DD"
    elif "ai dd" in question:
        filters["Deal Type"] = "AI DD"

    return filters


def detect_metric(user_question):
    """
    Detects which KPI metric the user wants.
    """

    question = user_question.lower()

    if "% of revenue" in question or "percentage of revenue" in question or "as % revenue" in question:
        return "IT Spend % Revenue"

    if "standalone" in question:
        return "IT Standalone Cost (m)"

    if "revenue" in question and "it spend" not in question and "it cost" not in question:
        return "Revenue (m)"

    if "org size" in question or "organization size" in question or "employees" in question:
        return "Org Size"

    if "it team" in question or "it fte" in question:
        return "IT Team"

    if "application" in question or "apps" in question:
        return "# Applications"

    # Default metric
    return "IT Spend (m)"


def detect_intent(user_question):
    """
    Detects what type of output the user wants.
    """

    question = user_question.lower()

    if "trend" in question or "over time" in question or "by year" in question or "last 3 years" in question:
        return "trend"

    if "breakdown" in question or "capex" in question or "opex" in question:
        return "cost_breakdown"

    if "application" in question or "vendor" in question or "saas" in question or "erp" in question:
        return "application_benchmark"

    return "average_metric"


# ------------------------------------------------------------
# 4. OUTPUT FUNCTIONS
# ------------------------------------------------------------

def get_average_metric(user_question):
    """
    Handles average KPI questions.
    """

    primary_kpis = prepare_primary_kpis()

    metric_name = detect_metric(user_question)
    filters = detect_filters(user_question)

    filtered_data = apply_filters(primary_kpis, filters)

    record_count = len(filtered_data)

    print("\n" + "=" * 100)
    print("ANSWER TYPE: Average KPI Benchmark Lookup")
    print("=" * 100)

    print(f"User question: {user_question}")
    print("Source sheet: Primary_KPIs")
    print(f"Metric selected: {metric_name}")
    print(f"Filters applied: {filters if filters else 'No filters applied'}")
    print(f"Matching records: {record_count}")
    print(f"Calculation logic: Average of {metric_name} after applying filters")

    if record_count == 0:
        print("Result: No matching records found.")
        return

    average_value = filtered_data[metric_name].mean()
    median_value = filtered_data[metric_name].median()
    min_value = filtered_data[metric_name].min()
    max_value = filtered_data[metric_name].max()

    print("\nResult:")
    print(f"Average {metric_name}: {round(average_value, 4)}")
    print(f"Median {metric_name}: {round(median_value, 4)}")
    print(f"Minimum {metric_name}: {round(min_value, 4)}")
    print(f"Maximum {metric_name}: {round(max_value, 4)}")

    if record_count < 5:
        print("\nNote: Small sample size; treat this result as directional.")

    print("\nSupporting table:")
    display_columns = [
        "Year",
        "Project Name",
        "Deal Type",
        "Sector",
        "Target Geography",
        metric_name
    ]

    print(filtered_data[display_columns])


def get_metric_trend(user_question):
    """
    Handles trend questions.
    """

    primary_kpis = prepare_primary_kpis()

    metric_name = detect_metric(user_question)
    filters = detect_filters(user_question)

    filtered_data = apply_filters(primary_kpis, filters)

    record_count = len(filtered_data)

    print("\n" + "=" * 100)
    print("ANSWER TYPE: Trend Analysis")
    print("=" * 100)

    print(f"User question: {user_question}")
    print("Source sheet: Primary_KPIs")
    print(f"Metric selected: {metric_name}")
    print(f"Filters applied: {filters if filters else 'No filters applied'}")
    print(f"Matching records: {record_count}")
    print(f"Calculation logic: Group by Year and calculate average {metric_name}")

    if record_count == 0:
        print("Result: No matching records found.")
        return

    trend = (
        filtered_data
        .groupby("Year")
        .agg(
            Average_Value=(metric_name, "mean"),
            Median_Value=(metric_name, "median"),
            Project_Count=("Project Name", "count")
        )
        .reset_index()
        .sort_values("Year")
    )

    print("\nYear-wise trend table:")
    print(trend)

    print("\nChart-ready output:")
    print("Chart type: Line chart")
    print("X-axis: Year")
    print(f"Y-axis: Average {metric_name}")

    if record_count < 5:
        print("\nNote: Small sample size; treat this trend as directional.")


def get_cost_breakdown(user_question):
    """
    Handles cost breakdown questions.
    """

    data = load_excel_data()

    cost_breakdown = data["cost_breakdown"].copy()
    primary_kpis = data["primary_kpis"].copy()

    filters = detect_filters(user_question)

    merged_data = cost_breakdown.merge(
        primary_kpis[["Project Name", "Deal Type", "Sector", "Target Geography"]],
        on="Project Name",
        how="left"
    )

    filtered_data = apply_filters(merged_data, filters)

    record_count = len(filtered_data)

    print("\n" + "=" * 100)
    print("ANSWER TYPE: Cost Breakdown")
    print("=" * 100)

    print(f"User question: {user_question}")
    print("Source sheet: Cost_Breakdown")
    print(f"Filters applied: {filters if filters else 'No filters applied'}")
    print(f"Matching records: {record_count}")
    print("Calculation logic: Average cost by category after applying filters")

    if record_count == 0:
        print("Result: No matching records found.")
        return

    cost_columns = [
        "IT capex",
        "IT opex",
        "IT Personnel Cost (m)",
        "Outsourcing Cost (m)",
        "Licensing Cost (m)",
        "Infrastructure Cost (m)",
        "IT Standalone Cost (m)",
        "Recurring Cost (m)",
        "One-off Cost (m)"
    ]

    summary = filtered_data[cost_columns].mean().reset_index()
    summary.columns = ["Cost Category", "Average Cost"]

    print("\nCost breakdown summary:")
    print(summary)

    if record_count < 5:
        print("\nNote: Small sample size; treat this as directional.")


def get_application_benchmark(user_question):
    """
    Handles application benchmark questions.
    """

    data = load_excel_data()

    applications = data["applications"].copy()

    question = user_question.lower()

    filters = {}

    if "saas" in question:
        filters["Hosting Type"] = "SaaS (Cloud)"

    if "microsoft" in question:
        filters["Vendor"] = "Microsoft"
    elif "salesforce" in question:
        filters["Vendor"] = "Salesforce"
    elif "sap" in question:
        filters["Vendor"] = "SAP"
    elif "oracle" in question:
        filters["Vendor"] = "Oracle"
    elif "workday" in question:
        filters["Vendor"] = "Workday"

    filtered_data = apply_filters(applications, filters)

    record_count = len(filtered_data)

    print("\n" + "=" * 100)
    print("ANSWER TYPE: Application Benchmark")
    print("=" * 100)

    print(f"User question: {user_question}")
    print("Source sheet: Applications")
    print(f"Filters applied: {filters if filters else 'No filters applied'}")
    print(f"Matching records: {record_count}")
    print("Calculation logic: Filter application records and calculate annual cost per user")

    if record_count == 0:
        print("Result: No matching records found.")
        return

    filtered_data["Annual Cost per User"] = filtered_data["Annual Cost"] / filtered_data["# Users"]

    display_columns = [
        "Year",
        "Project Name",
        "Application Type",
        "Application Name",
        "Vendor",
        "Pricing Model",
        "Hosting Type",
        "# Users",
        "Annual Cost",
        "Annual Cost per User"
    ]

    print("\nApplication benchmark table:")
    print(filtered_data[display_columns])

    print("\nNote: Application annual cost formula will be finalized once real data is available.")


# ------------------------------------------------------------
# 5. LOCAL MVP AGENT
# ------------------------------------------------------------

def answer_question(user_question):
    """
    This is the local MVP agent.
    It reads the user question, detects intent, and calls the correct function.
    """

    intent = detect_intent(user_question)

    if intent == "trend":
        get_metric_trend(user_question)

    elif intent == "cost_breakdown":
        get_cost_breakdown(user_question)

    elif intent == "application_benchmark":
        get_application_benchmark(user_question)

    else:
        get_average_metric(user_question)


if __name__ == "__main__":

    print("\nIT Diligence Benchmark Agent - Local MVP")
    print("Type a benchmark question.")
    print("Type 'exit' to stop.")

    while True:
        user_question = input("\nAsk a question: ")

        if user_question.lower() == "exit":
            print("Exiting local MVP agent.")
            break

        answer_question(user_question)