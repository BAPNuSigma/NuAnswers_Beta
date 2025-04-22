import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="NuAnswers Statistics",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 NuAnswers Statistics Dashboard")

# Admin authentication
admin_password = os.environ.get("ADMIN_PASSWORD") or st.secrets.get("ADMIN_PASSWORD")

if not admin_password:
    st.error("Admin password not configured. Please set ADMIN_PASSWORD in environment variables or secrets.toml")
    st.stop()

# Password protection
entered_password = st.sidebar.text_input("Enter Admin Password", type="password")

if entered_password != admin_password:
    st.error("❌ Please enter the correct admin password to view statistics")
    st.stop()

st.sidebar.success("✅ Admin access granted!")

try:
    # Load data
    csv_path = "registration_data.csv"
    if not os.path.exists(csv_path):
        st.info("No registration data available yet.")
        st.stop()
        
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registrations", len(df))
    with col2:
        st.metric("Total Usage Time (hrs)", f"{df['usage_time_minutes'].sum() / 60:.1f}")
    with col3:
        st.metric("Avg. Session Length (min)", f"{df['usage_time_minutes'].mean():.1f}")
    with col4:
        st.metric("Unique Students", df['student_id'].nunique())
    
    # Time-based Analysis
    st.subheader("📈 Usage Trends")
    
    tab1, tab2 = st.tabs(["Daily Stats", "Hourly Distribution"])
    
    with tab1:
        # Daily registration trend
        daily_stats = df.groupby(df['timestamp'].dt.date).agg({
            'student_id': 'count',
            'usage_time_minutes': ['sum', 'mean']
        }).reset_index()
        daily_stats.columns = ['Date', 'Registrations', 'Total Minutes', 'Avg Minutes']
        
        fig_daily = px.line(daily_stats, x='Date', y=['Registrations', 'Avg Minutes'],
                           title='Daily Registration and Usage Trends')
        st.plotly_chart(fig_daily, use_container_width=True)
        
    with tab2:
        # Hourly distribution
        hourly_dist = df.groupby(df['timestamp'].dt.hour)['student_id'].count().reset_index()
        hourly_dist.columns = ['Hour', 'Count']
        
        fig_hourly = px.bar(hourly_dist, x='Hour', y='Count',
                           title='Usage Distribution by Hour of Day')
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # User Demographics
    st.subheader("👥 User Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Campus distribution
        campus_dist = df['campus'].value_counts()
        fig_campus = px.pie(values=campus_dist.values, names=campus_dist.index,
                           title='Distribution by Campus')
        st.plotly_chart(fig_campus)
        
    with col2:
        # Major distribution
        major_dist = df['major'].value_counts()
        fig_major = px.pie(values=major_dist.values, names=major_dist.index,
                          title='Distribution by Major')
        st.plotly_chart(fig_major)
    
    # Grade Level Analysis
    grade_dist = df['grade'].value_counts()
    fig_grade = px.bar(x=grade_dist.index, y=grade_dist.values,
                       title='Distribution by Grade Level')
    st.plotly_chart(fig_grade, use_container_width=True)
    
    # Raw Data Section
    st.subheader("📝 Raw Registration Data")
    
    # Date filter
    date_range = st.date_input(
        "Filter by date range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df
    
    # Display filtered data
    st.dataframe(
        filtered_df.sort_values('timestamp', ascending=False),
        use_container_width=True
    )
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="nuanswers_registration_data.csv",
            mime="text/csv"
        )
        
    with col2:
        excel_buffer = pd.ExcelWriter(pd.io.common.BytesIO(), engine='openpyxl')
        filtered_df.to_excel(excel_buffer, index=False)
        excel_data = pd.io.common.BytesIO()
        filtered_df.to_excel(excel_data, index=False)
        st.download_button(
            label="📊 Download as Excel",
            data=excel_data.getvalue(),
            file_name="nuanswers_registration_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}") 