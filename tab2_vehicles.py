import pandas as pd
import sqlite3
import os
import streamlit as st
import plotly.express as px
from chart_helpers import build_vehicle_spec_scatter_fig

from style_filters import (
    apply_filter_colors,
    render_range_slider_filter,
    apply_slider_colors,
    apply_slider_label_bold,
    apply_chart_radio_colors,
    # apply_global_font,
)
from filter_helpers import render_multiselect_filter


def render():
    # ---------------------------------------------------------
    # Load data from SQLite.
    # This tab uses the vehicles table — spec/catalog data only.
    # Sales transactions are handled separately in Tab 1.
    # ---------------------------------------------------------
    db_path = os.path.join(os.path.dirname(__file__), "ev_data.db")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM vehicles", conn)
    conn.close()

    st.header("Browse and filter EV specifications")
    
    # Apply consistent theme styling for this tab’s widgets/charts
    apply_filter_colors()
    apply_slider_colors()
    apply_slider_label_bold()
    apply_chart_radio_colors()
    
    st.subheader("Filters")
    
    # Two-column layout for categorical filters and numeric sliders
    left_col, right_col = st.columns(2)
    
    # ---------------------------------------------------------
    # Categorical filters (multiselect)
    # ---------------------------------------------------------
    with left_col:
        selected_brands = render_multiselect_filter(
            df, "Brand", "Brands", "vc_brand_container"
        )

        selected_battery_types = render_multiselect_filter(
            df, "Battery_Type", "Battery Types", "vc_battery_type_container"
        )

        selected_drive_types = render_multiselect_filter(
            df, "Drive_Type", "Drive Types", "vc_drive_type_container"
        )

        selected_countries = render_multiselect_filter(
            df, "Country", "Countries", "vc_country_container"
        )
        
    # ---------------------------------------------------------
    # Numeric filters (range sliders)
    # ---------------------------------------------------------
    with right_col:
        battery_capacity_range = render_range_slider_filter(
            df,
            "Battery_Capacity_kWh",
            "Battery Capacity (kWh)",
            step=1.0,
            container_key="vc_battery_capacity_container",
        )

        acceleration_range = render_range_slider_filter(
            df,
            "Acceleration_0_100_sec",
            "0-100 Acceleration (sec)",
            step=0.1,
            container_key="vc_acceleration_container",
        )

        energy_consumption_range = render_range_slider_filter(
            df,
            "Energy_Consumption_Wh_km",
            "Energy Consumption (Wh/km)",
            step=1.0,
            container_key="vc_energy_consumption_container",
        )
        
    # Set the time ranges for slider so we can filter in-between min-max dates
    battery_capacity_min, battery_capacity_max = battery_capacity_range
    acceleration_min, acceleration_max = acceleration_range
    energy_consumption_min, energy_consumption_max = energy_consumption_range

    # ---------------------------------------------------------
    # Apply all filters (AND logic)
    # ---------------------------------------------------------
    filtered_df = df[
        df["Brand"].isin(selected_brands)
        & df["Battery_Type"].isin(selected_battery_types)
        & df["Drive_Type"].isin(selected_drive_types)
        & df["Country"].isin(selected_countries) 
        & df["Battery_Capacity_kWh"].between(battery_capacity_min, battery_capacity_max)
        & df["Acceleration_0_100_sec"].between(acceleration_min, acceleration_max)
        & df["Energy_Consumption_Wh_km"].between(
            energy_consumption_min, energy_consumption_max
        )
    ].copy()
    
    # ---------------------------------------------------------
    # Reorder columns and show major fields first
    # ---------------------------------------------------------
    priority_cols = [
        "Brand",
        "Country",
        "Model",
        "Battery_Type",
        "Drive_Type",
        "Battery_Capacity_kWh",
        "Acceleration_0_100_sec",
        "Energy_Consumption_Wh_km",
    ]

    # Keep priority columns first, so the results table feels consistent
    remaining_cols = [col for col in filtered_df.columns if col not in priority_cols]
    filtered_df = filtered_df[priority_cols + remaining_cols]

    # Create 1-based dataframe index display
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1
    
    # Keep track of total rows in the full dataset (before filtering)
    total_rows = len(df)
    
    # If filtering removes everything, stop early so we don’t try to build an empty chart.
    if filtered_df.empty:
        st.warning("No data to display — please adjust your filters above.")
        return
    
    # Let the user know whether filters changed the dataset size
    if len(filtered_df) == total_rows:
        st.write(f"Showing {len(filtered_df)} rows")
    else:
        st.write(f"Showing {len(filtered_df)} rows out of {total_rows}")

    # Data table (comes before chart for consistency)
    st.dataframe(filtered_df)

    # ---------------------------------------------------------
    # Chart (NEW) - simple scatter with configurable axes
    # ---------------------------------------------------------
    st.subheader("Vehicle Spec Chart")

    numeric_x_options = [
        "Battery_Capacity_kWh",
        "Acceleration_0_100_sec",
        "Energy_Consumption_Wh_km",
    ]

    numeric_y_options = [
        "Battery_Capacity_kWh",
        "Acceleration_0_100_sec",
        "Energy_Consumption_Wh_km",
    ]

    color_options = ["None", "Brand", "Country", "Drive_Type", "Battery_Type"]

    # Axis radios (use unique keys to avoid widget-state coflicts)
    colA, colB = st.columns(2)
    with colA:
        x_col = st.radio(
            "X-axis",
            options=numeric_x_options,
            index=0,
            horizontal=True,
            key="vc_chart_x",
        )
    with colB:
        y_col = st.radio(
            "Y-axis",
            options=numeric_y_options,
            index=1,
            horizontal=True,
            key="vc_chart_y",
        )
        
    # Create categorical coloring for easier comparison
    color_by = st.radio(
        "Color by",
        options=color_options,
        index=1,
        horizontal=True,
        key="vc_chart_color_by",
    )
    
    # Prevent the user from selecting identical axes
    if x_col == y_col:
        st.warning("X-axis and Y-axis are the same. Please choose different fields.")
        return
    
    # Copy to keep the chart helper free to modify if needed
    plot_df = filtered_df.copy()
    
    # Build the scatter figure using the shared chart helper
    fig = build_vehicle_spec_scatter_fig(
        plot_df=plot_df,
        x_col=x_col,
        y_col=y_col,
        color_by=None if color_by == "None" else color_by,
        hover_data=["Brand", "Model", "Country", "Drive_Type", "Battery_Type"],
        opacity=0.85,
    )
    
    # Render the chart
    st.plotly_chart(fig, use_container_width=True)
