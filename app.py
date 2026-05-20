# app.py — Final dashboard
"""
CPI Australia — The Cost-of-Living Story
DVN Group 7 · 2026

Narrative arc: What → So What → What Next.
Advanced features: context-aware filtering, modal sparklines, what-if slider.
"""
import re
import pandas as pd
import streamlit as st

from components import data_loader as dl
from components import theme as T
from components import visuals as viz


# Page config
st.set_page_config(
    page_title="CPI Australia — Cost-of-Living Story",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for KPI tiles, narrative styling, narrative tags
st.markdown(f"""
<style>
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }}
section[data-testid="stSidebar"] {{ background-color: {T.LIGHT_GREY}; }}

.kpi {{
    background: white; border: 1px solid {T.PALE_GREY};
    border-radius: 6px; padding: 14px 18px;
}}
.kpi-label {{
    font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase;
    color: {T.MID_GREY}; margin-bottom: 4px;
}}
.kpi-value {{
    font-size: 1.9rem; font-weight: 700; color: {T.NAVY}; line-height: 1.1;
}}
.kpi-sub {{ font-size: 0.8rem; color: {T.MID_GREY}; margin-top: 2px; }}

.narrative-tag {{
    display: inline-block; font-size: 0.72rem; letter-spacing: 0.08em;
    text-transform: uppercase; color: white; background: {T.NAVY};
    padding: 3px 10px; border-radius: 3px; margin-bottom: 6px;
}}
.narrative-body {{
    font-size: 0.95rem; color: {T.CHARCOAL}; line-height: 1.5;
    margin-bottom: 12px;
}}
.source-attrib {{
    font-size: 0.72rem; font-style: italic; color: {T.COOL_GREY};
    margin-top: 24px; padding-top: 12px;
    border-top: 1px solid {T.PALE_GREY};
}}

h1 {{ color: {T.NAVY}; font-weight: 700; }}
</style>
""", unsafe_allow_html=True)


def kpi_tile(label, value, sub=""):
    return (f'<div class="kpi"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')


def _md_bold(text):
    """Convert **bold** and *italic* to HTML inside styled divs."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"<em>\1</em>", text)
    return text


# Load data (cached)
with st.spinner("Loading ABS data…"):
    cpi_monthly = dl.load_cpi_monthly()
    cpi_annual = dl.load_cpi_annual_pct()
    cpi_vs_wpi = dl.cpi_vs_wpi_joined()
    wpi_q = dl.load_wpi_quarterly()


# Compute latest snapshot
latest_date = cpi_monthly["date"].max()
wpi_yoy_latest = wpi_q["wpi_yoy"].dropna().iloc[-1]
fastest_snap = (cpi_annual[(cpi_annual["date"] == latest_date)
                            & (cpi_annual["city"].isin(dl.CITIES))
                            & (cpi_annual["group"].isin(dl.TOP_LEVEL_GROUPS))]
                .groupby("group")["annual_pct"].mean()
                .sort_values(ascending=False))


# ── Sidebar (Advanced Feature 1: context-aware filtering) ──
st.sidebar.markdown("### Filters")
st.sidebar.caption("Selections update every chart **and** the narrative paragraphs.")

selected_city = st.sidebar.selectbox(
    "Focus city", ["Australia"] + dl.CITIES, index=0,
)
selected_group = st.sidebar.selectbox(
    "Focus expenditure group", ["All Groups"] + dl.TOP_LEVEL_GROUPS, index=0,
)
date_min = cpi_monthly["date"].min().date()
date_max = cpi_monthly["date"].max().date()
date_range = st.sidebar.slider(
    "Time range (monthly views)",
    min_value=date_min, max_value=date_max,
    value=(date_min, date_max), format="MMM YYYY",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### What-if scenario")
wage_growth = st.sidebar.slider(
    "Assumed wage growth %",
    min_value=0.0, max_value=8.0,
    value=float(wpi_yoy_latest), step=0.1, format="%.1f%%",
)

st.sidebar.markdown("---")
st.sidebar.caption(f"**Data:** ABS CPI & WPI. Latest: {latest_date.strftime('%b %Y')}.")


# ── Header ──
st.markdown("# CPI Australia: The Cost-of-Living Story")
st.markdown(
    f"<p style='color:{T.MID_GREY}; margin-top:-12px;'>"
    "The pressure is not felt equally across cities, categories, or households."
    "</p>", unsafe_allow_html=True)


# ── KPI strip ──
def city_yoy(city):
    """YoY CPI for a city. For 'Australia', average across the 8 capitals."""
    if city == "Australia":
        cities = cpi_monthly[cpi_monthly["city"].isin(dl.CITIES)]
        latest = cities["date"].max()
        m12 = cities[cities["date"] == latest]["cpi_index"].mean()
        m0_date = latest - pd.DateOffset(years=1)
        m0 = cities[cities["date"] == m0_date]["cpi_index"].mean()
        return (m12 / m0 - 1) * 100 if pd.notna(m0) and m0 > 0 else None
    sub = cpi_monthly[cpi_monthly["city"] == city].sort_values("date")
    if len(sub) < 13:
        return None
    return (sub["cpi_index"].iloc[-1] / sub["cpi_index"].iloc[-13] - 1) * 100

focus_cpi = city_yoy(selected_city)
gap_pp = (wpi_yoy_latest - focus_cpi) if focus_cpi is not None else None

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_tile(f"CPI · {selected_city}",
        f"{focus_cpi:.1f}%" if focus_cpi else "—",
        f"Year to {latest_date.strftime('%b %Y')}"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_tile("Wage growth (WPI)",
        f"{wpi_yoy_latest:.1f}%", "National · latest quarter"),
        unsafe_allow_html=True)
with k3:
    if gap_pp is not None:
        color = T.DEEP_TEAL if gap_pp >= 0 else T.VERMILLION
        st.markdown(
            f'<div class="kpi"><div class="kpi-label">Wage − CPI gap</div>'
            f'<div class="kpi-value" style="color:{color}">{gap_pp:+.1f} pp</div>'
            f'<div class="kpi-sub">'
            f'{"Wages outpacing inflation" if gap_pp >= 0 else "Wages falling behind"}'
            f'</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(kpi_tile("Fastest-rising group",
        fastest_snap.index[0],
        f"+{fastest_snap.iloc[0]:.1f}% YoY"), unsafe_allow_html=True)


# ── Visual 1 ──
st.markdown("---")
st.markdown('<span class="narrative-tag">What</span>', unsafe_allow_html=True)
st.markdown("## Are wages keeping pace with inflation?")

fig1 = viz.v1_cpi_vs_wpi(cpi_vs_wpi, wage_param_pct=wage_growth)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

latest_joint = cpi_vs_wpi.dropna().tail(1).iloc[0]
joint_gap = latest_joint["wpi_yoy"] - latest_joint["cpi_yoy"]
narrative_v1 = (
    f"In **{latest_joint['date'].strftime('%b %Y')}**, quarterly CPI ran at "
    f"**{latest_joint['cpi_yoy']:.1f}%** while wages grew "
    f"**{latest_joint['wpi_yoy']:.1f}%** — a gap of **{joint_gap:+.1f} pp**. "
    + ("Wages are *technically* outpacing the national inflation rate."
       if joint_gap >= 0
       else "Wages are *not* keeping pace; real purchasing power is eroding.")
)
st.markdown(f'<div class="narrative-body">{_md_bold(narrative_v1)}</div>',
             unsafe_allow_html=True)


# ── Visual 2 ──
st.markdown("---")
st.markdown('<span class="narrative-tag">What → So What</span>',
             unsafe_allow_html=True)
st.markdown("## How does inflation pressure differ across capital cities?")

cpi_m_range = cpi_monthly[
    (cpi_monthly["date"] >= pd.Timestamp(date_range[0]))
    & (cpi_monthly["date"] <= pd.Timestamp(date_range[1]))
]
fig2 = viz.v2_city_comparison(
    cpi_m_range,
    highlight_city=selected_city if selected_city != "Australia" else None,
)
st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# Per-city YoY for narrative
latest_m = cpi_monthly["date"].max()
m12 = cpi_monthly[cpi_monthly["date"] == latest_m].set_index("city")["cpi_index"]
m0 = cpi_monthly[cpi_monthly["date"] == (latest_m - pd.DateOffset(years=1))]\
    .set_index("city")["cpi_index"]
city_yoy_latest = ((m12 / m0 - 1) * 100).drop(["Australia"], errors="ignore")\
                                         .sort_values(ascending=False)
narrative_v2 = (
    f"**{city_yoy_latest.index[0]}** is under the strongest pressure at "
    f"**{city_yoy_latest.iloc[0]:.1f}%**, while **{city_yoy_latest.index[-1]}** "
    f"sits at **{city_yoy_latest.iloc[-1]:.1f}%** — a "
    f"**{(city_yoy_latest.iloc[0] - city_yoy_latest.iloc[-1]):.1f} pp** spread."
)
st.markdown(f'<div class="narrative-body">{_md_bold(narrative_v2)}</div>',
             unsafe_allow_html=True)


# ── Visual 3 + drill-in modal (Advanced Feature 2) ──
st.markdown("---")
st.markdown('<span class="narrative-tag">So What</span>', unsafe_allow_html=True)
st.markdown("## Which household costs are rising the fastest?")

col_chart, col_drill = st.columns([3, 1])
with col_chart:
    fig3 = viz.v3_category_ranking(cpi_annual, selected_city=selected_city)
    st.plotly_chart(fig3, use_container_width=True,
                     config={"displayModeBar": False})

with col_drill:
    st.markdown("**Drill into a category**")
    st.caption("See the 12-month trend for any group.")
    drill_group = st.selectbox(
        "Group", dl.TOP_LEVEL_GROUPS,
        index=dl.TOP_LEVEL_GROUPS.index("Housing"),
        label_visibility="collapsed",
    )
    if st.button("📊 Show 12-month trend", use_container_width=True):
        st.session_state["show_modal"] = True
        st.session_state["modal_group"] = drill_group
        st.session_state["modal_city"] = selected_city

# Sparkline trend (works on any Streamlit version)
if st.session_state.get("show_modal"):
    with st.expander("📊 12-month trend", expanded=True):
        g = st.session_state.get("modal_group", "Housing")
        c = st.session_state.get("modal_city", "Australia")
        fig_sp = viz.sparkline(cpi_annual, group=g, city=c)
        st.plotly_chart(fig_sp, use_container_width=True,
                         config={"displayModeBar": False})
        if st.button("Close", key="close_spark"):
            st.session_state["show_modal"] = False
            st.rerun()

# V3 narrative
if selected_city == "Australia":
    rank_src = (cpi_annual[
        (cpi_annual["date"] == cpi_annual["date"].max())
        & (cpi_annual["city"].isin(dl.CITIES))
        & (cpi_annual["group"].isin(dl.TOP_LEVEL_GROUPS))]
        .groupby("group", as_index=False)["annual_pct"].mean())
else:
    rank_src = cpi_annual[
        (cpi_annual["date"] == cpi_annual["date"].max())
        & (cpi_annual["city"] == selected_city)
        & (cpi_annual["group"].isin(dl.TOP_LEVEL_GROUPS))
    ][["group", "annual_pct"]]
rank_src = rank_src.sort_values("annual_pct", ascending=False)
top3 = rank_src.head(3)
narrative_v3 = (
    f"For **{selected_city}**, the three fastest-rising categories are "
    + ", ".join([f"**{r.group}** ({r.annual_pct:+.1f}%)"
                 for r in top3.itertuples()]) + "."
)
st.markdown(f'<div class="narrative-body">{_md_bold(narrative_v3)}</div>',
             unsafe_allow_html=True)


# ── Visual 4 ──
st.markdown("---")
st.markdown('<span class="narrative-tag">What Next</span>',
             unsafe_allow_html=True)
st.markdown("## Where is affordability pressure most concentrated?")

fig4 = viz.v4_pressure_heatmap(cpi_annual)
st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

hot = cpi_annual[(cpi_annual["date"] == cpi_annual["date"].max())
                  & (cpi_annual["city"].isin(dl.CITIES))
                  & (cpi_annual["group"].isin(dl.TOP_LEVEL_GROUPS))]\
    .sort_values("annual_pct", ascending=False).head(1).iloc[0]
narrative_v4 = (
    f"The single hottest cell is **{hot['group']} in {hot['city']}** at "
    f"**{hot['annual_pct']:+.1f}%** YoY. Targeted policy responses "
    "look essential here, not national-average measures."
)
st.markdown(f'<div class="narrative-body">{_md_bold(narrative_v4)}</div>',
             unsafe_allow_html=True)


# ── What-if scenario (Advanced Feature 3) ──
st.markdown("---")
st.markdown('<span class="narrative-tag">Scenario · Advanced</span>',
             unsafe_allow_html=True)
st.markdown("## What if wages grew at a different rate?")
st.markdown(
    f"<p style='color:{T.MID_GREY}; margin-top:-8px;'>"
    f"Sidebar slider set to <b>{wage_growth:.1f}%</b>. Negative bars = wages "
    "still fall behind."
    "</p>", unsafe_allow_html=True)

fig5 = viz.whatif_real_wage_gap(cpi_annual, wage_growth_pct=wage_growth)
st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

sub_whatif = cpi_annual[
    (cpi_annual["date"] == cpi_annual["date"].max())
    & (cpi_annual["group"] == "All Groups CPI")
    & (cpi_annual["city"].isin(dl.CITIES))
].copy()
sub_whatif["gap"] = wage_growth - sub_whatif["annual_pct"]
losing = sub_whatif[sub_whatif["gap"] < 0]
winning = sub_whatif[sub_whatif["gap"] >= 0]
narrative_whatif = (
    f"At **{wage_growth:.1f}%** wage growth, **{len(winning)}** of 8 capitals "
    f"see real-wage gains and **{len(losing)}** fall behind."
)
st.markdown(f'<div class="narrative-body">{_md_bold(narrative_whatif)}</div>',
             unsafe_allow_html=True)


# ── Footer ──
st.markdown(
    f"<div class='source-attrib'>{T.SOURCE_ATTRIBUTION}<br>"
    "DVN Group 7 · UTS MDSI 36104 · 2026</div>",
    unsafe_allow_html=True)