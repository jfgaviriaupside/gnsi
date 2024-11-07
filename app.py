import streamlit as st
import pandas as pd

# Load the data
file_path = 'doctors_gnsi.xlsx'
data = pd.read_excel(file_path)

# Sidebar: App title and description
st.sidebar.title("GNSI Doctor Analysis")
st.sidebar.write("Analyze doctors based on unique patients served and referral growth.")

# Page Title
st.title("Doctors Ranked by Total Unique Patients Served")

# Convert relevant columns to strings for consistent sorting and display
data['curr dprtmnt'] = data['curr dprtmnt'].astype(str)
data['ctm role'] = data['ctm role'].astype(str)
data['ctm city'] = data['ctm city'].astype(str)

# Filter options for Current Department, Role, and City
st.write("### Filters")

# Dropdown filters
selected_department = st.selectbox("Select Department", options=['All'] + sorted(data['curr dprtmnt'].dropna().unique().tolist()))
selected_role = st.selectbox("Select Role", options=['All'] + sorted(data['ctm role'].dropna().unique().tolist()))
selected_city = st.selectbox("Select City", options=['All'] + sorted(data['ctm city'].dropna().unique().tolist()))

# Apply filters based on selections
filtered_data = data.copy()
if selected_department != 'All':
    filtered_data = filtered_data[filtered_data['curr dprtmnt'] == selected_department]
if selected_role != 'All':
    filtered_data = filtered_data[filtered_data['ctm role'] == selected_role]
if selected_city != 'All':
    filtered_data = filtered_data[filtered_data['ctm city'] == selected_city]

# Sort filtered data by 'total unique patients served' in descending order
filtered_data = filtered_data.sort_values(by='total unique patients served', ascending=False)

# Display the filtered table with specific columns
st.write("### Top Doctors by Unique Patients Served")
st.write(
    filtered_data[['ctm name', 'ctm role', 'ctm city', 'total unique patients served', 'CAGR']]
    .rename(columns={
        'ctm name': 'Doctor Name', 
        'ctm role': 'Role', 
        'ctm city': 'City', 
        'total unique patients served': 'Unique Patients', 
        'CAGR': 'CAGR (2023-2024) (%)'
    })
    .style.format({'Unique Patients': '{:.0f}', 'CAGR (%)': '{:.2f}%'})
)

# Search and dropdown selection for doctor lookup
st.write("### Search for a Doctor")
search_query = st.text_input("Start typing a doctor name to search:")
matching_doctors = data[data['ctm name'].str.contains(search_query, case=False, na=False)]

# Dropdown with matching doctor names
if not matching_doctors.empty:
    selected_doctor = st.selectbox("Select a doctor", matching_doctors['ctm name'].unique())
else:
    selected_doctor = None

# Display detailed information for the selected doctor in text format
if selected_doctor:
    doctor_data = data[data['ctm name'] == selected_doctor].iloc[0]
    
    st.write(f"### Details for {selected_doctor}")
    st.write(f"**Address:** {doctor_data['ctm addr']} {doctor_data['ctm addr 2']}")
    st.write(f"**Phone:** {doctor_data['ctm phone']}")
    st.write(f"**Fax:** {doctor_data['ctm fax']}")
    st.write(f"**Current Department:** {doctor_data['curr dprtmnt']}")
    st.write(f"**Role:** {doctor_data['ctm role']}")
    st.write(f"**City:** {doctor_data['ctm city']}")
    st.write(f"**ZIP:** {doctor_data['ctm zip']}")
    st.write(f"**Unique Patients Served:** {doctor_data['total unique patients served']}")
    st.write(f"**CAGR (%):** {doctor_data['CAGR']:.2f}%")
