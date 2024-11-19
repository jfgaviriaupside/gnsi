import streamlit as st
import pandas as pd

# Load the data
file_path = 'doctors_gnsi.xlsx'
try:
    data_main = pd.read_excel(file_path)  # Load the main dataset containing unique patient information
except FileNotFoundError:
    st.error("The main dataset file was not found. Please check the file path.")
    data_main = pd.DataFrame()

try:
    data_additional = pd.read_excel('Potential Reltaions GNSI ACTUALIZADO.xlsx', sheet_name='Doctor Details')  # Load additional dataset for doctor details
except FileNotFoundError:
    st.error("The additional dataset file was not found. Please check the file path.")
    data_additional = pd.DataFrame()

# Sidebar: App title and description
st.sidebar.title("GNSI Doctor Analysis")  # Set the title for the sidebar
st.sidebar.write("Analyze doctors based on unique patients served, referral growth, and other parameters.")  # Sidebar description

# Tabs for different datasets
tab1, tab2 = st.tabs(["Referring Doctors Ranking", "Potential Market of Doctors"])  # Create two tabs for navigating between different analyses

# --- Tab 1: Unique Patients Analysis ---
with tab1:
    # Page Title
    st.title("Referring Doctors Ranking")  # Title for the first tab

    # Add search functionality at the top
    st.write("### Search for a Doctor")
    search_query = st.text_input("Enter the doctor's name to search:", key="tab1_search")
    if search_query:
        matching_doctors = data_main[data_main['ctm name'].str.contains(search_query, case=False, na=False)]
        if not matching_doctors.empty:
            selected_doctor = st.selectbox("Select a doctor", matching_doctors['ctm name'].unique(), key="tab1_doctor_select")
            if selected_doctor:
                doctor_data = matching_doctors[matching_doctors['ctm name'] == selected_doctor].iloc[0]
                st.write(f"### Details for {selected_doctor}")
                st.write(f"**Address:** {doctor_data['ctm addr']}")
                st.write(f"**Specialty:** {doctor_data['ctm role']}")
                st.write(f"**Department:** {doctor_data['curr dprtmnt']}")
                st.write(f"**Phone:** {doctor_data.get('ctm phone', 'N/A')}")  # Add if column exists
                st.write(f"**Fax:** {doctor_data.get('ctm fax', 'N/A')}")      # Add if column exists
                st.write(f"**City:** {doctor_data['ctm city']}")
                st.write(f"**Zip Code:** {doctor_data.get('ctm zip', 'N/A')}")  # Add if column exists

    # Check if the required columns are present
    required_columns_main = ['curr dprtmnt', 'ctm role', 'ctm city', 'ctm name', 'total unique patients served', 'CAGR']
    if all(col in data_main.columns for col in required_columns_main):
        # Convert relevant columns to strings for consistent sorting and display
        data_main['curr dprtmnt'] = data_main['curr dprtmnt'].astype(str)  # Ensure 'curr dprtmnt' column is treated as string
        data_main['ctm role'] = data_main['ctm role'].astype(str)  # Ensure 'ctm role' column is treated as string
        data_main['ctm city'] = data_main['ctm city'].astype(str)  # Ensure 'ctm city' column is treated as string

        # Filter options for Current Department, Role, and City
        st.write("### Filters")  # Subtitle for filter section

        # Dropdown filters
        selected_department = st.selectbox("Select Location", options=['All'] + sorted(data_main['curr dprtmnt'].dropna().unique().tolist()))  # Dropdown to select location
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
            filtered_data[['ctm name', 'ctm role', 'ctm city', 'total unique patients served', 'CAGR', 'curr dprtmnt']]  # Added 'curr dprtmnt'
            .rename(columns={
                'ctm name': 'Doctor Name',
                'ctm role': 'Role', 
                'ctm city': 'City', 
                'total unique patients served': 'Unique Patients', 
                'CAGR': 'CAGR (2023-2024) (%)',
                'curr dprtmnt': 'Address'  # Added new column rename
            })
            .style.format({'Unique Patients': '{:.0f}', 'CAGR (%)': '{:.2f}%'})
        )
    else:
        st.error("The required columns are missing in the main dataset.")

