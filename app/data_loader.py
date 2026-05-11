import pandas as pd
from pathlib import Path


EXCEL_PATH = Path(__file__).resolve().parents[1] / "data" / "IT_KPI_PowerBI_Template_v5_dummy_refined.xlsx"


def load_excel_data():
    """
    Loads all important sheets from the Excel workbook.
    Returns a dictionary of pandas DataFrames.
    """

    sheets = {
        "primary_kpis": "Primary_KPIs",
        "cost_breakdown": "Cost_Breakdown",
        "it_org_breakdown": "IT_Org_Breakdown",
        "applications": "Applications",
        "benchmark_reference": "Benchmark_Reference",
    }

    data = {}

    for key, sheet_name in sheets.items():
        data[key] = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)

    return data


def preview_data():
    """
    Quick check to confirm that Excel is loading correctly.
    """

    data = load_excel_data()

    for name, df in data.items():
        print("\n" + "=" * 80)
        print(f"Sheet loaded: {name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(df.head())


if __name__ == "__main__":
    preview_data()