# components/theme.py
"""Design system tokens — colours and Plotly defaults."""

# Core palette
NAVY            = "#1B3A5C"
SLATE_BLUE      = "#3D6B99"
OFF_WHITE       = "#FAFBFC"
LIGHT_GREY      = "#F0F2F5"
CHARCOAL        = "#1A1A2E"
MID_GREY        = "#6B7280"
PALE_GREY       = "#D1D5DB"

# Semantic colours
VERMILLION      = "#D64045"   # inflation / housing / pressure
DEEP_TEAL       = "#1A8A6E"   # easing / wage gains
AMBER           = "#E8910C"
COOL_GREY       = "#9CA3AF"

# CPI vs WPI pair
CPI_COLOR = VERMILLION
WPI_COLOR = SLATE_BLUE

# 8 capital cities (colourblind-safe Dark2 palette)
CITY_COLORS = {
    "Sydney":    "#1B9E77",
    "Melbourne": "#D95F02",
    "Brisbane":  "#7570B3",
    "Adelaide":  "#E7298A",
    "Perth":     "#66A61E",
    "Hobart":    "#E6AB02",
    "Darwin":    "#A6761D",
    "Canberra":  "#666666",
}

# 7-stop diverging scale for V4 heatmap
HEATMAP_DIVERGING = [
    [0.00, "#1A8A6E"],
    [0.17, "#7EC4AA"],
    [0.33, "#C5E5D6"],
    [0.50, "#FAFBFC"],
    [0.67, "#F0A8AA"],
    [0.83, "#E06E72"],
    [1.00, VERMILLION],
]

# Plotly layout defaults
PLOTLY_LAYOUT = dict(
    font=dict(family="-apple-system, BlinkMacSystemFont, sans-serif",
              size=12, color=CHARCOAL),
    paper_bgcolor=OFF_WHITE,
    plot_bgcolor=OFF_WHITE,
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(showgrid=False, linecolor=PALE_GREY, tickcolor=PALE_GREY,
               title_font=dict(size=11, color=MID_GREY),
               tickfont=dict(size=10, color=MID_GREY)),
    yaxis=dict(gridcolor="#E5E7EB", linecolor=PALE_GREY, tickcolor=PALE_GREY,
               title_font=dict(size=11, color=MID_GREY),
               tickfont=dict(size=10, color=MID_GREY)),
    legend=dict(font=dict(size=10, color=CHARCOAL),
                bgcolor="rgba(0,0,0,0)", orientation="h",
                yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# RBA target band
RBA_TARGET_LOW = 2.0
RBA_TARGET_HIGH = 3.0
RBA_MIDPOINT = 2.5

SOURCE_ATTRIBUTION = (
    "Source: ABS Consumer Price Index (Cat. No. 6401.0); "
    "ABS Wage Price Index (Cat. No. 6345.0). Latest: Feb 2026."
)