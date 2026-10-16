# chart_helpers.py
import plotly.express as px
import pandas as pd

# Used to build a year-based line chart for Tabs 1 and 3 (optionally grouped by color_col)
def build_year_value_line_fig(
    chart_df: pd.DataFrame,
    color_col: str | None,
    y_label: str,
    markers: bool = True,
):
    
    # ---------------------------------------------------------
    # Shared “Tab 1 and Tab 3 style” line chart builder
    #
    # Produces:
    #  - X-axis: Year (treated as category to maintain ordering)
    #  - Y-axis: Value (already pre-aggregated by the calling tab)
    #  - Optional color grouping when color_col is provided
    # ---------------------------------------------------------
    """
    For Tabs 1 & 3: line chart with x="Year", y="Value", optional color grouping.

    chart_df must contain:
      - "Year"
      - "Value"
    and if color_col is provided:
      - a column with name == color_col
    """
    
    # When there is no grouping, use a single series
    if color_col is None:
        fig = px.line(chart_df, x="Year", y="Value", markers=markers)
    else:
        # When grouped, Plotly uses the given column to create multiple lines 
        fig = px.line(chart_df, x="Year", y="Value", color=color_col, markers=markers)
        
    # Keep layout styling consistent across tabs
    fig.update_layout(
        xaxis=dict(type="category"),
        yaxis_title=y_label,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig

# Build a vehicle scatter chart based on user-chosen specifications
def build_vehicle_spec_scatter_fig(
    plot_df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_by: str | None,
    hover_data: list[str] | None = None,
    opacity: float = 0.85,
):  
    
    # ---------------------------------------------------------
    # Shared “Tab 2 style” scatter chart builder.
    #
    # Supports:
    #  - arrangeable x/y columns
    #  - optional color grouping
    #  - optional hover_data fields
    # ---------------------------------------------------------
    """
    For Tab 2: scatter chart with configurable axes and optional color grouping.

    If color_by is None, produces a single-color scatter.
    """
    
    # Avoid Plotly receiving hover_data=None (we standardize to an empty list)
    if hover_data is None:
        hover_data = []
        
    # Create either a single-series scatter or a grouped scatter
    if color_by is None:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            hover_data=hover_data,
            opacity=opacity,
        )
    else:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_by,
            hover_data=hover_data,
            opacity=opacity,
        )        
        
    # Keep plot chrome consistent (margins especially) across re-renders/re-triggers
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig