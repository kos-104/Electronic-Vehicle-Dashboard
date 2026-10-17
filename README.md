# Electronic Vehicle Dashboard (Streamlit)

## Overview
A Streamlit dashboard for exploring EV sales and vehicle specifications.

This repo includes the SQLite database file ev_data.db so the app can run after cloning.

## Project layout
- MainApp.py — entry point
- ev_data.db — included SQLite database (expected in project root)
- data/ — supporting files (if present)

## Clone-and-run (quick start)
1) Install dependencies:
   pip install -r requirements.txt

2) Start the app:
   python -m streamlit run MainApp.py

## Notes
- **ev_data.db must be present in the project root directory** (CWD when you run Streamlit).  
  If it’s missing, the app will fail to load the database.
