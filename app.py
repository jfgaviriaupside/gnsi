import streamlit as st
import pandas as pd

# Load the data
file_path = 'doctors_gnsi.xlsx'
data_main = pd.read_excel(file_path)  # Load the main dataset containing unique patient information
data_additional = pd.read_excel('Potential Reltaions GNSI ACTUALIZADO.xlsx', sheet_name='Doctor Details')  # Load additional dataset for doctor detail

# Sidebar: App title and description
st.sidebar.title("GNSI Doctor Analysis")  # Set the title for the sidebar
st.sidebar.write("Analyze doctors based on unique patients served, referral growth, and other parameters.")  # Sidebar description

# Tabs for different datasets
tab1, tab2 = st.tabs(["Unique Patients Analysis", "Doctor Details Analysis"])  # Create two tabs for navigating between different analyses

# --- Tab 1: Unique Patients Analysis ---
with tab1:
    # Page Title
    st.title("Referring Doctors Ranking")  # Title for the first tab

    # Convert relevant columns to strings for consistent sorting and display
    data_main['curr dprtmnt'] = data_main['curr dprtmnt'].astype(str)  # Ensure 'curr dprtmnt' column is treated as string
    data_main['ctm role'] = data_main['ctm role'].astype(str)  # Ensure 'ctm role' column is treated as string
    data_main['ctm city'] = data_main['ctm city'].astype(str)  # Ensure 'ctm city' column is treated as string

    # Filter options for Current Department, Role, and City
    st.write("### Filters")  # Subtitle for filter section

    # Dropdown filters
    selected_department = st.selectbox("Select Department", options=['All'] + sorted(data_main['curr dprtmnt'].dropna().unique().tolist()))  # Dropdown to select department
    selected_role = st.selectbox("Select Role", options=['All'] + sorted(data_main['ctm role'].dropna().unique().tolist()))  # Dropdown to select role
    selected_city = st.selectbox("Select City", options=['All'] + sorted(data_main['ctm city'].dropna().unique().tolist()))  # Dropdown to select city

    # Apply filters based on selections
    filtered_data = data_main.copy()  # Start with a copy of the original data
    if selected_department != 'All':
        filtered_data = filtered_data[filtered_data['curr dprtmnt'] == selected_department]  # Filter by selected department if not 'All'
    if selected_role != 'All':
        filtered_data = filtered_data[filtered_data['ctm role'] == selected_role]  # Filter by selected role if not 'All'
    if selected_city != 'All':
        filtered_data = filtered_data[filtered_data['ctm city'] == selected_city]  # Filter by selected city if not 'All'

    # Sort filtered data by 'total unique patients served' in descending order
    filtered_data = filtered_data.sort_values(by='total unique patients served', ascending=False)  # Sort data by unique patients served

    # Display the filtered table with specific columns
    st.write("### Top Doctors by Unique Patients Served")  # Subtitle for the results table
    st.write(
        filtered_data[['ctm name', 'ctm role', 'ctm city', 'total unique patients served', 'CAGR']]  # Select relevant columns to display
        .rename(columns={
            'ctm name': 'Doctor Name',  # Rename columns for better readability
            'ctm role': 'Role', 
            'ctm city': 'City', 
            'total unique patients served': 'Unique Patients', 
            'CAGR': 'CAGR (2023-2024) (%)'
        })
        .style.format({'Unique Patients': '{:.0f}', 'CAGR (%)': '{:.2f}%'})  # Format numeric values for better display
    )

# --- Tab 2: Doctor Details Analysis ---
with tab2:
    # Page Title
    st.title("Potential Market of Doctors")  # Title for the second tab

    # Convert relevant columns to strings for consistent sorting and display
    data_additional['Location'] = data_additional['Location'].astype(str)  # Ensure 'Location' column is treated as string
    data_additional['Specialty'] = data_additional['Specialty'].astype(str)  # Ensure 'Specialty' column is treated as string
    data_additional['Insurance'] = data_additional['Insurance'].astype(str)  # Ensure 'Insurance' column is treated as string

    # Filter options for Location, Specialty, and Insurance
    st.write("### Filters")  # Subtitle for filter section

    # Dropdown filters
    selected_location = st.selectbox("Select Location", options=['All'] + sorted(data_additional['Location'].dropna().unique().tolist()))  # Dropdown to select location
    selected_specialty = st.selectbox("Select Specialty", options=['All'] + sorted(data_additional['Specialty'].dropna().unique().tolist()))  # Dropdown to select specialty
    selected_insurance = st.selectbox("Select Insurance", options=['All'] + sorted(data_additional['Insurance'].dropna().unique().tolist()))  # Dropdown to select insurance

    # Apply filters based on selections
    filtered_data_additional = data_additional.copy()  # Start with a copy of the original data
    if selected_location != 'All':
        filtered_data_additional = filtered_data_additional[filtered_data_additional['Location'] == selected_location]  # Filter by selected location if not 'All'
    if selected_specialty != 'All':
        filtered_data_additional = filtered_data_additional[filtered_data_additional['Specialty'] == selected_specialty]  # Filter by selected specialty if not 'All'
    if selected_insurance != 'All':
        filtered_data_additional = filtered_data_additional[filtered_data_additional['Insurance'] == selected_insurance]  # Filter by selected insurance if not 'All'

    # Display the filtered table with specific columns
    st.write("### Filtered Doctor Details")  # Subtitle for the results table
    st.write(
        filtered_data_additional[['Doctor', 'Specialty', 'Location', 'Insurance', 'Number', 'Address', 'Postal Code']]  # Select relevant columns to display
        .rename(columns={
            'Doctor': 'Doctor Name',  # Rename columns for better readability
            'Insurance': 'Insurance',
            'Specialty': 'Specialty', 
            'Location': 'Location',  
            'Number': 'Contact Number',
            'Address': 'Address',
            'Postal Code': 'Postal Code'
        })
    )
