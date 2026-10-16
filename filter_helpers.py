import streamlit as st

def render_multiselect_filter(df, column, label, container_key):
    # ---------------------------------------------------------
    # “Select All” + multiselect filter with session state sync.
    #
    # Goal:
    #  - checkbox controls whether the multiselect shows all options vs none
    #  - multiselect changes update the checkbox when user manually deselects
    # ---------------------------------------------------------    
    options = sorted(df[column].unique())

    multiselect_key = f"{container_key}_multiselect"
    checkbox_key = f"{container_key}_checkbox"

    with st.container(key=container_key):

        # Initialize state once, on first run
        if multiselect_key not in st.session_state:
            st.session_state[multiselect_key] = options

        def sync_multiselect():
            # Called whenever the checkbox changes
            # If checkbox is ON, select everything; otherwise select nothing.
            if st.session_state[checkbox_key]:
                st.session_state[multiselect_key] = options
            else:
                st.session_state[multiselect_key] = []

        def sync_checkbox():
            # Called whenever the multiselect changes
            current = st.session_state[multiselect_key]
            st.session_state[checkbox_key] = (set(current) == set(options))

        # Derive checkbox value BEFORE rendering it, based on current multiselect state
        st.session_state[checkbox_key] = (set(st.session_state[multiselect_key]) == set(options))

        # Checkbox: “Select All ...”
        st.checkbox(
            f"Select All {label}",
            key=checkbox_key,
            on_change=sync_multiselect
        )

        # Multiselect: user selects subset from the options
        st.multiselect(
            f"Select by {label}",
            options,
            key=multiselect_key,
            on_change=sync_checkbox
        )

    # Return the selected option list for the calling tab
    return st.session_state[multiselect_key]

def get_metric_aggregation_config(metric_choice: str) -> dict:
    if metric_choice == "Total Sales ($)":
        return {"value_column": "Final_Price_USD", "agg_func": "sum", "label": "Total Sales (USD)"}
    elif metric_choice == "Sales Count":
        return {"value_column": None, "agg_func": "count_rows", "label": "Sales Count"}
    else:
        raise ValueError(f"Unknown metric_choice: {metric_choice}")

def build_year_grouped_chart_df(
    df: pd.DataFrame,
    year_col: str,
    metric_choice: str,
    group_col: str | None = None,
) -> pd.DataFrame:
    """
    Prepares the dataframe used by build_year_value_line_fig.

    Output:
      - always includes: ["Year", "Value"]
      - includes: group_col if provided (so px.line can color by it)
    """
            
    # ---------------------------------------------------------
    # Choose the aggregation method + column based on metric selection
    # ---------------------------------------------------------
    cfg = get_metric_aggregation_config(metric_choice)    
    
    # ---------------------------------------------------------
    # Aggregate either by:
    #  - Year
    #  - or (Year + group_col) when grouping/coloring is enabled
    # ---------------------------------------------------------
    if cfg["agg_func"] == "sum":
        if group_col is None:
            out = df.groupby([year_col], as_index=False)[cfg["value_column"]].sum()
            out = out.rename(columns={cfg["value_column"]: "Value"})
        else:
            out = df.groupby([year_col, group_col], as_index=False)[cfg["value_column"]].sum()
            out = out.rename(columns={cfg["value_column"]: "Value"})

    else:  # count_rows
        if group_col is None:
            out = df.groupby([year_col], as_index=False).size()
            out = out.rename(columns={"size": "Value"})
        else:
            out = df.groupby([year_col, group_col], as_index=False).size()
            out = out.rename(columns={"size": "Value"})

    # Standardize output schema expected by the chart helper
    out = out.rename(columns={year_col: "Year"})
    return out
