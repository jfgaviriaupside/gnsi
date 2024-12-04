import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from dataclasses import dataclass
from typing import Tuple, List
import math
import json

@dataclass
class GNSILocation:
    name: str
    coordinates: Tuple[float, float]

    def distance_to(self, lat: float, lon: float) -> float:
        """Calculate distance in miles to given coordinates using Haversine formula"""
        R = 3959.87433  # Earth's radius in miles

        lat1, lon1 = self.coordinates
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat), math.radians(lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

# Define GNSI locations
GNSI_LOCATIONS = [
    GNSILocation("GNSI Plantation", (26.127846, -80.249504)),
    GNSILocation("GNSI Atlantis", (26.601933, -80.090660)),
    GNSILocation("GNSI Jensen Beach", (27.2573016, -80.2802879)),
    GNSILocation("GNSI Fort Pierce", (27.430028, -80.347494)),
    GNSILocation("GNSI Palm Bay", (28.0192676, -80.6205719)),
    GNSILocation("GNSI Winter Park", (28.59372, -81.286417)),
    GNSILocation("GNSI Orlando", (28.512038, -81.370154))
]

def find_nearest_location(lat: float, lon: float) -> GNSILocation:
    """Find the nearest GNSI location to given coordinates"""
    return min(GNSI_LOCATIONS, key=lambda loc: loc.distance_to(lat, lon))

def create_base_map(center_lat: float, center_lon: float, zoom: int = 9) -> folium.Map:
    """Create a base map with all GNSI locations marked"""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)
    
    # Add GNSI locations
    for loc in GNSI_LOCATIONS:
        folium.Marker(
            loc.coordinates,
            popup=loc.name,
            icon=folium.Icon(color='red', icon='plus', prefix='fa'),
        ).add_to(m)
    
    return m

# Load the data
file_path = 'doctors_gnsi.xlsx'
try:
    data_main = pd.read_excel(file_path)  # Load the main dataset containing unique patient information
except FileNotFoundError:
    st.error("The main dataset file was not found. Please check the file path.")
    data_main = pd.DataFrame()

try:
    data_additional = pd.read_excel('potential_doctors_database.xlsx', sheet_name='Sheet1')  # Load additional dataset for doctor details
except FileNotFoundError:
    st.error("The additional dataset file was not found. Please check the file path.")
    data_additional = pd.DataFrame()

# Sidebar: App title and description
st.sidebar.title("GNSI Doctor Analysis")  # Set the title for the sidebar
st.sidebar.write("Analyze doctors based on unique patients served, referral growth, and other parameters.")  # Sidebar description

# Tabs for different datasets
tab1, tab2, tab3 = st.tabs(["Referring Doctors Ranking", "Potential Market of Doctors", "Geographic Analysis"])  # Create two tabs for navigating between different analyses

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
                'Location': 'City',  
                'Number': 'Contact Numbers',
                'Address': 'Addresses',
            })
        )

        # Search functionality for doctor details
        st.write("### Search for a Doctor")  # Subtitle for search section
        search_query = st.text_input("Enter the doctor's name to search:")  # Input field for doctor name search
        if search_query:
            matching_doctors = aggregated_data[aggregated_data['Doctor'].str.contains(search_query, case=False, na=False)]
            if not matching_doctors.empty:
                selected_doctor = st.selectbox("Select a doctor", matching_doctors['Doctor'].unique())
                if selected_doctor:
                    doctor_data = matching_doctors[matching_doctors['Doctor'] == selected_doctor].iloc[0]
                    
                    # Display doctor details
                    st.write(f"### Details for {selected_doctor}")
                    st.write(f"**Contact Numbers:** {doctor_data['Number']}")
                    st.write(f"**Addresses:** {doctor_data['Address']}")
                    st.write(f"**Specialty:** {doctor_data['Specialty']}")
                    st.write(f"**Location:** {doctor_data['Location']}")
                    st.write(f"**Insurance:** {doctor_data['Insurance']}")
                    
                    # Get doctor's coordinates from the original dataset
                    doctor_coords = data_additional[
                        data_additional['Doctor'] == selected_doctor
                    ][['Latitude', 'Longitude']].iloc[0]
                    
                    if not pd.isna(doctor_coords['Latitude']) and not pd.isna(doctor_coords['Longitude']):
                        # Create map centered on doctor's location
                        m = create_base_map(doctor_coords['Latitude'], doctor_coords['Longitude'])
                        
                        # Add doctor's marker
                        folium.Marker(
                            [doctor_coords['Latitude'], doctor_coords['Longitude']],
                            popup=selected_doctor,
                            icon=folium.Icon(color='blue', icon='user-md', prefix='fa')
                        ).add_to(m)
                        
                        # Find and highlight nearest GNSI location
                        nearest = find_nearest_location(doctor_coords['Latitude'], doctor_coords['Longitude'])
                        folium.PolyLine(
                            locations=[
                                [doctor_coords['Latitude'], doctor_coords['Longitude']],
                                nearest.coordinates
                            ],
                            weight=2,
                            color='red',
                            opacity=0.8
                        ).add_to(m)
                        
                        # Display map
                        st.write("### Location Map")
                        st_folium(m)
                        
                        # Display distance to nearest location
                        distance = nearest.distance_to(doctor_coords['Latitude'], doctor_coords['Longitude'])
                        st.write(f"**Nearest GNSI Location:** {nearest.name} ({distance:.1f} miles)")
                    else:
                        st.warning("No location data available for this doctor")
            else:
                st.write("No matching doctors found.")  # Message if no doctors match the search query
    else:
        st.error("The required columns are missing in the additional dataset.")

# --- Tab 3: Geographic Analysis ---
with tab3:
    st.title("Geographic Analysis")
    
    viz_mode = st.radio(
        "Select Visualization Mode",
        ["Individual Doctor Locations"]  # Removed "Doctors per ZIP Code"
    )
    
    selected_gnsi = st.selectbox(
        "Select GNSI Location",
        [loc.name for loc in GNSI_LOCATIONS]
    )
    selected_loc = next(loc for loc in GNSI_LOCATIONS if loc.name == selected_gnsi)
    
    if viz_mode == "Individual Doctor Locations":
        m = create_base_map(selected_loc.coordinates[0], selected_loc.coordinates[1])
        
        radius = st.slider("Radius (miles)", 5, 100, 25)
        doctors_in_radius = []  # Changed to a list to store doctor information
        
        for _, doctor in data_additional.iterrows():
            if not pd.isna(doctor['Latitude']) and not pd.isna(doctor['Longitude']):
                dist = selected_loc.distance_to(doctor['Latitude'], doctor['Longitude'])
                if dist <= radius:
                    doctor_info = {
                        'Doctor': doctor['Doctor'],
                        'Number': doctor['Number'],
                        'Address': doctor['Address'],
                        'Distance (miles)': dist  # Calculate and store distance
                    }
                    doctors_in_radius.append(doctor_info)  # Store doctor information
        
        folium.Circle(
            selected_loc.coordinates,
            radius=radius * 1609.34,  # Convert miles to meters
            color='red',
            fill=True,
            opacity=0.2
        ).add_to(m)
        
        st_folium(m)
        st.write(f"**Total Doctors within {radius} miles:** {len(doctors_in_radius)}")  # Count of doctors
        
        # Display contact information table for doctors in radius
        if doctors_in_radius:
            contact_info_df = pd.DataFrame(doctors_in_radius)  # Create DataFrame from the list
            st.write("### Contact Information of Doctors in Radius")
            st.write(contact_info_df)  # Display relevant columns including distance
        else:
            st.write("No doctors found within the selected radius.")