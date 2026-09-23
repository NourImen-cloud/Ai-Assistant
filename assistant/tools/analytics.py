"""Data analysis and chart generation tools for CSV and Excel files."""

from datetime import datetime
from pathlib import Path
from typing import Any

from assistant.config import PROJECT_ROOT
from assistant.tools.paths import ensure_within_home, resolve_path

CHARTS_DIR = PROJECT_ROOT / "data" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_dataframe(file_path: str):
    import pandas as pd

    path = ensure_within_home(resolve_path(file_path))
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path), path
    elif suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path), path
    elif suffix == ".json":
        return pd.read_json(path), path
    else:
        raise ValueError(f"Unsupported format '{suffix}'. Supported: .csv, .xlsx, .json")


def analyze_tabular_data(file_path: str, query: str = "") -> dict[str, Any]:
    """Analyze a CSV or Excel dataset, returning summary statistics, columns, and data shape."""
    try:
        df, path = _load_dataframe(file_path)

        rows, cols = df.shape
        col_list = list(df.columns)
        null_counts = df.isnull().sum().to_dict()

        # Generate descriptive statistics for numeric columns
        describe_dict = {}
        if not df.select_dtypes(include="number").empty:
            describe_dict = df.describe().round(2).to_dict()

        # Preview head
        preview_csv = df.head(5).to_csv(index=False)

        summary_msg = (
            f"Dataset Analysis for '{path.name}':\n"
            f"- Dimensions: {rows} rows x {cols} columns\n"
            f"- Columns: {', '.join(col_list)}\n"
            f"- Missing values: {sum(null_counts.values())} total\n\n"
            f"Sample Data (First 5 Rows):\n{preview_csv}\n"
        )

        if describe_dict:
            summary_msg += f"\nSummary Statistics (Numeric):\n{df.describe().round(2).to_string()}"

        return {
            "status": "success",
            "message": summary_msg,
            "rows": rows,
            "columns": col_list,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Data analysis failed: {exc}"}


def generate_chart(
    file_path: str,
    chart_type: str = "bar",
    x_col: str = "",
    y_col: str = "",
    title: str = "",
) -> dict[str, Any]:
    """Generate and save a chart (bar, line, scatter, pie, hist) from a CSV or Excel file."""
    try:
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive background backend
        import matplotlib.pyplot as plt

        df, path = _load_dataframe(file_path)

        if x_col and x_col not in df.columns:
            return {"status": "error", "message": f"Column '{x_col}' not found. Available: {list(df.columns)}"}
        if y_col and y_col not in df.columns:
            return {"status": "error", "message": f"Column '{y_col}' not found. Available: {list(df.columns)}"}

        plt.figure(figsize=(10, 6))
        plt.style.use("ggplot")

        chart_type = chart_type.lower()
        if chart_type == "bar":
            if not x_col or not y_col:
                return {"status": "error", "message": "Bar chart requires both x_col and y_col."}
            plt.bar(df[x_col].astype(str), df[y_col], color="#9333ea")
            plt.xticks(rotation=45, ha="right")
        elif chart_type == "line":
            if not x_col or not y_col:
                return {"status": "error", "message": "Line chart requires both x_col and y_col."}
            plt.plot(df[x_col].astype(str), df[y_col], marker="o", color="#ec4899", linewidth=2.5)
            plt.xticks(rotation=45, ha="right")
        elif chart_type == "scatter":
            if not x_col or not y_col:
                return {"status": "error", "message": "Scatter chart requires both x_col and y_col."}
            plt.scatter(df[x_col], df[y_col], color="#00f2fe", alpha=0.7)
        elif chart_type == "hist":
            target = y_col or x_col
            if not target:
                return {"status": "error", "message": "Histogram requires a numeric column in x_col or y_col."}
            plt.hist(df[target].dropna(), bins=15, color="#8b5cf6", edgecolor="white")
        elif chart_type == "pie":
            if not x_col or not y_col:
                return {"status": "error", "message": "Pie chart requires category in x_col and values in y_col."}
            plt.pie(df[y_col], labels=df[x_col], autopct="%1.1f%%", colors=["#9333ea", "#ec4899", "#3b82f6", "#10b981", "#f59e0b"])
        else:
            return {"status": "error", "message": f"Unsupported chart_type '{chart_type}'. Choose: bar, line, scatter, hist, pie."}

        chart_title = title or f"{chart_type.title()} Chart: {y_col or ''} vs {x_col or ''}"
        plt.title(chart_title, fontsize=14, fontweight="bold", pad=15)
        if x_col and chart_type != "pie":
            plt.xlabel(x_col)
        if y_col and chart_type != "pie":
            plt.ylabel(y_col)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_filename = f"chart_{chart_type}_{timestamp}.png"
        out_path = CHARTS_DIR / out_filename
        plt.savefig(str(out_path), dpi=150)
        plt.close()

        return {
            "status": "success",
            "message": f"Chart successfully generated and saved to: {out_path}",
            "file_path": str(out_path),
            "chart_type": chart_type,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to generate chart: {exc}"}
