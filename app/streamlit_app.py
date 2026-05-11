import streamlit as st
import pandas as pd
from data_loader import load_excel_data


st.set_page_config(
    page_title="IT Diligence Benchmark Agent",
    page_icon="📊",
    layout="wide"
)


# ------------------------------------------------------------
# BASIC DATA HELPERS
# ------------------------------------------------------------

def apply_filters(dataframe, filters):
    filtered_data = dataframe.copy()

    for column_name, filter_value in filters.items():
        if column_name not in filtered_data.columns:
            continue

        filtered_data = filtered_data[
            filtered_data[column_name].astype(str).str.lower() == str(filter_value).lower()
        ]

    return filtered_data


def prepare_primary_kpis():
    data = load_excel_data()
    primary_kpis = data["primary_kpis"].copy()

    primary_kpis["IT Spend % Revenue"] = (
        primary_kpis["IT Spend (m)"] / primary_kpis["Revenue (m)"]
    )

    primary_kpis["IT Standalone Cost % Revenue"] = (
        primary_kpis["IT Standalone Cost (m)"] / primary_kpis["Revenue (m)"]
    )

    primary_kpis["IT Spend per Employee"] = (
        primary_kpis["IT Spend (m)"] * 1_000_000 / primary_kpis["Org Size"]
    )

    primary_kpis["IT Spend per IT FTE"] = (
        primary_kpis["IT Spend (m)"] * 1_000_000 / primary_kpis["IT Team"]
    )

    return primary_kpis


# ------------------------------------------------------------
# SIMPLE QUERY UNDERSTANDING
# ------------------------------------------------------------

def detect_filters(user_question):
    question = user_question.lower()
    filters = {}

    # Sector filters
    if "healthcare" in question or "health care" in question or "medical" in question:
        filters["Sector"] = "Healthcare"
    elif "retail" in question:
        filters["Sector"] = "Retail"
    elif "logistics" in question:
        filters["Sector"] = "Logistics"
    elif "automotive" in question or "automobile" in question or "auto" in question or "cars" in question:
        filters["Sector"] = "Automobiles & Components"
    elif "consumer" in question:
        filters["Sector"] = "Consumer Products"
    elif "software" in question:
        filters["Sector"] = "Software & Services"
    elif "pharma" in question or "life science" in question or "lifescience" in question:
        filters["Sector"] = "Pharma, Biotech and Lifescience"
    elif "utility" in question or "utilities" in question:
        filters["Sector"] = "Utilities"

    # Geography filters
    if "uk" in question or "united kingdom" in question:
        filters["Target Geography"] = "UK"
    elif "us" in question or "usa" in question or "united states" in question:
        filters["Target Geography"] = "US"
    elif "india" in question:
        filters["Target Geography"] = "India"
    elif "europe" in question:
        filters["Target Geography"] = "Europe"
    elif "apac" in question:
        filters["Target Geography"] = "APAC"

    # Deal type filters
    if "itdd" in question or "it dd" in question or "it diligence" in question:
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
    question = user_question.lower()

    if "% of revenue" in question or "percentage of revenue" in question or "as % of revenue" in question:
        return "IT Spend % Revenue"

    if "standalone" in question or "separation" in question:
        return "IT Standalone Cost (m)"

    if "revenue" in question and "it spend" not in question and "it cost" not in question and "tech" not in question:
        return "Revenue (m)"

    if "employee" in question or "per employee" in question:
        return "IT Spend per Employee"

    if "fte" in question or "it team" in question:
        return "IT Spend per IT FTE"

    if "applications" in question or "app count" in question:
        return "# Applications"

    return "IT Spend (m)"


def detect_intent(user_question):
    question = user_question.lower()

    if "breakdown" in question or "capex" in question or "opex" in question:
        return "cost_breakdown"

    if "application" in question or "vendor" in question or "saas" in question or "erp" in question:
        return "application_benchmark"

    if "trend" in question or "by year" in question or "over time" in question or "last 3 years" in question:
        return "trend"

    return "average_metric"


def detect_application_filters(user_question):
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
    elif "servicenow" in question or "service now" in question:
        filters["Vendor"] = "ServiceNow"

    if "front office" in question:
        filters["Application Type"] = "Front Office"
    elif "back office" in question or "erp" in question:
        filters["Application Type"] = "Back Office"
    elif "mid office" in question:
        filters["Application Type"] = "Mid Office"

    return filters


