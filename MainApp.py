import streamlit as st
import tab1_salesRedo
import tab2_vehicles
import tab3_matched
from style_filters import render_section_divider, apply_global_font

# Apply page-wide font/CSS once
apply_global_font()

tab1_salesRedo.render()
render_section_divider()

tab2_vehicles.render()
render_section_divider()

tab3_matched.render()