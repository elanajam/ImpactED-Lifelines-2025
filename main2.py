import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Function to create a map
def create_map(school_data):
    m = folium.Map(location=[31.7917, 7.0926], zoom_start=5)
    for school in school_data:
        folium.Marker(
            [school["lat"], school["lon"]],
            popup=(
                f"<b>{school['name']}</b><br>"
                f"City: {school['city']}<br>"
                f"Status: {school['status']}<br>"
                f"Displaced Students: {school['displaced_students']}<br>"
                f"Resources Needed: Teachers ({school['resources']['teachers']})<br>"
                f"Delivery Status: {school['resources']['status']}"
            ),
            icon=folium.Icon(
                color="red" if school["status"] == "Severely Damaged" else "orange"
            ),
        ).add_to(m)
    return m


# Sidebar input for adding a new school
st.sidebar.header("Add a New School")
school_name = st.sidebar.text_input("School Name", value="New School")
latitude = st.sidebar.number_input("Latitude", value=31.7917, format="%.6f")
longitude = st.sidebar.number_input("Longitude", value=7.0926, format="%.6f")
city = st.sidebar.text_input("City", value="Unknown")
status = st.sidebar.selectbox(
    "Damage Status", ["Severely Damaged", "Moderately Damaged", "Minor Damage"]
)
displaced_students = st.sidebar.number_input("Displaced Students", value=0, min_value=0)
teachers_needed = st.sidebar.number_input("Temporary Teachers Needed", value=0, min_value=0)
schools_needed = st.sidebar.number_input("Temporary Schools Needed", value=0, min_value=0)
stationery_kits_needed = st.sidebar.number_input(
    "Stationery Kits Needed", value=0, min_value=0
)
delivery_status = st.sidebar.selectbox(
    "Delivery Status", ["Not Delivered", "Being Delivered", "Delivered"]
)
estimated_loss = st.sidebar.number_input("Estimated Loss (in USD)", value=100000, min_value=0)
current_spending = st.sidebar.number_input("Current Spending (in USD)", value=0, min_value=0)

add_school = st.sidebar.button("Add School")

# Initialize session state
if "schools" not in st.session_state:
    st.session_state.schools = []

# Add school to session state
if add_school:
    st.session_state.schools.append(
        {
            "name": school_name,
            "lat": latitude,
            "lon": longitude,
            "city": city,
            "status": status,
            "displaced_students": displaced_students,
            "resources": {
                "teachers": teachers_needed,
                "schools": schools_needed,
                "stationery_kits": stationery_kits_needed,
                "status": delivery_status,
            },
            "estimated_loss": estimated_loss,
            "current_spending": current_spending,
        }
    )

# Create and display the map
m = create_map(st.session_state.schools)
st_folium(m, width=700, height=500)

# Dashboard button
if st.button("Open Dashboard"):
    st.header("Schools Dashboard")
    
    # Create a DataFrame from session state data
    if st.session_state.schools:
        school_df = pd.DataFrame(
            [
                {
                    "School Name": school["name"],
                    "City": school["city"],
                    "Damage Status": school["status"],
                    "Displaced Students": school["displaced_students"],
                    "Temporary Teachers": school["resources"]["teachers"],
                    "Temporary Schools": school["resources"]["schools"],
                    "Stationery Kits": school["resources"]["stationery_kits"],
                    "Delivery Status": school["resources"]["status"],
                    "Estimated Loss (USD)": school["estimated_loss"],
                    "Current Spending (USD)": school["current_spending"],
                }
                for school in st.session_state.schools
            ]
        )

        # Ensure columns for sorting are numerical
        school_df["Displaced Students"] = pd.to_numeric(school_df["Displaced Students"], errors="coerce")
        school_df["Temporary Teachers"] = pd.to_numeric(school_df["Temporary Teachers"], errors="coerce")
        school_df["Temporary Schools"] = pd.to_numeric(school_df["Temporary Schools"], errors="coerce")
        school_df["Stationery Kits"] = pd.to_numeric(school_df["Stationery Kits"], errors="coerce")
        school_df["Estimated Loss (USD)"] = pd.to_numeric(school_df["Estimated Loss (USD)"], errors="coerce")
        school_df["Current Spending (USD)"] = pd.to_numeric(school_df["Current Spending (USD)"], errors="coerce")

        # Filters
        st.subheader("Filters")
        city_filter = st.multiselect(
            "Filter by City", options=school_df["City"].unique(), default=school_df["City"].unique()
        )
        damage_filter = st.multiselect(
            "Filter by Damage Status",
            options=school_df["Damage Status"].unique(),
            default=school_df["Damage Status"].unique(),
        )

        # Apply filters
        filtered_df = school_df[
            (school_df["City"].isin(city_filter)) & (school_df["Damage Status"].isin(damage_filter))
        ]

        # Sorting
        st.subheader("Sort Schools")
        sort_by = st.selectbox(
            "Sort By",
            options=["School Name", "City", "Damage Status", "Displaced Students", "Temporary Teachers", "Temporary Schools", "Stationery Kits", "Estimated Loss (USD)", "Current Spending (USD)"],
            index=0,
        )
        sort_ascending = st.checkbox("Sort in Ascending Order", value=True)
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_ascending)

        # Display the table
        st.dataframe(filtered_df)

        # Budget Overview
        st.subheader("Budget Overview")
        total_budget = 1000000  # Example budget (in USD)
        st.markdown(f"**Total Budget for Rebuilding:** ${total_budget:,}")
        
        st.subheader("Budget Status for Each School")
        
        for index, row in filtered_df.iterrows():
            overspend = "Might be overspending" if row["Current Spending (USD)"] > row["Estimated Loss (USD)"] else ""
            underspend = "Might be underspending" if row["Current Spending (USD)"] < row["Estimated Loss (USD)"] else ""
            st.markdown(f"**{row['School Name']}**")
            st.markdown(f"Estimated Loss: ${row['Estimated Loss (USD)']:,}")
            st.markdown(f"Current Spending: ${row['Current Spending (USD)']:,}")
            if overspend:
                st.markdown(f"*{overspend}*")
            if underspend:
                st.markdown(f"*{underspend}*")
            st.markdown("---")

        # Summary
        st.subheader("Summary")
        total_displaced_students = filtered_df["Displaced Students"].sum()
        total_teachers_needed = filtered_df["Temporary Teachers"].sum()
        total_schools_needed = filtered_df["Temporary Schools"].sum()
        total_stationery_kits_needed = filtered_df["Stationery Kits"].sum()

        st.markdown(f"**Total Displaced Students:** {total_displaced_students}")
        st.markdown(f"**Total Temporary Teachers Needed:** {total_teachers_needed}")
        st.markdown(f"**Total Temporary Schools Needed:** {total_schools_needed}")
        st.markdown(f"**Total Stationery Kits Needed:** {total_stationery_kits_needed}")

        # Delivery Status Summary
        st.subheader("Delivery Status")
        delivery_status_counts = filtered_df["Delivery Status"].value_counts()
        for status, count in delivery_status_counts.items():
            color = (
                "green" if status == "Delivered" else "yellow" if status == "Being Delivered" else "red"
            )
            st.markdown(f"<span style='color:{color};'>{status}: {count}</span>", unsafe_allow_html=True)

    else:
        st.write("No schools added yet.")