# ------------------------------------------------------------
# FORMATTING
# ------------------------------------------------------------

def format_metric_value(metric_name, value):
    if value is None or pd.isna(value):
        return "N/A"

    if "% Revenue" in metric_name:
        return f"{value * 100:.2f}%"

    if "per Employee" in metric_name or "per IT FTE" in metric_name:
        return f"{value:,.0f}"

    if "(m)" in metric_name or "Cost" in metric_name or "Spend" in metric_name:
        return f"{value:.2f}m"

    return f"{value:.2f}"


def show_governance_box(source_sheet, filters, logic, record_count):
    st.info(f"**Source sheet:** {source_sheet}")
    st.info(f"**Filters applied:** {filters if filters else 'No filters applied'}")
    st.info(f"**Calculation logic:** {logic}")

    if record_count < 5:
        st.warning("Small sample size; treat this result as directional.")


# ------------------------------------------------------------
# ANSWER FUNCTIONS
# ------------------------------------------------------------

def show_average_metric_answer(user_question):
    primary_kpis = prepare_primary_kpis()

    metric_name = detect_metric(user_question)
    filters = detect_filters(user_question)

    filtered_data = apply_filters(primary_kpis, filters)
    record_count = len(filtered_data)

    st.subheader("Benchmark Result")

    if record_count == 0:
        st.warning("No matching records found.")
        return

    average_value = filtered_data[metric_name].mean()
    median_value = filtered_data[metric_name].median()
    min_value = filtered_data[metric_name].min()
    max_value = filtered_data[metric_name].max()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(f"Average {metric_name}", format_metric_value(metric_name, average_value))
    col2.metric(f"Median {metric_name}", format_metric_value(metric_name, median_value))
    col3.metric("Matching Records", record_count)
    col4.metric("Answer Type", "Benchmark")

    st.write(
        f"Based on **{record_count} matching project(s)**, the average **{metric_name}** is "
        f"**{format_metric_value(metric_name, average_value)}**."
    )

    show_governance_box(
        source_sheet="Primary_KPIs",
        filters=filters,
        logic=f"Average / median / min / max of {metric_name} after applying filters.",
        record_count=record_count
    )

    st.subheader("Range")
    range_col1, range_col2 = st.columns(2)
    range_col1.metric(f"Minimum {metric_name}", format_metric_value(metric_name, min_value))
    range_col2.metric(f"Maximum {metric_name}", format_metric_value(metric_name, max_value))

    st.subheader("Supporting Table")

    display_columns = [
        "Year",
        "Project Name",
        "Deal Type",
        "Sector",
        "Target Geography",
        "Revenue (m)",
        "IT Spend (m)",
        "IT Standalone Cost (m)",
        metric_name
    ]

    display_columns = list(dict.fromkeys(display_columns))

    st.dataframe(filtered_data[display_columns], use_container_width=True)


def show_trend_answer(user_question):
    primary_kpis = prepare_primary_kpis()

    metric_name = detect_metric(user_question)
    filters = detect_filters(user_question)

    filtered_data = apply_filters(primary_kpis, filters)
    record_count = len(filtered_data)

    st.subheader("Trend Result")

    if record_count == 0:
        st.warning("No matching records found.")
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

    col1, col2, col3 = st.columns(3)
    col1.metric("Matching Records", record_count)
    col2.metric("Source Sheet", "Primary_KPIs")
    col3.metric("Chart Type", "Line chart")

    show_governance_box(
        source_sheet="Primary_KPIs",
        filters=filters,
        logic=f"Grouped records by Year and calculated average {metric_name}.",
        record_count=record_count
    )

    st.subheader("Year-wise Trend Table")
    st.dataframe(trend, use_container_width=True)

    st.subheader("Trend Chart")
    chart_data = trend.set_index("Year")[["Average_Value"]]
    st.line_chart(chart_data)

    st.write(
        f"Based on **{record_count} matching project(s)**, the chart shows year-wise average "
        f"**{metric_name}**."
    )


