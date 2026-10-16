import pandas as pd
import sqlite3
import os
import streamlit as st
import plotly.express as px

# --- UI styling helpers (colors + consistent Streamlit widget styling) ---
from style_filters import (
    apply_filter_colors,
    render_range_slider_filter,
    apply_chart_radio_colors,
    apply_slider_colors,
)

# --- Data/filter helpers (build filtered data + common filter components) ---
from filter_helpers import render_multiselect_filter, build_year_grouped_chart_df

# --- Chart helpers (construct figures from prepared data) ---
from chart_helpers import build_year_value_line_fig

print("Loaded tab1_salesRedo from:", __file__)


def render():
    # ---------------------------------------------------------
    # Load data from SQLite
    # ---------------------------------------------------------
    db_path = os.path.join(os.path.dirname(__file__), "ev_data.db")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()

    # Sale_Date is stored as plain text in SQLite, so we convert
    # it to a real date inside of pandas, then extract the Year for 
    # grouping/charting later.
    df["Sale_Date"] = pd.to_datetime(df["Sale_Date"], errors="coerce")
    df["Year"] = df["Sale_Date"].dt.year

    # ---------------------------------------------------------
    # Page header
    # ---------------------------------------------------------
    st.header("Explore electric vehicle sales transactions")

    # Calculate start and end dates for data coverage
    # (Used only for the caption so users know what years are included)
    min_date = df["Sale_Date"].min()
    max_date = df["Sale_Date"].max()

    st.caption(
        f"Sales data coverage: {min_date:%b %Y} to {max_date:%b %Y}."
        if pd.notna(min_date) and pd.notna(max_date)
        else "Sales data coverage: (date range unavailable)."
    )

    # Ensure widget colors match the app theme
    apply_filter_colors()

    # Show filters with medium size
    st.subheader("Filters")
    
    # ---------------------------------------------------------
    # Multiselect filters return the selected values (lists)
    # ---------------------------------------------------------    
    selected_vehicle_types = render_multiselect_filter(
        df, "Vehicle_Type", "Vehicle Types", "vehicle_type_container"
    )

    selected_brands = render_multiselect_filter(
        df, "Brand", "Brands", "brand_container"
    )

    selected_countries = render_multiselect_filter(
        df, "Country", "Countries", "country_container"
    )

    selected_batteries = render_multiselect_filter(
        df, "Battery_Type", "Batteries", "battery_type_container"
    )

    selected_financing_types = render_multiselect_filter(
        df, "Financing_Type", "Financing Types", "financing_type_container"
    )

    selected_usage_types = render_multiselect_filter(
        df, "Fleet_or_Personal", "Usage Types", "usage_type_container"
    )
    
    # Apply all selected filters (AND logic: all conditions must be true)
    filtered_df = df[
        df["Vehicle_Type"].isin(selected_vehicle_types)
        & df["Brand"].isin(selected_brands)
        & df["Country"].isin(selected_countries)
        & df["Battery_Type"].isin(selected_batteries)
        & df["Financing_Type"].isin(selected_financing_types)
        & df["Fleet_or_Personal"].isin(selected_usage_types)
    ]
    
    # Creates a list of columns that need to be prioritized
    priority_cols = [
        "Sale_Date",
        "Brand",
        "Country",
        "Vehicle_Type",
        "Battery_Type",
        "Financing_Type",
        "Fleet_or_Personal",
    ]
    
    # Keep priority columns first, so the results table feels consistent
    remaining_cols = [col for col in filtered_df.columns if col not in priority_cols]
    filtered_df = filtered_df[priority_cols + remaining_cols]
    
    # Create 1-based dataframe index display
    filtered_df = filtered_df.reset_index(drop=True)    
    filtered_df.index = filtered_df.index + 1

    # ---------------------------------------------------------
    # Filtered range caption (only when there is data)
    # ---------------------------------------------------------
    if not filtered_df.empty:
        filtered_min = filtered_df["Sale_Date"].min()
        filtered_max = filtered_df["Sale_Date"].max()
        
        # Only display the caption if the dates are valid (not NaT/NaN)
        if pd.notna(filtered_min) and pd.notna(filtered_max):
            st.caption(
                f"Filtered range: {filtered_min:%b %Y} to {filtered_max:%b %Y}."
            )            
            
    # Keep track of total rows in the full dataset (before filtering)
    total_rows = len(df)    
    
    # Provide user feedback if filters remove all rows
    if filtered_df.empty:
        st.warning("No data to display — please select at least one option in each filter above.")
    else:
        # Provide user feedback if filters remove all rows
        if len(filtered_df) == total_rows:
            st.write(f"Showing {len(filtered_df)} rows")
        else:
            st.write(f"Showing {len(filtered_df)} rows out of {total_rows}")

    # Display the filtered dataset as a table, using a DateColumn - 
    # so the Sale_Date column renders with the desired formatting.
    st.dataframe(
        filtered_df,
        column_config={
            "Sale_Date": st.column_config.DateColumn(
                "Sale_Date",
                format="YYYY-MM-DD",
            )
        },
    )

    # ---------------------------------------------------------
    # Display the chart
    # ---------------------------------------------------------
    st.subheader("Sales Overview")
    
    if filtered_df.empty:
        # If no rows survive the filters, we can’t build a chart.
        st.warning("No chart to display — please select at least one option in each filter above.")
    else:
        # -------------------------------------------------------------
        # Sales trend reminder (sharp drop detection)
        # Uses filtered_df so it matches the currently selected filters
        # -------------------------------------------------------------
        
        # Count sales rows per year from the filtered dataset
        year_counts = (
            filtered_df.dropna(subset=["Year"])
            .groupby("Year")
            .size()
            .reset_index(name="sales_count")
            .sort_values("Year")
        )

        drop_msg_shown = False
        
        if len(year_counts) >= 4:
            # Compare each year’s sales count to the previous year
            year_counts["prev"] = year_counts["sales_count"].shift(1)
            year_counts["ratio"] = year_counts["sales_count"] / year_counts["prev"]

            # Identify “sharp drops” where the ratio is <= 0.50
            sharp_drops = year_counts[
                (year_counts["prev"] > 0)
                & (year_counts["ratio"].notna())
                & (year_counts["ratio"] <= 0.50)
            ]

            if not sharp_drops.empty:
                # Show a caption to explain the apparent plunge is likely due
                # to the dataset ending mid-2025.                
                st.caption(
                    "Reminder: The chart shows a sharp sales decline simply because "
                    "our sales data ends in mid-2025"
                )
                drop_msg_shown = True
        
        # If we didn’t trigger via the detection logic, still show the gentle note
        # about the mid-2025 cut-off to prevent misinterpretation.
        if not drop_msg_shown:
            st.markdown(
                '<span style="font-size: 0.9em;">*WARNING: The plunge in sales is deceptive and results only because information used in the dataset halts in mid-2025, thereby NOT reflecting the true market!*'
                '</span>',
                unsafe_allow_html=True
            )

        # Apply chart widget coloring (radio button theme)
        apply_chart_radio_colors()
        
        # ---------------------------------------------------------
        # Chart controls (group + metric)
        # ---------------------------------------------------------
        with st.container(key="chart_controls_container"):
            dimension_choice = st.radio(
                "Group by",
                options=[
                    "Brand",
                    "Country",
                    "Vehicle Type",
                    "Battery Type",
                    "Financing Type",
                    "Fleet or Personal",
                ],
                horizontal=True,
                key="chart_dimension",
            )

            metric_choice = st.radio(
                "View by",
                options=["Total Sales ($)", "Sales Count"],
                horizontal=True,
                key="chart_metric",
            )            
            
        # Map the UI label (“Brand”, “Vehicle Type”, etc.) to the 
        # true column name in the dataframe.
        dimension_column_map = {
            "Brand": "Brand",
            "Country": "Country",
            "Vehicle Type": "Vehicle_Type",
            "Battery Type": "Battery_Type",
            "Financing Type": "Financing_Type",
            "Fleet or Personal": "Fleet_or_Personal",
        }
        group_column = dimension_column_map[dimension_choice]
        
        # Build a year-by-year chart dataframe aggregated by the selected group column
        chart_df = build_year_grouped_chart_df(
            df=filtered_df,
            year_col="Year",
            metric_choice=metric_choice,
            group_col=group_column,
        )

        # Label the y-axis based on what the user chose to view
        y_label = "Total Sales (USD)" if metric_choice == "Total Sales ($)" else "Sales Count"

        # Create the Plotly figure from the aggregated chart dataframe
        fig = build_year_value_line_fig(
            chart_df=chart_df,
            color_col=group_column,
            y_label=y_label,
        )

        # Render the chart
        st.plotly_chart(fig, width="stretch")