# CPI Australia

An interactive Streamlit dashboard analysing Australian cost-of-living pressure using ABS Consumer Price Index (CPI) and Wage Price Index (WPI) data. It provides insights into national inflation trends, regional differences across the 8 capital cities, expenditure category breakdowns, and the affordability gap between rising prices and wage growth. The analysis helps policymakers and economic advisors identify where targeted attention is needed through data-driven storytelling.

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#-problem-statement)
- [Dataset](#-dataset)
- [Key Metrics](#-key-metrics)
- [Visual Insights](#-visual-insights)
- [Tools and Technologies](#%EF%B8%8F-tools-and-technologies)
- [Data Cleaning and Analysis](#-data-cleaning-and-analysis)
- [Dashboard](#-dashboard)
- [Visual Highlights](#-visual-highlights)
- [Advanced Features](#-advanced-features)
- [Next Steps / Recommendations](#-next-steps--recommendations)
- [Installation](#%EF%B8%8F-installation)
- [Conclusion](#conclusion)
- [Contact](#contact)

## Project Overview

An interactive Streamlit dashboard analysing Australian cost-of-living pressure using official ABS data. It explores how inflation differs across the 8 Australian capital cities and 11 household expenditure categories, and whether wage growth is keeping pace. The analysis helps surface where affordability pressure is most concentrated and where national averages may hide important regional differences.

By leveraging Streamlit, Plotly, Pandas, and Python, the project delivers an interactive data narrative structured around the **What → So What → What Next** arc to support evidence-based policy decisions for cost-of-living advisors, RBA analysts, and treasury teams.

## 🚩 Problem Statement

National headline inflation figures mask significant regional and category-level differences in cost-of-living pressure. Policymakers and economic advisors lack a single interactive view of:

- 📊 The national relationship between CPI inflation and WPI wage growth over time
- 🏙️ How inflation pressure differs across the 8 capital cities
- 🏠 Which household expenditure categories are driving affordability pressure
- 🗺️ City × category combinations under the most severe pressure
- 📉 The real wage gap — whether wages are keeping pace with prices
- 🎯 Where targeted interventions are needed versus national-average measures
- 🔮 How alternative wage growth scenarios would affect each city

## 📂 Dataset

- Source: [ABS — Consumer Price Index (Cat. 6401.0)](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia) and [ABS — Wage Price Index (Cat. 6345.0)](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia)
- Description: Official Australian Bureau of Statistics time-series workbooks containing monthly and quarterly CPI by capital city × expenditure group, and quarterly WPI by sector and state. Data spans 1948–2026.
- Latest data point: **February 2026** (September 2025 quarterly release)

The objective was to combine these two complementary datasets to reveal the affordability gap between price rises and wage growth across cities, categories, and time.

## 📊 Key Metrics

- Headline CPI (national, year to Mar 2026): **4.6%**
- Wage Growth (WPI, Dec 2025, combined sectors): **3.4%**
- Real Wage Gap (Dec 2025): **−0.2 pp** (wages just fell behind inflation)
- Fastest-Rising Category: **Transport (+9.1% YoY)** — driven by automotive fuel (+24.1%)
- Second-Fastest: **Clothing & Footwear (+6.8% YoY)**
- Highest Sub-Item: **Electricity (+24.3% YoY)** within Housing
- Highest-Pressure City: **Hobart (+5.1% YoY)**
- Lowest-Pressure City: **Canberra (+4.2% YoY)** — a spread of nearly 1 pp the national headline hides
- Cities Analysed: 8 capital cities
- Expenditure Groups: 11 top-level categories

## 🔍 Visual Insights

- 📈 **National Tension:** CPI hit 4.6% in March 2026 — the highest point in the dataset and well above the RBA's 2–3% target band. WPI is running at 3.4%, meaning wages have just slipped behind inflation after 7 consecutive quarters of real wage gains.
- 🚗 **Transport Is the Top Story:** Transport leads every other category at +9.1% YoY, driven almost entirely by automotive fuel (+24.1%).
- 🏠 **Housing Pressure From Electricity:** Within Housing, electricity prices are up 24.3% — the single largest annual movement in the data.
- 🧥 **Clothing Surprises:** Clothing & Footwear sits unusually high at +6.8%, with accessories up 17.8% YoY.
- 🏙️ **City Spread:** Hobart (+5.1%) leads city inflation; Canberra and Darwin (+4.2%) sit lowest. The 0.9 pp spread is invisible in the national headline.
- 📊 **Headline vs Trimmed Mean:** Headline CPI is now above the RBA's preferred Trimmed Mean measure (3.8% vs 3.3% in Feb 2026), suggesting recent inflation is driven by volatile components rather than broad-based price growth.
- 🏥 **Industry Winners:** Health Care, Electricity/Gas/Water, and Public Administration are the only industries where wages are clearly beating inflation (+0.5 to +0.8 pp).
- 🗺️ **State Spread:** Western Australia is the only state where wages are clearly ahead of inflation (+0.5 pp gap). Victoria, Queensland, and Tasmania all lag.

## 🛠️ Tools and Technologies

- Programming: Python 🐍
- Streamlit: For building the interactive web dashboard.
- Plotly: For creating interactive charts (line, bar, heatmap, sparkline).
- Pandas: For data wrangling and time-series transformations.
- openpyxl: For reading the ABS Excel time-series workbooks.
- NumPy: For numerical operations and YoY change computation.
- Libraries: Pandas, NumPy, Plotly, openpyxl
- Hosting: Streamlit Community Cloud
- Version Control: Git & GitHub
- Environment: VS Code + Jupyter Notebook (for EDA)

## 🧹 Data Cleaning and Analysis

Data cleaning was performed in Python using Pandas to handle the ABS time-series workbook format, where metadata occupies the first 10 rows and data begins from row 11. All cleaning steps are wrapped in `@st.cache_data` so the spreadsheets are parsed only once per session.

Python (Pandas)

- **Handling ABS File Layout:** The ABS time-series workbooks use a fixed format — row 0 contains the series description (e.g., `Index Numbers ; All groups CPI ; Sydney ;`), rows 1–9 contain metadata (Unit, Series Type, Series ID, etc.), and row 10 onwards contains the actual date-indexed values. Built a `_clean_abs_sheet()` helper to handle this uniformly.
- **De-duplicating Column Names:** ABS occasionally repeats identical series names across sub-groups. Implemented a `__dup` suffix system that the parser strips back when extracting metadata.
- **Reshaping Wide to Tidy:** Original ABS data is wide (one column per series). Reshaped into tidy long format with one row per `(date, series, value)` so the data is usable by Plotly.
- **Parsing Series Descriptions:** Each column header is split on `;` into (measure, item, geography) tuples — for example, `"Index Numbers ; Housing ; Sydney ;"` becomes `("Index Numbers", "Housing", "Sydney")`.
- **Mapping ABS Group Strings to Display Labels:** Long ABS strings like `"Furnishings, household equipment and services"` are mapped to friendlier display names like `"Furnishings & Household"` via a `GROUP_DISPLAY` dictionary.
- **Coercing Numeric Types:** All value columns are coerced with `pd.to_numeric(errors="coerce")` to handle any non-numeric placeholders.
- **Handling Missing Values:** Rows with non-parseable dates or NaN values in critical fields are dropped at load time.
- **Computing Year-on-Year Change:** YoY % change is computed using `pct_change(4)` on quarterly data (4 quarters = 1 year) and `pct_change(12)` on monthly data.
- **Collapsing Duplicates from Multi-Sheet Workbooks:** Table 11 has 5 data sheets — duplicates across sheets are collapsed with `groupby().mean()`.

Streamlit & Plotly

- **Caching Strategy:** Used `@st.cache_data` decorators on every loader so 8 Excel files are parsed once per session, then served instantly on every interaction.
- **Data Modelling:** Joined CPI (quarterly, national) with WPI (quarterly, national) on the date column to enable the central CPI vs WPI comparison visual.
- **Theming:** Centralised colour palette, typography, and Plotly layout defaults in `components/theme.py` so every chart renders consistently against the design system.
- **Interactive Filtering:** Sidebar selectors and the what-if slider drive every chart via Streamlit's reactive re-run loop — no callbacks or event handlers needed.
- **Narrative Generation:** Auto-generated prose paragraphs beneath each chart recompute on every filter change using f-strings against the filtered data.

## 📈 Dashboard

![Dashboard] <img width="1440" height="772" alt="Screenshot 2026-05-20 at 9 17 52 pm" src="https://github.com/user-attachments/assets/d127f786-8777-4494-bccf-b88d2d82044f" />


The live dashboard is hosted at:
**[https://cpi-australia-group7.streamlit.app](https://cpi-australia-group7.streamlit.app)**

## 📊 Visual Highlights

Selected visualisations from the dashboard:

1. 📈 **Visual 1 — Are wages keeping pace with inflation?**

   A dual-line chart showing quarterly CPI vs WPI year-on-year change, with the RBA 2–3% target band shaded and an optional what-if wage growth reference line driven by the sidebar slider. Narrative role: **What**.

2. 🏙️ **Visual 2 — How does inflation pressure differ across Australian capital cities?**

   A multi-line chart of monthly YoY CPI change for the 8 capitals. Selecting a focus city in the sidebar dims the others to draw attention to the chosen city. Narrative role: **What → So What**.

3. 🏠 **Visual 3 — Which household costs are rising the fastest?**

   A horizontal bar chart ranking the 11 expenditure categories by annual % change, with Housing rendered in vermillion to reinforce the narrative emphasis. Includes a drill-in panel that opens a 12-month sparkline for any selected category. Narrative role: **So What**.

4. 🔥 **Visual 4 — Where is affordability pressure most concentrated?**

   A diverging-colour heatmap of city × category annual % change, with cells sorted by severity so the hottest spots sit top-left. Anchored at the RBA midpoint (2.5%) so colour is semantically meaningful. Narrative role: **What Next**.

5. 🔮 **What-If Scenario — Real wage gap per city**

   A bar chart showing the per-city gap between the user-set wage growth assumption and current CPI inflation. Cities with positive bars (teal) would see real wage gains; cities with negative bars (vermillion) would still fall behind. Narrative role: **Scenario / Advanced**.

## 🎯 Advanced Features

This project implements **three advanced features** as required by the assignment brief:

1. **Context-Aware Filtering:** Sidebar selectors (Focus city, Focus expenditure group, Time range) and the what-if slider update every chart on the dashboard as well as five auto-generated narrative paragraphs that recompute on every interaction.

2. **Visual Drill-In Panel:** On Visual 3, users can select any expenditure group and click **Show 12-month trend** to reveal an inline sparkline panel with a mini stats row (latest value, 12-month average, vs RBA midpoint).

3. **What-If Parameterisation:** The sidebar **Assumed wage growth %** slider (0.0–8.0%) drives both a dashed reference line overlaid on Visual 1 and a standalone bar chart showing per-city real-wage gaps under the scenario.

## 🎯 Next Steps / Recommendations

Based on the analysis, the following insights and policy recommendations were derived:

- **Target Energy Pressure:** Electricity alone is up 24.3% — the single largest contributor to Housing inflation. Energy-bill relief programs would have the largest direct impact on the headline number.
- **Fuel-Cost Mitigation:** Transport's +9.1% rise is almost entirely automotive fuel. Public transport subsidies or fuel excise adjustments could meaningfully ease pressure for commuter households.
- **City-Targeted Responses:** Hobart, Adelaide, and Brisbane consistently sit above the national average. National-average policies will under-serve these cities.
- **State-Level Wage Disparity:** Wages are beating inflation only in Western Australia. The other 7 jurisdictions need attention through industry wage policy or targeted cost-of-living transfers.
- **Industry-Level Response:** Public Administration, Health Care, and Utilities workers are protected; the construction, retail, and hospitality workforces are losing real income and warrant focused intervention.
- **Watch Trimmed Mean vs Headline:** The widening gap between headline (3.8%) and trimmed mean (3.3%) suggests current inflation is volatile-component-driven — RBA policy responses should reflect this distinction.

## ⚙️ Installation

To get started with the project, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Dhrishita/CPI Australia.git
   cd CPI Australia
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # On Windows: .venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL displayed in your terminal (usually `http://localhost:8501`) in any modern browser.

## Conclusion

The CPI-Australia dashboard provides actionable insights into the affordability landscape facing Australian households. By combining ABS CPI and WPI data into a single interactive narrative, the project surfaces the gap between national headlines and lived household experience — Transport's surge driven by fuel, Housing pressure from electricity, geographic disparities between Hobart and Canberra, and the real wage gap that has just turned negative. These insights enable policymakers to design city-specific, category-specific, and industry-specific interventions rather than relying solely on national-average measures.

## Contact

If you have any questions or suggestions, feel free to open an issue or contact:
Dhrishita Parve: <dhrishitap18@gmail.com>