# --- Tab 2: Doctor Details Analysis ---
with tab2:
    # Page Title
    st.title("Potential Market of Doctors")  # Title for the second tab

    # Check if the required columns are present
    required_columns_additional = ['Doctor', 'Location', 'Specialty', 'Insurance', 'Number', 'Address']
    if all(col in data_additional.columns for col in required_columns_additional):
        # Convert relevant columns to strings for consistent sorting and display
        data_additional['Location'] = data_additional['Location'].astype(str)  # Ensure 'Location' column is treated as string
        data_additional['Specialty'] = data_additional['Specialty'].astype(str)  # Ensure 'Specialty' column is treated as string
        data_additional['Insurance'] = data_additional['Insurance'].astype(str)  # Ensure 'Insurance' column is treated as string
        data_additional['Number'] = data_additional['Number'].astype(str)  # Ensure 'Number' column is treated as string
        data_additional['Address'] = data_additional['Address'].astype(str)  # Ensure 'Address' column is treated as string

        # Group data by doctor name and aggregate columns
        aggregated_data = data_additional.groupby('Doctor').agg({
            'Insurance': lambda x: ', '.join(sorted(x.unique())),
            'Location': lambda x: ', '.join(sorted(x.unique())),
            'Specialty': lambda x: ', '.join(sorted(x.unique())),
            'Number': lambda x: ', '.join(sorted(x.unique())),  # Aggregate all phone numbers
            'Address': lambda x: ', '.join(sorted(x.unique())),  # Aggregate all addresses
        }).reset_index()

        # Filter options for Location, Specialty, and Insurance
        st.write("### Filters")  # Subtitle for filter section

        # Dropdown filters
        selected_location = st.selectbox("Select City", options=['All'] + sorted(data_additional['Location'].dropna().unique().tolist()))  # Dropdown to select location
        selected_specialty = st.selectbox("Select Specialty", options=['All'] + sorted(data_additional['Specialty'].dropna().unique().tolist()))  # Dropdown to select specialty
        selected_insurance = st.selectbox("Select Insurance", options=['All'] + sorted(data_additional['Insurance'].dropna().unique().tolist()))  # Dropdown to select insurance

        # Apply filters based on selections
        filtered_data_aggregated = aggregated_data.copy()  # Start with a copy of the aggregated data
        if selected_location != 'All':
            filtered_data_aggregated = filtered_data_aggregated[filtered_data_aggregated['Location'].str.contains(selected_location, case=False, na=False)]  # Filter by selected location if not 'All'
        if selected_specialty != 'All':
            filtered_data_aggregated = filtered_data_aggregated[filtered_data_aggregated['Specialty'].str.contains(selected_specialty, case=False, na=False)]  # Filter by selected specialty if not 'All'
        if selected_insurance != 'All':
            filtered_data_aggregated = filtered_data_aggregated[filtered_data_aggregated['Insurance'].str.contains(selected_insurance, case=False, na=False)]  # Filter by selected insurance if not 'All'

        # Display the filtered table with specific columns
        st.write("### Filtered Doctor Details")  # Subtitle for the results table
        st.write(
            filtered_data_aggregated[['Doctor', 'Specialty', 'Location', 'Insurance', 'Number', 'Address']]  # Select relevant columns to display
            .rename(columns={
                'Doctor': 'Doctor Name',  # Rename columns for better readability
                'Insurance': 'Insurance',
                'Specialty': 'Specialty', 
                'Location': 'Location',  
                'Number': 'Contact Numbers',
                'Address': 'Addresses',
            })
        )

        # Search functionality for doctor details
        st.write("### Search for a Doctor")  # Subtitle for search section
        search_query = st.text_input("Enter the doctor's name to search:")  # Input field for doctor name search
        if search_query:
            matching_doctors = aggregated_data[aggregated_data['Doctor'].str.contains(search_query, case=False, na=False)]  # Search for matching doctor names
            if not matching_doctors.empty:
                selected_doctor = st.selectbox("Select a doctor", matching_doctors['Doctor'].unique())  # Dropdown with matching doctor names
                if selected_doctor:
                    doctor_data = matching_doctors[matching_doctors['Doctor'] == selected_doctor].iloc[0]  # Get the data for the selected doctor
                    st.write(f"### Details for {selected_doctor}")  # Display details for the selected doctor
                    st.write(f"**Contact Numbers:** {doctor_data['Number']}")
                    st.write(f"**Addresses:** {doctor_data['Address']}")
                    st.write(f"**Specialty:** {doctor_data['Specialty']}")
                    st.write(f"**Location:** {doctor_data['Location']}")
                    st.write(f"**Insurance:** {doctor_data['Insurance']}")
            else:
                st.write("No matching doctors found.")  # Message if no doctors match the search query
    else:
        st.error("The required columns are missing in the additional dataset.")
