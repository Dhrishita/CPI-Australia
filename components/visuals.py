# components/visuals.py
"""Plotly chart builders for V1-V4."""
import pandas as pd
import plotly.graph_objects as go

from components import theme as T
from components import data_loader as dl

def v1_cpi_vs_wpi(df, wage_param_pct=None):
    """Dual-line: CPI YoY vs WPI YoY. Optional what-if wage line."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["cpi_yoy"], mode="lines+markers",
        name="CPI (inflation)",
        line=dict(color=T.CPI_COLOR, width=2.8),
        marker=dict(size=6),
        hovertemplate="<b>%{x|%b %Y}</b><br>CPI: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["wpi_yoy"], mode="lines+markers",
        name="WPI (wages)",
        line=dict(color=T.WPI_COLOR, width=2.8),
        marker=dict(size=6),
        hovertemplate="<b>%{x|%b %Y}</b><br>WPI: %{y:.1f}%<extra></extra>",
    ))

    # RBA target band
    fig.add_hrect(
        y0=T.RBA_TARGET_LOW, y1=T.RBA_TARGET_HIGH,
        fillcolor=T.DEEP_TEAL, opacity=0.08, line_width=0,
        annotation_text="RBA target 2–3%", annotation_position="top left",
        annotation_font=dict(size=10, color=T.MID_GREY),
    )

    # Optional what-if line
    if wage_param_pct is not None:
        fig.add_hline(
            y=wage_param_pct,
            line=dict(color=T.DEEP_TEAL, width=2, dash="dash"),
            annotation_text=f"Hypothetical wage growth: {wage_param_pct:.1f}%",
            annotation_position="top right",
            annotation_font=dict(size=10, color=T.DEEP_TEAL),
        )

    layout = dict(T.PLOTLY_LAYOUT)
    layout["yaxis"] = dict(layout["yaxis"], title="Annual % change",
                            ticksuffix="%", zeroline=True,
                            zerolinecolor=T.COOL_GREY, zerolinewidth=1)
    layout["xaxis"] = dict(layout["xaxis"], title=None)
    layout["height"] = 380
    layout["hovermode"] = "x unified"
    fig.update_layout(**layout)
    return fig



def v2_city_comparison(df_monthly, highlight_city=None):
    """Multi-line YoY by city. Highlight one city if specified."""
    d = df_monthly[df_monthly["city"] != "Australia"].copy()
    d = d.sort_values(["city", "date"])
    d["yoy"] = d.groupby("city")["cpi_index"].pct_change(12) * 100
    d = d.dropna(subset=["yoy"])

    fig = go.Figure()
    for city in T.CITY_COLORS.keys():
        sub = d[d["city"] == city]
        if sub.empty:
            continue
        is_focus = (highlight_city is None) or (city == highlight_city)
        fig.add_trace(go.Scatter(
            x=sub["date"], y=sub["yoy"], mode="lines",
            name=city,
            line=dict(color=T.CITY_COLORS[city],
                      width=3 if is_focus else 1.4),
            opacity=1.0 if is_focus else 0.25,
            hovertemplate=f"<b>{city}</b><br>%{{x|%b %Y}}<br>"
                          "Annual change: %{y:.1f}%<extra></extra>",
        ))

    fig.add_hline(y=T.RBA_MIDPOINT,
                  line=dict(color=T.DEEP_TEAL, width=1, dash="dash"),
                  annotation_text="RBA mid 2.5%",
                  annotation_position="bottom right",
                  annotation_font=dict(size=10, color=T.DEEP_TEAL))

    layout = dict(T.PLOTLY_LAYOUT)
    layout["yaxis"] = dict(layout["yaxis"], title="Annual % change",
                            ticksuffix="%")
    layout["xaxis"] = dict(layout["xaxis"], title=None)
    layout["height"] = 380
    layout["hovermode"] = "closest"
    fig.update_layout(**layout)
    return fig


def v3_category_ranking(df, selected_city="Australia"):
    """Horizontal bar of annual % change by group. Housing highlighted."""
    latest_date = df["date"].max()
    if selected_city == "Australia":
        snap = (df[(df["date"] == latest_date)
                   & (df["city"].isin(dl.CITIES))
                   & (df["group"].isin(dl.TOP_LEVEL_GROUPS))]
                .groupby("group", as_index=False)["annual_pct"].mean())
    else:
        snap = df[(df["date"] == latest_date)
                  & (df["city"] == selected_city)
                  & (df["group"].isin(dl.TOP_LEVEL_GROUPS))].copy()

    snap = snap.sort_values("annual_pct", ascending=True)
    colors = [T.VERMILLION if g == "Housing" else T.COOL_GREY
              for g in snap["group"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=snap["annual_pct"], y=snap["group"], orientation="h",
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in snap["annual_pct"]],
        textposition="outside",
        textfont=dict(size=11, color=T.CHARCOAL),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>",
    ))

    fig.add_vline(x=T.RBA_MIDPOINT,
                  line=dict(color=T.DEEP_TEAL, width=1, dash="dash"))

    layout = dict(T.PLOTLY_LAYOUT)
    layout["xaxis"] = dict(layout["xaxis"], title="Annual % change",
                            ticksuffix="%", showgrid=True,
                            gridcolor="#E5E7EB")
    layout["yaxis"] = dict(layout["yaxis"], title=None, showgrid=False)
    layout["height"] = 420
    layout["showlegend"] = False
    layout["margin"] = dict(l=160, r=60, t=40, b=40)
    fig.update_layout(**layout)
    return fig


def v4_pressure_heatmap(df):
    """City × group heatmap of latest annual % change."""
    latest_date = df["date"].max()
    snap = df[(df["date"] == latest_date)
              & (df["city"].isin(dl.CITIES))
              & (df["group"].isin(dl.TOP_LEVEL_GROUPS))].copy()

    pivot = snap.pivot_table(
        index="city", columns="group", values="annual_pct", aggfunc="mean",
    )
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]
    pivot = pivot[pivot.mean(axis=0).sort_values(ascending=False).index]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=T.HEATMAP_DIVERGING,
        zmid=T.RBA_MIDPOINT, zmin=-2, zmax=10,
        text=[[f"{v:+.1f}" if pd.notna(v) else "" for v in row]
              for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=11, color=T.CHARCOAL),
        hovertemplate="<b>%{y}</b> · <b>%{x}</b><br>"
                      "Annual change: %{z:.1f}%<extra></extra>",
        colorbar=dict(title="% YoY", thickness=12,
                      tickfont=dict(size=10, color=T.MID_GREY),
                      ticksuffix="%"),
        xgap=2, ygap=2,
    ))

    layout = dict(T.PLOTLY_LAYOUT)
    layout["xaxis"] = dict(layout["xaxis"], title=None, side="top",
                            tickangle=-30)
    layout["yaxis"] = dict(layout["yaxis"], title=None, autorange="reversed")
    layout["height"] = 460
    layout["margin"] = dict(l=80, r=40, t=80, b=40)
    fig.update_layout(**layout)
    return fig


def sparkline(df_annual, group, city="Australia"):
    """12-month YoY sparkline for one group × city."""
    d = df_annual.copy()
    if city == "Australia":
        d = (d[d["city"].isin(dl.CITIES)]
             .groupby(["date", "group"], as_index=False)["annual_pct"].mean())
    else:
        d = d[d["city"] == city]
    d = d[d["group"] == group].sort_values("date").tail(12)

    fig = go.Figure(go.Scatter(
        x=d["date"], y=d["annual_pct"], mode="lines+markers",
        line=dict(color=T.VERMILLION, width=2.5),
        marker=dict(size=5),
        hovertemplate="%{x|%b %Y}<br>%{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=T.RBA_MIDPOINT,
                  line=dict(color=T.DEEP_TEAL, width=1, dash="dash"))
    fig.update_layout(
        height=180, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=T.OFF_WHITE, plot_bgcolor=T.OFF_WHITE,
        xaxis=dict(showgrid=False, tickfont=dict(size=9, color=T.MID_GREY)),
        yaxis=dict(showgrid=True, gridcolor="#E5E7EB", ticksuffix="%",
                   tickfont=dict(size=9, color=T.MID_GREY)),
        showlegend=False,
        title=dict(text=f"<b>{group}</b> · {city} — last 12 months",
                   font=dict(size=12, color=T.CHARCOAL), x=0),
    )
    return fig


def whatif_real_wage_gap(df_annual, wage_growth_pct):
    """Per-city bar: wage_growth - city CPI."""
    latest_date = df_annual["date"].max()
    snap = df_annual[(df_annual["date"] == latest_date)
                     & (df_annual["group"] == "All Groups CPI")
                     & (df_annual["city"].isin(dl.CITIES))].copy()
    snap["gap"] = wage_growth_pct - snap["annual_pct"]
    snap = snap.sort_values("gap", ascending=True)

    colors = [T.DEEP_TEAL if g >= 0 else T.VERMILLION for g in snap["gap"]]
    fig = go.Figure(go.Bar(
        x=snap["gap"], y=snap["city"], orientation="h",
        marker_color=colors,
        text=[f"{g:+.1f} pp" for g in snap["gap"]],
        textposition="outside",
        textfont=dict(size=11, color=T.CHARCOAL),
        hovertemplate="<b>%{y}</b><br>Gap: %{x:+.2f} pp<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color=T.COOL_GREY, width=1, dash="dash"))

    layout = dict(T.PLOTLY_LAYOUT)
    layout["xaxis"] = dict(layout["xaxis"],
                            title="Wage − CPI (percentage points)",
                            ticksuffix=" pp")
    layout["yaxis"] = dict(layout["yaxis"], title=None)
    layout["height"] = 360
    layout["showlegend"] = False
    layout["margin"] = dict(l=100, r=60, t=40, b=40)
    fig.update_layout(**layout)
    return fig