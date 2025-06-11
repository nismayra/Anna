# NOTE: This script requires Streamlit to run. To test it locally, install it using:
# pip install streamlit
# Then run: streamlit run college_selector_app.py

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed. Please run 'pip install streamlit' in your environment.")

import pandas as pd

# Load datasets
@st.cache_data
def load_data():
    main_df = pd.read_csv("Anna-1CGS - Anna-1CG.csv")
    df_colleges = pd.read_csv("Copy of Anna-1CGS - Col-fi.csv")
    df_branches = pd.read_csv("Copy of Anna-1CGS - Bran-fi.csv")
    df_cities = pd.read_csv("Copy of Anna-1CGS - City-fi.csv", skiprows=2)
    return main_df, df_colleges, df_branches, df_cities

main_df, df_colleges, df_branches, df_cities = load_data()

st.title("🎓 Anna University College Selector")

# --- Filters ---
st.sidebar.header("📍 Filter Options")

# City filter
selected_cities = st.sidebar.multiselect(
    "Select Cities (Districts):",
    options=df_cities['District'].dropna().unique().tolist(),
    default=df_cities[df_cities['Select'].astype(str).str.lower() == 'true']['District'].dropna().tolist()
)

# College filter
available_colleges = df_colleges[df_colleges['Location'].isin(selected_cities)]
selected_colleges = st.sidebar.multiselect(
    "Select Colleges:",
    options=available_colleges['College'].tolist(),
    default=available_colleges[available_colleges['Select'] == True]['College'].tolist()
)

# Branch filter
selected_branches = st.sidebar.multiselect(
    "Select Branches:",
    options=df_branches['Branch Name - Selected 98'].tolist(),
    default=df_branches[df_branches['Select'] == True]['Branch Name - Selected 98'].tolist()
)

# --- Filtering Logic ---
filtered_df = main_df.copy()

# Map college and branch names
college_map = dict(zip(df_colleges['College'], df_colleges['coc']))
branch_map = dict(zip(df_branches['Branch Name - Selected 98'], df_branches['Branch Code']))

if selected_colleges:
    selected_coc = [college_map[col] for col in selected_colleges if col in college_map]
    filtered_df = filtered_df[filtered_df['coc'].isin(selected_coc)]

if selected_branches:
    selected_brc = [branch_map[br] for br in selected_branches if br in branch_map]
    filtered_df = filtered_df[filtered_df['brc'].isin(selected_brc)]

# Add readable names for output
filtered_df = filtered_df.merge(df_colleges[['coc', 'College']], on='coc', how='left')
filtered_df = filtered_df.merge(df_branches[['Branch Code', 'Branch Name - Selected 98']], left_on='brc', right_on='Branch Code', how='left')

# --- Display Result ---
st.subheader("📊 Filtered Colleges")
st.write(f"Total Matches: {len(filtered_df)}")

if not filtered_df.empty:
    st.dataframe(filtered_df[['College', 'Branch Name - Selected 98', 'OC', 'BC', 'MBCV']])
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download CSV", csv, "filtered_colleges.csv")
else:
    st.warning("No colleges match your filters. Please refine your selection.")
