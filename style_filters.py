import streamlit as st

print("LOADED STYLE_FILTERS FROM:", __file__)

# ---------------------------------------------------------
# Colors for multiselect “tag pills” (one flat color per filter)
# ---------------------------------------------------------
FILTER_STYLES = {
    "vehicle_type_container": "#1E88E5",
    "brand_container": "#43A047",
    "country_container": "#FB8C00",
    "battery_type_container": "#8E24AA",
    "financing_type_container": "#00897B",
    "usage_type_container": "#E53935",
    "vc_brand_container": "#3949AB",
    "vc_battery_type_container": "#00ACC1",
    "vc_drive_type_container": "#7CB342",
    "vc_country_container": "#D81B60",
    # NOTE: match_brand_container intentionally excluded — it uses
    # per-pill cycling colors via apply_brand_pill_colors() instead
    # of a single flat container color. See below.
}


def apply_filter_colors():
    # Apply CSS so each filter pill gets a consistent background color
    rules = "\n".join(
        f"""
        .st-key-{key} span[data-tag] {{
            background-color: {color} !important;
            color: white !important;
        }}
        """
        for key, color in FILTER_STYLES.items()
    )

    st.markdown(f"""
        <style>
        {rules}
        span[data-tag] * {{
            color: white !important;
        }}
        span[data-tag] button svg path {{
            stroke: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# Per-pill cycling colors (used by Tab 3's brand filter)

# Unlike FILTER_STYLES, which paints an entire container one
# flat color, this cycles N colors across pills by DOM position.
#
# Caveat: colors are stable per SLOT, not per brand. Deselecting
# a pill shifts everything after it by one position, which can
# change its color. An acceptable tradeoff for visual variety —
# not meant to guarantee "Tesla is always blue."
# ---------------------------------------------------------
BRAND_PILL_COLORS = ["#1E88E5", "#E53935", "#43A047", "#C9A227"]  # blue, red, green, mustard — cycles every 4


def apply_brand_pill_colors(container_key):
    cycle_length = len(BRAND_PILL_COLORS)

    rules = "\n".join(
        f"""
        .st-key-{container_key} span[data-tag]:nth-of-type({cycle_length}n+{i + 1}) {{
            background-color: {color} !important;
            color: white !important;
        }}
        """
        for i, color in enumerate(BRAND_PILL_COLORS)
    )
    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Chart radio button styling
# ---------------------------------------------------------
RADIO_BORDER_UNSELECTED = "#999999"
RADIO_BORDER_SELECTED = "#8B0000"
SECTION_DIVIDER = "#3B1F5A" # "#5E2B97"
RADIO_ACCENT_SELECTED = "#1f77b4"


def apply_chart_radio_colors():
    # Change the look of the chart-type radio buttons
    st.markdown(f"""
        <style>
        /* Selected circle - outer ring
           Matches Tab 1's wrapped container key, and Tab 2/3's direct radio keys */
        [class*="st-key-chart_controls_container"] label[data-selected="true"] .eqiohyi4,
        [class*="st-key-vc_chart_"] label[data-selected="true"] .eqiohyi4,
        [class*="st-key-match_chart_"] label[data-selected="true"] .eqiohyi4 {{
            border-color: {RADIO_BORDER_SELECTED} !important;
        }}

        /* Selected circle - inner dot */
        [class*="st-key-chart_controls_container"] label[data-selected="true"] .eqiohyi5,
        [class*="st-key-vc_chart_"] label[data-selected="true"] .eqiohyi5,
        [class*="st-key-match_chart_"] label[data-selected="true"] .eqiohyi5 {{
            background-color: {RADIO_ACCENT_SELECTED} !important;
        }}

        /* Unselected circle - border color (keeps consistent look) */
        [class*="st-key-chart_controls_container"] label[data-testid="stRadioOption"] .eqiohyi4,
        [class*="st-key-vc_chart_"] label[data-testid="stRadioOption"] .eqiohyi4,
        [class*="st-key-match_chart_"] label[data-testid="stRadioOption"] .eqiohyi4 {{
            border-color: {RADIO_BORDER_UNSELECTED} !important;
        }}

        /* Selected label text */
        [class*="st-key-chart_controls_container"] label[data-selected="true"] div[data-testid="stMarkdownContainer"] p,
        [class*="st-key-vc_chart_"] label[data-selected="true"] div[data-testid="stMarkdownContainer"] p,
        [class*="st-key-match_chart_"] label[data-selected="true"] div[data-testid="stMarkdownContainer"] p {{
            color: {RADIO_ACCENT_SELECTED} !important;
            font-weight: 600;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_range_slider_filter(df, column, label, step, container_key=None):
    """
    Renders a range slider for a numeric column and returns the
    (min, max) tuple selected by the user.
    """
    col_min = float(df[column].min())
    col_max = float(df[column].max())

    if container_key:
        with st.container(key=container_key):
            selected_range = st.slider(
                label,
                min_value=col_min,
                max_value=col_max,
                value=(col_min, col_max),
                step=step
            )
    else:
        selected_range = st.slider(
            label,
            min_value=col_min,
            max_value=col_max,
            value=(col_min, col_max),
            step=step
        )

    return selected_range


# ---------------------------------------------------------
# Slider styling
# ---------------------------------------------------------
SLIDER_STYLES = {
    "vc_battery_capacity_container": "#3949AB",
    "vc_acceleration_container": "#00ACC1",
    "vc_energy_consumption_container": "#7CB342",
}

def apply_slider_colors():
    # Color the slider bar/background for each slider container
    rules = "\n".join(
        f"""
        .st-key-{key} {{
            margin-bottom: 1.5rem;
        }}
        .st-key-{key} .st-emotion-cache-1v3hvtd {{
            background-color: {color} !important;
        }}
        """
        for key, color in SLIDER_STYLES.items()
    )
    st.markdown(f"<style>{rules}</style>", unsafe_allow_html=True)

def apply_slider_label_bold():
    # Make slider labels bold to stand out
    selectors = ", ".join(
        f'.st-key-{key} [data-testid="stWidgetLabel"] p'
        for key in SLIDER_STYLES
    )
    st.markdown(f"""
        <style>
        {selectors} {{
            font-weight: 700 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

def render_section_divider():
    # Apply a visual horizontal divider to separate sections for each tab
    st.markdown(f"""
        <div style="
            height: 3.22px;
            background-color: {SECTION_DIVIDER};
            opacity: 0.6;
            margin: 2rem 0;
            border-radius: 2px;
        "></div>
    """, unsafe_allow_html=True)

def apply_global_font():
    # Set the font + global background color for the whole app
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

        <style>
            /* Font */
            html, body, [class*="st-"] {
                font-family: 'Inter', sans-serif;
            }

            /* Whole page background */
            html, body {
                background-color:  #EBEEF7 !important; #F6F8FC
            }

            /* Streamlit app wrapper */
            [data-testid="stApp"] {
                background-color:  #EBEEF7 !important;
            }

            /* Sometimes Streamlit uses these containers for visible area */
            .stApp {
                background-color:  #EBEEF7 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    

# ---------------------------------------------------------
# Kept as a backup/experiment: alternative font version.
# ---------------------------------------------------------
# def apply_global_font():
#     st.markdown(
#         """
#         <link rel="preconnect" href="https://fonts.googleapis.com">
#         <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
#         <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&display=swap" rel="stylesheet">

#         <style>
#           .stApp, .stApp * {
#             font-family: "Lora", Georgia, "Times New Roman", Times, serif !important;
#           }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

