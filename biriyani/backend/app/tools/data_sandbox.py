from __future__ import annotations
import io
import math
import re
import statistics
from typing import Any
import pandas as pd
import numpy as np


class DataSandboxError(Exception):
    pass


def parse_csv_or_table(content: str) -> pd.DataFrame | None:
    """Attempt to parse tabular input from plain text, CSV, or Markdown tables."""
    trimmed = content.strip()
    if not trimmed:
        return None

    try:
        # Try standard CSV format first
        df = pd.read_csv(io.StringIO(trimmed))
        if len(df) > 0 and len(df.columns) > 1:
            return df
    except Exception:
        pass

    try:
        # Try markdown table format (| col1 | col2 |)
        lines = [line.strip() for line in trimmed.splitlines() if line.strip().startswith("|")]
        if len(lines) >= 2:
            clean_lines = [re.sub(r"^\||\|$", "", l) for l in lines]
            header = [c.strip() for c in clean_lines[0].split("|")]
            # Filter out separator line |---|---|
            data_rows = []
            for line in clean_lines[1:]:
                if re.match(r"^[:\s\-|\+]+$", line):
                    continue
                cells = [c.strip() for c in line.split("|")]
                if len(cells) == len(header):
                    data_rows.append(cells)
            if data_rows:
                return pd.DataFrame(data_rows, columns=header)
    except Exception:
        pass

    return None


def calculate_data_metrics(text_or_data: str) -> dict[str, Any]:
    """
    Safely inspect tabular data or numerical expressions and return structured metrics:
    - Summary stats (mean, median, sum, min, max, count, top items)
    - Calculated trend highlights
    """
    results: dict[str, Any] = {
        "status": "success",
        "has_dataframe": False,
        "metrics": {},
        "summary": "",
    }

    # 1. Check if input contains structured tabular data
    df = parse_csv_or_table(text_or_data)
    if df is not None and not df.empty:
        results["has_dataframe"] = True
        cols = list(df.columns)
        num_rows = len(df)
        results["metrics"]["num_rows"] = num_rows
        results["metrics"]["columns"] = cols

        # Try to convert numeric columns
        numeric_summary = {}
        for col in cols:
            # Convert numeric types
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0:
                valid_num = converted.dropna()
                numeric_summary[col] = {
                    "count": int(valid_num.count()),
                    "sum": float(valid_num.sum()),
                    "mean": float(round(valid_num.mean(), 4)),
                    "min": float(valid_num.min()),
                    "max": float(valid_num.max()),
                    "median": float(round(valid_num.median(), 4)),
                }

        results["metrics"]["numeric_analysis"] = numeric_summary

        # Highlight top 5 rows if available
        results["metrics"]["sample_head"] = df.head(5).to_dict(orient="records")
        results["summary"] = (
            f"Analyzed dataset with {num_rows} rows and {len(cols)} columns ({', '.join(cols)}). "
            f"Found {len(numeric_summary)} numeric field(s)."
        )
        return results

    # 2. Extract standalone numbers from text prompt if no explicit CSV table found
    numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text_or_data)]
    if numbers:
        results["metrics"] = {
            "count": len(numbers),
            "sum": float(sum(numbers)),
            "mean": float(round(statistics.mean(numbers), 4)),
            "min": float(min(numbers)),
            "max": float(max(numbers)),
            "median": float(round(statistics.median(numbers), 4)),
        }
        results["summary"] = (
            f"Extracted {len(numbers)} numerical values. "
            f"Sum: {results['metrics']['sum']}, Mean: {results['metrics']['mean']}, "
            f"Min: {results['metrics']['min']}, Max: {results['metrics']['max']}."
        )
    else:
        results["summary"] = "Data Agent performed inspection; no numerical table or values detected."

    return results
