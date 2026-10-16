import pandas as pd
import sqlite3
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --- UI styling helpers (colors + consistent Streamlit widget styling) ---
from style_filters import (
    apply_filter_colors,
    apply_brand_pill_colors,
    apply_chart_radio_colors,
)

# --- Data/filter helpers (build filtered data + common filter components) --- 
from filter_helpers import render_multiselect_filter

# --- Chart helpers (construct figures from prepared data) --- 
from chart_helpers import build_year_value_line_fig


def render():
    # -------------------------------------------------------------------------
    # Load data from SQLite
    # This tab demonstrates the JOIN between sales and vehicles via Vehicle_ID
    # -------------------------------------------------------------------------
    db_path = os.path.join(os.path.dirname(__file__), "ev_data.db")
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            sales.Sale_ID,
            sales.Sale_Date,
            sales.Vehicle_ID,
            sales.Final_Price_USD,
            sales.Payment_Method,
            vehicles.Brand,
            vehicles.Model,
            vehicles.Battery_Type,
            vehicles.Battery_Capacity_kWh,
            vehicles.Country
        FROM sales
        JOIN vehicles ON sales.Vehicle_ID = vehicles.Vehicle_ID
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    st.header("Matched Vehicle Sales (JOIN Demo)")

    st.info(
        f"This tab joins the `sales` and `vehicles` tables on `Vehicle_ID`. "
        f"Only **{len(df)} of 5,000** sales records have a `Vehicle_ID` that "
        f"exists in the vehicle catalog — the two ID spaces appear to have "
        f"been generated independently, so most values don't align. "
        f"The matches below are likely coincidental overlaps, not a reliable join."
    )

    # ---------------------------------------------------------------
    # Metrics — calculated on the FULL matched set (before filtering)
    # ---------------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    if df.empty:
        total_revenue = 0.0
        unique_brands = 0
    else:
        total_revenue = float(df["Final_Price_USD"].sum())
        unique_brands = int(df["Brand"].nunique())

    with col1:
        st.metric("Matched Sales", len(df))

    with col2:
        st.metric("Total Revenue (Matched)", f"${total_revenue:,.0f}")

    with col3:
        st.metric("Unique Brands Represented", unique_brands)

    # -----------------------------------------------------------------
    # Filter — applied after metrics, only affects table + chart below
    # -----------------------------------------------------------------
    apply_filter_colors()
    apply_brand_pill_colors("match_brand_container")

    if df.empty:
        st.warning("No matched rows found — try adjusting your data or regenerating the database.")
        st.dataframe(pd.DataFrame())
        return
    
    # User filter (single dimension): kept simple so the counts are easy to interpret
    selected_brands = render_multiselect_filter(
        df=df,
        column="Brand",
        label="Brands",
        container_key="match_brand_container",
    )

    df_filtered = df[df["Brand"].isin(selected_brands)].copy()

    # ---------------------------------------------------------
    # Data table (comes before chart for consistency)
    # ---------------------------------------------------------
    priority_cols = ["Sale_Date",
                        "Brand", 
                        "Country", 
                        "Model", 
                        "Battery_Type", 
                        "Payment_Method",
                    ]
        
    # Keep the important columns first, then show the remaining columns,
    # but place the Final_Price_USD columnn at the end.    
    remaining_cols = [c for c in df_filtered.columns if c not in priority_cols and c != "Final_Price_USD"]
    df_filtered = df_filtered[priority_cols + remaining_cols + ["Final_Price_USD"]]
        
    # Display index as 1-based so row numbers are more user-friendly
    df_display = df_filtered.reset_index(drop=True)
    df_display.index = df_display.index + 1  # 1-based index for display

    total_rows = len(df)
    filtered_rows = len(df_display)
    
    # Quick “sanity" check to verify how much the filter narrowed the dataset
    if filtered_rows == total_rows:
        st.write(f"Showing {filtered_rows} rows")
    else:
        st.write(f"Showing {filtered_rows} rows out of {total_rows}")

    st.dataframe(df_display)

    # ---------------------------------------------------------
    # Display the chart
    # ---------------------------------------------------------
    st.subheader("Matched Sales Overview")

    if df_filtered.empty:
        st.warning("No chart to display — please select at least one option in each filter above.")
        return

    # Build Year from Sale_Date (like Tab 1)
    # Coerce invalid dates to NaT, then drop them
    df_filtered["Sale_Date"] = pd.to_datetime(df_filtered["Sale_Date"], errors="coerce")
    df_filtered = df_filtered.dropna(subset=["Sale_Date"])
    df_filtered["Year"] = df_filtered["Sale_Date"].dt.year

    if df_filtered.empty:
        st.warning("No chart data available after parsing Sale_Date into Year.")
        return

    # Apply consistent chart widget colors for the radios
    apply_chart_radio_colors()

    with st.container(key="match_chart_controls_container"):
        dimension_choice = st.radio(
            "Group by",
            options=["Brand", "Country", "Model", "Battery Type", "Payment_Method", "None"],
            horizontal=True,
            key="match_chart_dimension",
        )

        metric_choice = st.radio(
            "View by",
            options=["Total Sales ($)", "Sales Count"],
            horizontal=True,
            key="match_chart_metric",
        )

    dimension_column_map = {
        "Brand": "Brand",
        "Country": "Country",
        "Model": "Model",
        "Battery Type": "Battery_Type",
        "Payment_Method": "Payment_Method",
        "None": None,
    }
    group_column = dimension_column_map[dimension_choice]

    # Force chronological ordering for the category axis (fixes 2024 before 2023)
    years_sorted = sorted(df_filtered["Year"].dropna().unique().tolist())
    category_years = [str(y) for y in years_sorted]  # Plotly category safety

    # -----------------------------
    # Build chart data
    # -----------------------------
    if metric_choice == "Total Sales ($)":
        y_label = "Total Sales (USD)"
        if group_column is None:
            chart_df = (
                df_filtered.groupby(["Year"], as_index=False)["Final_Price_USD"]
                .sum()
                .rename(columns={"Final_Price_USD": "Value"})
            )
            color_col = None
        else:
            chart_df = (
                df_filtered.groupby(["Year", group_column], as_index=False)["Final_Price_USD"]
                .sum()
                .rename(columns={"Final_Price_USD": "Value"})
            )
            color_col = group_column
    else:
        y_label = "Sales Count"
        if group_column is None:
            chart_df = (
                df_filtered.groupby(["Year"], as_index=False)
                .size()
                .rename(columns={"size": "Value"})
            )
            color_col = None
        else:
            chart_df = (
                df_filtered.groupby(["Year", group_column], as_index=False)
                .size()
                .rename(columns={"size": "Value"})
            )
            color_col = group_column

    # ------------------------------------
    # Special case: Model legend + colors
    # ------------------------------------
    if dimension_choice == "Model":
        # Build (Year, Brand, Model) so legend can show "Brand - Model"
        if metric_choice == "Total Sales ($)":
            chart_df = (
                df_filtered.groupby(["Year", "Brand", "Model"], as_index=False)["Final_Price_USD"]
                .sum()
                .rename(columns={"Final_Price_USD": "Value"})
            )
        else:
            chart_df = (
                df_filtered.groupby(["Year", "Brand", "Model"], as_index=False)
                .size()
                .rename(columns={"size": "Value"})
            )
            
        # Create a combined legend label to make vehicles easy to identify
        chart_df["Legend_Label"] = chart_df["Brand"].astype(str) + " - " + chart_df["Model"].astype(str)
        chart_df = chart_df.sort_values(["Brand", "Model", "Year"])

        fig = go.Figure()

        # One trace per (Brand - Model)
        legend_groups = (
            chart_df[["Legend_Label", "Brand", "Model"]]
            .drop_duplicates()
            .sort_values(["Brand", "Model"])
            .itertuples(index=False)
        )

        # Distinct colors per model trace (not colored by brand)
        model_labels = chart_df["Legend_Label"].dropna().unique().tolist()
        palette = px.colors.qualitative.Plotly
        label_to_color = {lab: palette[i % len(palette)] for i, lab in enumerate(model_labels)}

        for legend_label, brand, model in legend_groups:
            df_lm = chart_df[
                (chart_df["Legend_Label"] == legend_label)
                & (chart_df["Brand"] == brand)
                & (chart_df["Model"] == model)
            ].sort_values("Year")

            fig.add_trace(
                go.Scatter(
                    x=df_lm["Year"].astype(str),
                    y=df_lm["Value"],
                    mode="lines+markers",
                    name=legend_label,  # "Brand - Model"
                    line=dict(color=label_to_color.get(legend_label)),
                    marker=dict(size=6),
                )
            )
            
        # Lock in the X-axis ordering using the precomputed category_years
        fig.update_layout(
            yaxis_title=y_label,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=category_years,
            ),
            legend=dict(traceorder="normal"),
        )

        st.plotly_chart(fig, width="stretch")

    # -----------------------------
    # Default: use helper function
    # -----------------------------
    else:
        # Use the shared year aggregation + line chart builder for consistency
        fig = build_year_value_line_fig(
            chart_df=chart_df,
            color_col=color_col,
            y_label=y_label,
            markers=True,
        )
        
        # Ensure the x-axis uses chronological ordering
        fig.update_layout(
            xaxis=dict(
                type="category",
                categoryorder="array",
                categoryarray=category_years,
            )
        )
        
        # Render the chart
        st.plotly_chart(fig, width="stretch")