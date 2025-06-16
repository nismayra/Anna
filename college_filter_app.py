# NOTE: This script requires Streamlit to run. To test it locally, install it using:
# pip install streamlit streamlit-aggrid
# Then run: streamlit run college_selector_app.py

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed. Please run 'pip install streamlit' in your environment.")

import pandas as pd
import os
import json

try:
    from st_aggrid import AgGrid, GridOptionsBuilder
except ModuleNotFoundError:
    os.system("pip install streamlit-aggrid")
    from st_aggrid import AgGrid, GridOptionsBuilder

# Load datasets
@st.cache_data
def load_data():
    main_df = pd.read_csv("Anna-1CGS - Anna-1CG.csv")
    df_colleges = pd.read_csv("Copy of Anna-1CGS - Col-fi.csv")
    df_branches = pd.read_csv("Copy of Anna-1CGS - Bran-fi.csv")
    df_cities = pd.read_csv("Copy of Anna-1CGS - City-fi.csv", skiprows=2)
    return main_df, df_colleges, df_branches, df_cities

main_df, df_colleges, df_branches, df_cities = load_data()

# Ask for user ID and prepare preference file path
user_id = st.sidebar.text_input("Enter your name or ID to load/save preferences:", value="default")
PREF_FILE = f"user_filters_{user_id}.json"

def load_preferences(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_preferences(file_path, prefs):
    with open(file_path, "w") as f:
        json.dump(prefs, f)

user_prefs = load_preferences(PREF_FILE)

st.title("🎓 Anna University College Selector")

# --- Sidebar Filters ---
st.sidebar.header("📍 Filter Options")

# --- City Selection ---
st.sidebar.subheader("🏙️ Select Cities")
city_names = df_cities['District'].dropna().unique().tolist()
def_cities = user_prefs.get("cities", [])
selected_city_names = st.sidebar.multiselect("Choose cities:", city_names, default=def_cities)

if selected_city_names:
    editable_city_df = df_cities[df_cities['District'].isin(selected_city_names)][['District', 'Weight']].copy()
    city_gb = GridOptionsBuilder.from_dataframe(editable_city_df)
    city_gb.configure_column("Weight", editable=True)
    city_table = AgGrid(
        editable_city_df,
        gridOptions=city_gb.build(),
        theme="streamlit",
        update_mode="MANUAL",
        height=200,
        fit_columns_on_grid_load=True,
    )
else:
    city_table = {"data": pd.DataFrame()}

# --- Branch Selection ---
st.sidebar.subheader("🛠️ Select Branches")
branch_names = df_branches['Branch Name - Selected 98'].dropna().tolist()
def_branches = user_prefs.get("branches", [])
selected_branch_names = st.sidebar.multiselect("Choose branches:", branch_names, default=def_branches)

if selected_branch_names:
    editable_branch_df = df_branches[df_branches['Branch Name - Selected 98'].isin(selected_branch_names)][['Branch Name - Selected 98', 'Weight']].copy()
    branch_gb = GridOptionsBuilder.from_dataframe(editable_branch_df)
    branch_gb.configure_column("Weight", editable=True)
    branch_table = AgGrid(
        editable_branch_df,
        gridOptions=branch_gb.build(),
        theme="streamlit",
        update_mode="MANUAL",
        height=200,
        fit_columns_on_grid_load=True,
    )
else:
    branch_table = {"data": pd.DataFrame()}

# --- College Selection ---
st.sidebar.subheader("🏫 Select Colleges")
college_names = df_colleges['College'].dropna().tolist()
def_colleges = user_prefs.get("colleges", [])
selected_college_names = st.sidebar.multiselect("Choose colleges:", college_names, default=def_colleges)

if selected_college_names:
    editable_college_df = df_colleges[df_colleges['College'].isin(selected_college_names)][['College', 'Weight']].copy()
    college_gb = GridOptionsBuilder.from_dataframe(editable_college_df)
    college_gb.configure_column("Weight", editable=True)
    college_table = AgGrid(
        editable_college_df,
        gridOptions=college_gb.build(),
        theme="streamlit",
        update_mode="MANUAL",
        height=200,
        fit_columns_on_grid_load=True,
    )
else:
    college_table = {"data": pd.DataFrame()}

if st.sidebar.button("💾 Save My Filter Preferences"):
    save_preferences(PREF_FILE, {
        "cities": selected_city_names,
        "branches": selected_branch_names,
        "colleges": selected_college_names
    })
    st.sidebar.success("Preferences saved!")

# --- Filtering Logic ---
filtered_df = main_df.copy()

# Filter by selected cities
if selected_city_names:
    city_college_codes = df_colleges[df_colleges['Location'].isin(selected_city_names)]['coc'].unique()
    filtered_df = filtered_df[filtered_df['coc'].isin(city_college_codes)]

# Apply branch filter only if branches are selected
if selected_branch_names:
    branch_map = dict(zip(df_branches['Branch Name - Selected 98'], df_branches['Branch Code']))
    selected_brc = [branch_map[br] for br in selected_branch_names if br in branch_map]
    filtered_df = filtered_df[filtered_df['brc'].isin(selected_brc)]

# Apply college filter only if colleges are selected
if selected_college_names:
    college_map = dict(zip(df_colleges['College'], df_colleges['coc']))
    selected_coc = [college_map[col] for col in selected_college_names if col in college_map]
    filtered_df = filtered_df[filtered_df['coc'].isin(selected_coc)]

# Add readable names for output
filtered_df = filtered_df.merge(df_colleges[['coc', 'College', 'Location']], on='coc', how='left')
filtered_df = filtered_df.merge(df_branches[['Branch Code', 'Branch Name - Selected 98']], left_on='brc', right_on='Branch Code', how='left')

# --- Display Result ---
st.subheader("📊 Filtered Colleges")
st.write(f"Total Matches: {len(filtered_df)}")

display_columns = [col for col in ['College', 'Location', 'Branch Name - Selected 98', 'OC', 'BC', 'MBCV'] if col in filtered_df.columns]

if not filtered_df.empty:
    gb = GridOptionsBuilder.from_dataframe(filtered_df[display_columns])
    gb.configure_default_column(sortable=True, filter=True, resizable=True)
    gridOptions = gb.build()

    AgGrid(
        filtered_df[display_columns],
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True
    )
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "filtered_colleges.csv")
else:
    st.warning("No colleges match your filters. Please refine your selection.")
