# EV Sales & Vehicle Specification Dashboard

**A three-tab Streamlit dashboard for exploring EV sales trends and vehicle
specifications, built as a first Python portfolio project after a
background primarily in VBA.**

![Python](https://img.shields.io/badge/Language-Python-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)
![pandas](https://img.shields.io/badge/Library-pandas-150458.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange.svg)

> **Credit / Origins:** This dashboard extends and reconfigures an earlier,
> simpler Streamlit dashboard pattern created by **Paul Kelly**. Kelly’s work
> provided the starting structure; I used this as a foundation and then
> repurposed and expanded it with a EV-focused implementation — covering the
> tab design, data workflow, UI interactions, and the JOIN-scope handling
> described below.
>
> **AI transparency:** I used AI as a coding assistant and study support while
> implementing and debugging specific sections, but the overall design/feature
> decisions and correctness validation are my own.

## Overview

- **Sales Analysis** — trends across ~5,000 EV sale transactions
- **Vehicle Catalog** — filterable browser of vehicle specs (range, battery, price, performance)
- **Matched Vehicle Sales** — a scoped SQL `JOIN` tab, deliberately small — see below for why

Built with an emphasis on clean, modular, explainable code rather than
technique chosen to look impressive. Every pattern used here is one I can
justify and rationalize, not just one that happens to work.

## The Data Problem

**The plan:** two related Kaggle CSVs, `ev_vehicles.csv` and `ev_sales.csv`,
sharing a `Vehicle_ID` key — meant to support a real `JOIN` as the
project's centerpiece.

**What I found while building that join:**

| Metric | Value |
|---|---|
| Total sales records | 5,000 |
| Records with a valid matching vehicle | 55 |
| Match rate | ~1.1% |

The join syntax wasn't the problem — I confirmed it against known-good IDs
first. The two source tables were simply generated independently, without
a consistently maintained relationship between them.

**Ruled out:**
- Forcing a full join by reassigning IDs — fabricates a relationship that isn't real
- Keeping only the 55 matched rows as the whole project — too sparse to be meaningful

**What I did instead:**
- `Sales Analysis` and `Vehicle Catalog` each run independently off their
  own table, unaffected by the join issue
- `Matched Vehicle Sales` isolates the genuine ~1% overlap and labels it
  as exactly that — a partial-match demo, not a claim of a fully relational
  dataset

This is disclosed directly rather than left for someone to discover by
reading the code. A limitation stated up front is more credible than one
found later.

*(Also disclosed: the dataset appears synthetic — sequential IDs,
generated-looking distributions, production years extending into the near
future — rather than real-world scraped data. Suitable for demonstrating
pipeline/dashboard skills; not intended as real market analysis.)*

## Design Decisions

**Structure**
- Logic split across dedicated files — `filter_helpers.py`,
  `style_filters.py`, one file per tab — rather than a single script
- Each concern changes independently: a styling tweak won't break a query,
  and vice versa

**Styling**
- UI styling (slider colors, label weight, spacing) is driven by a single
  `SLIDER_STYLES` dictionary, looped over to generate CSS
- Replaced an earlier version with three near-duplicate styling functions — the repetition signaled that a data-driven refactor was overdue, in line with the DRY (Don't Repeat Yourself) principle
**Widget State**
- All Tab 2 container keys use a consistent `vc_` prefix
- Prevents Streamlit's `DuplicateWidgetID` errors across tabs and
  self-documents its own purpose

**Scope Restraint**
- No custom classes — nothing in this project's actual complexity justifies
  them; functions and dictionaries handle our needs
- SQL limited to `SELECT`, `WHERE`, and `JOIN` — all aggregation happens in
  pandas afterward, since this is a first real exposure to SQL and every
  query here is one I fully understand

## Decision Log (Why Tab 3 is Scoped)

To keep the project truthful *and* useful as a dashboard, I avoided “fixing”
the dataset relationship by fabrication. With only **55 / 5000** sales rows
having a valid `Vehicle_ID` match, Tab 3 is intentionally implemented as a
**partial-match JOIN demo**, while Tabs 1 and 2 run independently from their
respective tables for meaningful exploration.

## Data Pipeline (How the App Gets Its Data)

- CSVs are ingested into SQLite once (see `build_database.py`)
- Streamlit reads/query-sources from SQLite (with straightforward `SELECT` / `WHERE` / `JOIN`)
- pandas performs filtering, reshaping, and all aggregation for chart-ready outputs

## What I Learned

This project surfaced a few real problems worth solving rather than
theoretical ones:

- **Widget state collisions in Streamlit.** Reusing similar filter logic
  across tabs caused `DuplicateWidgetID` errors until I understood that
  Streamlit tracks widget identity by key, not by position in the script.
  The `vc_` prefix convention in Tab 2 came directly out of debugging this.
- **The JOIN didn't behave the way the dataset implied it should.**
  Discovering that only 55 of 5,000 records matched via `Vehicle_ID` meant
  rethinking Tab 3 entirely — from "show the joined data" to "show the
  joined data *and be upfront about its scope*."
- **DRY isn't just about functions — it applies to config, too.**
  Centralizing repeated style logic into the `SLIDER_STYLES` dictionary
  in `style_filters.py` was a direct application of a principle I'd used
  in VBA for years, just expressed through a Python dictionary instead of
  a repeated Sub per control.

## Tech Stack
Python 3 · SQLite (`sqlite3`, standard library) · pandas · Streamlit · Plotly Express

## Project Structure

ev-sales-dashboard/ ├── MainApp.py # Entry point, tab routing ├── tab1_saleRedo.py # Sales Analysis tab ├── tab2_vehicles.py # Vehicle Catalog tab ├── tab3_matched.py # Matched Vehicle Sales tab (JOIN demo) ├── filter_helpers.py # Shared filter-building logic ├── style_filters.py # Centralized, data-driven CSS styling ├── build_database.py # One-time script: CSV → SQLite ingestion ├── ev_data.db ├── data/ │ ├── ev_vehicles.csv │ └── ev_sales.csv └── README.md

## Run Locally

### 1) Clone (or download) the repo
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO_NAME>.git
cd <YOUR_REPO_NAME>

### 2) Install Python dependencies
pip install -r requirements.txt

### 3) Build the SQLite database (one-time, or after updating CSVs)
This project uses `ev_data.db` as its data source. If `ev_data.db` isn’t present (or you changed the CSVs), generate it from the CSVs in the `data/` folder:
python build_database.py

Expected inputs:
- `data/ev_vehicles.csv`
- `data/ev_sales.csv`

Expected output:
- `ev_data.db`

### 4) Start the Streamlit app
streamlit run MainApp.py

Open the local URL shown in your terminal (commonly `http://localhost:8501`).
If you want a specific port (example 8502):
streamlit run MainApp.py --server.port 8502


## What I'd Do Differently
- Validate cross-table key integrity immediately after loading raw data,
  before designing any structure around an assumed relationship
- A five-minute row-count check up front would have caught this before it
  forced a mid-project scope change

## Data Source
Kaggle: *[dataset name/link]* — synthetic/simulated EV data, used to
demonstrate pipeline and dashboard construction, not real-world market
analysis.

## Author
[Your Name] — background in VBA/Excel, building toward Python, SQL, and
data tooling through hands-on portfolio projects.

Coming from VBA turned out to be a better foundation than expected —
including its OOP side, which is more capable than VBA's reputation as a
basic scripting tool would suggest, and honestly kind of fun to work with
once you find it. Class modules and interfaces give VBA real polymorphism,
and while it has no native inheritance, composition and factory patterns
mimic it convincingly (see [Project Name] elsewhere in this portfolio).

What's genuinely new to me in Python is the ecosystem — real package
management, and libraries like pandas and Streamlit — rather than the
underlying logic itself.

Principles like avoiding repeated code, grouping related logic together,
and separating data from the processes that act on it aren't new concepts,
however — they're ones I already employed in VBA; here in Python, they're
just expressed in a language with cleaner syntax to enforce them.





