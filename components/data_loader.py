# components/data_loader.py
"""ABS data loader — turns wide xlsx files into tidy DataFrames."""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CITIES = ["Sydney", "Melbourne", "Brisbane", "Adelaide",
          "Perth", "Hobart", "Darwin", "Canberra"]

GROUP_DISPLAY = {
    "All groups CPI":                                 "All Groups CPI",
    "Food and non-alcoholic beverages":               "Food & Beverages",
    "Alcohol and tobacco":                            "Alcohol & Tobacco",
    "Clothing and footwear":                          "Clothing & Footwear",
    "Housing":                                        "Housing",
    "Furnishings, household equipment and services": "Furnishings & Household",
    "Health":                                         "Health",
    "Transport":                                      "Transport",
    "Communication":                                  "Communication",
    "Recreation and culture":                         "Recreation & Culture",
    "Education":                                      "Education",
    "Insurance and financial services":               "Insurance & Finance",
}
TOP_LEVEL_GROUPS = [g for g in GROUP_DISPLAY.values() if g != "All Groups CPI"]


def _clean_abs_sheet(filepath, sheet="Data1"):
    """Read an ABS xlsx: row 0 = column names, rows 1-9 = metadata, row 10+ = data."""
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    col_names = raw.iloc[0].tolist()
    seen, deduped = {}, []
    for c in col_names:
        key = str(c)
        seen[key] = seen.get(key, 0) + 1
        deduped.append(c if seen[key] == 1 else f"{c}__dup{seen[key]}")
    deduped[0] = "date"
    df = raw.iloc[10:].copy()
    df.columns = deduped
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).set_index("date")
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _parse_series_string(s):
    """Split 'Index Numbers ; Housing ; Sydney ;' into 3 parts."""
    s = str(s)
    if "__dup" in s:
        s = s.split("__dup")[0]
    parts = [p.strip() for p in s.split(";") if p.strip()]
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], parts[1], ""
    return s, "", ""


def _wide_to_tidy(wide, value_name):
    """Convert wide ABS DataFrame to long format."""
    rows = []
    for col in wide.columns:
        measure, item, geo = _parse_series_string(col)
        sub = wide[col].dropna().reset_index()
        sub.columns = ["date", value_name]
        sub["measure"] = measure
        sub["item"] = item
        sub["geography"] = geo
        rows.append(sub)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_cpi_monthly():
    """CPI by city × group, monthly. Returns all-groups only (filter by group later)."""
    wide = _clean_abs_sheet(DATA_DIR / "CPI_CapitalCities_09.xlsx")
    tidy = _wide_to_tidy(wide, "value")
    tidy = tidy[tidy["measure"].str.contains("Index Numbers", na=False)].copy()
    # Filter to All groups CPI only (we need city-level overall CPI for V2)
    tidy = tidy[tidy["item"].str.strip() == "All groups CPI"].copy()
    tidy = tidy[tidy["geography"].isin(CITIES)].copy()
    tidy = tidy.rename(columns={"value": "cpi_index", "geography": "city"})
    return tidy[["date", "city", "cpi_index"]]


@st.cache_data(show_spinner=False)
def load_cpi_quarterly():
    """Quarterly CPI by city, long history (1948 →)."""
    wide = _clean_abs_sheet(DATA_DIR / "CPI_Quarterly_01.xlsx")
    tidy = _wide_to_tidy(wide, "value")
    tidy = tidy[tidy["measure"].str.contains("Index Numbers", na=False)].copy()
    tidy["geography"] = tidy["geography"].replace({"": "Australia"})
    tidy = tidy.rename(columns={"value": "cpi_index", "geography": "city"})
    tidy = tidy.sort_values(["city", "date"])
    tidy["cpi_yoy"] = tidy.groupby("city")["cpi_index"].pct_change(4) * 100
    return tidy[["date", "city", "cpi_index", "cpi_yoy"]]


@st.cache_data(show_spinner=False)
def load_cpi_annual_pct():
    """Annual % change by group × city."""
    parts = []
    for sheet in ["Data1", "Data2", "Data3", "Data4", "Data5"]:
        try:
            wide = _clean_abs_sheet(DATA_DIR / "CPI_CapitalCities_11.xlsx", sheet=sheet)
            parts.append(_wide_to_tidy(wide, "value"))
        except Exception:
            continue
    tidy = pd.concat(parts, ignore_index=True)
    tidy = tidy[tidy["measure"].str.contains("Percentage Change", na=False)].copy()
    tidy = tidy[tidy["geography"].isin(CITIES + ["Australia"])].copy()
    tidy["group"] = tidy["item"].map(GROUP_DISPLAY)
    tidy = tidy.dropna(subset=["group", "value"])
    tidy = tidy.rename(columns={"value": "annual_pct", "geography": "city"})
    tidy = (tidy.groupby(["date", "city", "group"], as_index=False)["annual_pct"]
                .mean())
    return tidy[["date", "city", "group", "annual_pct"]]


@st.cache_data(show_spinner=False)
def load_wpi_quarterly():
    """WPI Table 1 — quarterly wage index, national."""
    wide = _clean_abs_sheet(DATA_DIR / "WPI_Table1.xlsx")
    tidy = _wide_to_tidy(wide, "value")
    mask = (
        tidy["measure"].str.contains("Quarterly Index", na=False)
        & tidy["item"].str.contains("Total hourly rates", na=False)
    )
    tidy = tidy[mask].copy()
    tidy = tidy.rename(columns={"value": "wpi_index"})
    tidy = tidy[tidy["geography"] == "Australia"].copy()
    tidy = tidy.sort_values("date").drop_duplicates(subset=["date"])
    tidy["wpi_yoy"] = tidy["wpi_index"].pct_change(4) * 100
    return tidy[["date", "wpi_index", "wpi_yoy"]]


@st.cache_data(show_spinner=False)
def cpi_vs_wpi_joined():
    """Join CPI quarterly (national) with WPI quarterly."""
    cpi = load_cpi_quarterly()
    cpi_au = cpi[cpi["city"] == "Australia"][["date", "cpi_yoy"]]
    wpi = load_wpi_quarterly()[["date", "wpi_yoy"]]
    df = pd.merge(cpi_au, wpi, on="date", how="inner")
    return df.dropna().sort_values("date")