def show_cost_breakdown_answer(user_question):
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

    st.subheader("Cost Breakdown Result")

    if record_count == 0:
        st.warning("No matching records found.")
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

    col1, col2, col3 = st.columns(3)
    col1.metric("Matching Records", record_count)
    col2.metric("Source Sheet", "Cost_Breakdown")
    col3.metric("Answer Type", "Cost Breakdown")

    show_governance_box(
        source_sheet="Cost_Breakdown",
        filters=filters,
        logic="Average cost by category after applying filters.",
        record_count=record_count
    )

    st.subheader("Average Cost by Category")
    st.dataframe(summary, use_container_width=True)

    st.subheader("Cost Breakdown Chart")
    chart_data = summary.set_index("Cost Category")
    st.bar_chart(chart_data)

    st.subheader("Supporting Records")
    st.dataframe(filtered_data, use_container_width=True)


def show_application_benchmark_answer(user_question):
    data = load_excel_data()

    applications = data["applications"].copy()

    filters = detect_application_filters(user_question)
    filtered_data = apply_filters(applications, filters)
    record_count = len(filtered_data)

    st.subheader("Application Benchmark Result")

    if record_count == 0:
        st.warning("No matching application records found.")
        return

    filtered_data["Annual Cost per User"] = (
        filtered_data["Annual Cost"] / filtered_data["# Users"]
    )

    avg_annual_cost = filtered_data["Annual Cost"].mean()
    avg_cost_per_user = filtered_data["Annual Cost per User"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Annual Cost", f"{avg_annual_cost:.2f}m")
    col2.metric("Average Cost per User", f"{avg_cost_per_user:.4f}")
    col3.metric("Matching Records", record_count)
    col4.metric("Source Sheet", "Applications")

    show_governance_box(
        source_sheet="Applications",
        filters=filters,
        logic="Filtered application records and calculated annual cost per user.",
        record_count=record_count
    )

    st.warning("Application annual cost formula will be finalized once real data is available.")

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

    st.subheader("Application Benchmark Table")
    st.dataframe(filtered_data[display_columns], use_container_width=True)

    st.subheader("Annual Cost by Application")
    chart_data = filtered_data.set_index("Application Name")[["Annual Cost"]]
    st.bar_chart(chart_data)


def answer_question(user_question):
    intent = detect_intent(user_question)

    if intent == "trend":
        show_trend_answer(user_question)
    elif intent == "cost_breakdown":
        show_cost_breakdown_answer(user_question)
    elif intent == "application_benchmark":
        show_application_benchmark_answer(user_question)
    else:
        show_average_metric_answer(user_question)


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------

st.title("📊 IT Diligence Benchmark Agent")
st.caption("Local MVP demo using dummy Excel backend")

st.write(
    "This MVP lets consultants ask benchmark questions over structured IT diligence KPI data. "
    "The current version uses rule-based query understanding and deterministic Python calculations."
)

with st.sidebar:
    st.header("MVP Scope")
    st.write("Currently supported:")
    st.markdown(
        """
        - Average KPI lookup
        - Year-wise trend analysis
        - Cost breakdown
        - Application benchmark
        - Basic sector / geography / deal filters
        """
    )

    st.header("Governance")
    st.markdown(
        """
        Every answer shows:
        - Source sheet
        - Filters applied
        - Record count
        - Calculation logic
        - Small sample warning
        """
    )

    st.header("Note")
    st.warning(
        "This app uses dummy data. Values are directional and for MVP demonstration only."
    )

st.divider()

example_questions = [
    "Show average IT spend for healthcare projects",
    "Show average IT spend for retail projects in the UK",
    "For automotive sector, what is average IT cost as % of revenue?",
    "Show IT spend trend across years",
    "Show IT spend trend for healthcare projects",
    "Show cost breakdown for ITDD deals",
    "Show capex and opex breakdown for transformation projects",
    "Show application annual cost for Microsoft applications",
    "Show application annual cost for SaaS applications",
    "Show application annual cost for back office applications"
]

selected_example = st.selectbox(
    "Try an example question",
    example_questions
)

user_question = st.text_input(
    "Ask a benchmark question",
    value=selected_example
)

if st.button("Run Benchmark Query", type="primary"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        st.subheader("Question Asked")
        st.write(user_question)
        answer_question(user_question)