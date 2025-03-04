import streamlit as st
import pandas as pd
from google.cloud import bigquery
import os

# Set up Google Cloud credentials
from google.oauth2 import service_account

# Initialize BigQuery client with credentials from Streamlit secrets
# Convert the private key string to proper format
credentials_info = st.secrets["gcp_service_account"]
credentials_info["private_key"] = credentials_info["private_key"].replace('\\n', '\n')

bigquery_credentials = service_account.Credentials.from_service_account_info(
    credentials_info
)

# Initialize BigQuery client
bigquery_client = bigquery.Client(
    credentials=bigquery_credentials,
    project=st.secrets["gcp_service_account"]["project_id"]
)

# Set page title
st.title('Traffic Accident Analysis Dashboard')

# Query data from BigQuery
@st.cache_data
def fetch_data():
    try:
        query = """
        SELECT *
        FROM `cmpe255-451700.crash2025.crash`
        LIMIT 1000
        """
        
        df = bigquery_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f'Error fetching data: {str(e)}')
        return pd.DataFrame()

# Load the data
df = fetch_data()

if not df.empty:
    # Sidebar filters
    st.sidebar.header('Filters')
    
    # Age Range filter
    # Filter out None/null values and sort age ranges
    valid_age_ranges = df['AGERANGE'].dropna().unique().tolist()
    age_ranges = ['All'] + sorted(valid_age_ranges)
    selected_age_range = st.sidebar.selectbox('Age Range', age_ranges)
    
    # Day Number filter
    day_numbers = ['All'] + sorted(df['DAYNUMBER'].unique().tolist())
    selected_day = st.sidebar.selectbox('Day Number', day_numbers)
    
    # Chart type selector
    chart_type = st.sidebar.selectbox(
        'Chart Type',
        ['Bar Chart', 'Line Chart']
    )
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_age_range != 'All':
        filtered_df = filtered_df[filtered_df['AGERANGE'] == selected_age_range]
    if selected_day != 'All':
        filtered_df = filtered_df[filtered_df['DAYNUMBER'] == selected_day]
    
    # Display charts
    st.subheader('Accident Distribution by Age Range')
    
    # Prepare data for visualization
    age_distribution = df['AGERANGE'].value_counts().reset_index()
    age_distribution.columns = ['Age Range', 'Count']
    
    # Create visualization based on selected chart type
    if chart_type == 'Bar Chart':
        st.bar_chart(age_distribution.set_index('Age Range'))
    else:
        st.line_chart(age_distribution.set_index('Age Range'))
    
    # Display filtered data table
    st.subheader('Filtered Data')
    st.dataframe(filtered_df)
else:
    st.warning('No data available to display')

    