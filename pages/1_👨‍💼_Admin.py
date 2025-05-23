import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import numpy as np
from pathlib import Path
import io
from supabase_db import get_all_registrations, get_all_feedback, get_all_topics, get_all_completions

# Set page config
st.set_page_config(
    page_title="NuAnswers Admin",
    page_icon="👨‍💼",
    layout="wide"
)

# Hide all default Streamlit elements we don't want to show
st.markdown("""
    <style>
        /* Hide page names in sidebar */
        span.css-10trblm.e16nr0p30 {
            display: none;
        }
        /* Hide the default Streamlit menu button */
        button.css-1rs6os.edgvbvh3 {
            display: none;
        }
        /* Hide "streamlit app" text */
        .css-17ziqus {
            display: none;
        }
        /* Hide development mode indicator */
        .stDeployButton {
            display: none;
        }
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("👨‍💼 Administrator Dashboard")

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
    # Load all data from Supabase
    df = get_all_registrations()
    feedback_df = get_all_feedback()
    topic_df = get_all_topics()
    completion_df = get_all_completions()
    
    # Convert timestamp columns to datetime if they exist
    for df_name, df_data in [('df', df), ('feedback_df', feedback_df), 
                            ('topic_df', topic_df), ('completion_df', completion_df)]:
        if not df_data.empty and 'timestamp' in df_data.columns:
            try:
                df_data['timestamp'] = pd.to_datetime(df_data['timestamp'])
            except Exception as e:
                st.error(f"Error converting timestamp in {df_name}: {str(e)}")
                # If conversion fails, drop the timestamp column
                df_data = df_data.drop('timestamp', axis=1)
    
    # Add download section at the top
    st.subheader("📥 Download Data")
    
    download_col1, download_col2 = st.columns(2)
    
    # Prepare all data
    all_data = {
        "Registration Data": df,
        "Feedback Data": feedback_df,
        "Topic Data": topic_df,
        "Completion Data": completion_df
    }
    
    # Create Excel file with multiple sheets
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for sheet_name, data_df in all_data.items():
            if not data_df.empty:
                data_df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Create an empty DataFrame with the same columns
                empty_df = pd.DataFrame(columns=data_df.columns)
                empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    with download_col1:
        # Download individual CSVs
        for name, data_df in all_data.items():
            if not data_df.empty:
                csv_data = data_df.to_csv(index=False).encode('utf-8')
            else:
                # Create an empty CSV with headers
                csv_data = pd.DataFrame(columns=data_df.columns).to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download {name} (CSV)",
                data=csv_data,
                file_name=f"nuanswers_{name.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    
    with download_col2:
        # Download combined Excel file
        excel_buffer.seek(0)
        st.download_button(
            label="Download All Data (Excel)",
            data=excel_buffer,
            file_name="nuanswers_all_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Overview metrics
    st.subheader("📊 Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registrations", len(df) if not df.empty else 0)
    with col2:
        total_usage = df['usage_time_minutes'].sum() if not df.empty else 0
        st.metric("Total Usage Time (hrs)", f"{total_usage / 60:.1f}")
    with col3:
        avg_session = df['usage_time_minutes'].mean() if not df.empty else 0
        st.metric("Avg. Session Length (min)", f"{avg_session:.1f}")
    with col4:
        unique_students = df['student_id'].nunique() if not df.empty else 0
        st.metric("Unique Students", unique_students)
    
    # Return User Analysis
    st.subheader("🔄 Return User Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Return Users", 0)
    with col2:
        st.metric("Return Rate", "0.0%")
    with col3:
        st.metric("Avg Sessions per User", "0.0")
    
    # Time-based Analysis
    st.subheader("📈 Usage Trends")
    
    tab1, tab2, tab3 = st.tabs(["Daily Stats", "Weekly Patterns", "Hourly Distribution"])
    
    with tab1:
        # Create empty daily stats DataFrame
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now())
        daily_stats = pd.DataFrame({
            'Date': dates,
            'Registrations': [0] * len(dates),
            'Total Minutes': [0] * len(dates),
            'Avg Minutes': [0] * len(dates)
        })
        
        fig_daily = px.line(daily_stats, x='Date', y=['Registrations', 'Avg Minutes'],
                           title='Daily Registration and Usage Trends')
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with tab2:
        # Create empty weekly stats DataFrame
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_stats = pd.DataFrame({
            'day_of_week': day_order,
            'student_id': [0] * 7,
            'usage_time_minutes': [0] * 7
        }).set_index('day_of_week')
        
        fig_weekly = go.Figure()
        fig_weekly.add_trace(go.Bar(
            x=weekly_stats.index,
            y=weekly_stats['student_id'],
            name='Number of Sessions'
        ))
        fig_weekly.add_trace(go.Scatter(
            x=weekly_stats.index,
            y=weekly_stats['usage_time_minutes'],
            name='Avg Session Length (min)',
            yaxis='y2'
        ))
        fig_weekly.update_layout(
            title='Weekly Usage Patterns',
            yaxis2=dict(
                title='Avg Session Length (min)',
                overlaying='y',
                side='right'
            )
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    with tab3:
        # Create empty hourly distribution DataFrame
        hourly_dist = pd.DataFrame({
            'Hour': range(24),
            'Count': [0] * 24
        })
        
        fig_hourly = px.bar(hourly_dist, x='Hour', y='Count',
                           title='Usage Distribution by Hour of Day')
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Time-Based Performance
    st.subheader("⏰ Time-Based Performance")
    
    tab1, tab2 = st.tabs(["Session Duration Analysis", "Peak Usage Times"])
    
    with tab1:
        # Create empty duration analysis
        hourly_duration = pd.DataFrame({
            'Hour': range(24),
            'Avg Duration': [0] * 24
        })
        
        fig_duration = px.line(hourly_duration, x='Hour', y='Avg Duration',
                             title='Average Session Duration by Hour of Day',
                             labels={'Hour': 'Hour of Day', 'Avg Duration': 'Average Duration (minutes)'})
        st.plotly_chart(fig_duration, use_container_width=True)
        
        # Create empty duration distribution
        duration_dist = pd.DataFrame({
            'usage_time_minutes': range(0, 60, 2),
            'count': [0] * 30
        })
        
        fig_duration_dist = px.histogram(duration_dist, x='usage_time_minutes',
                                       title='Distribution of Session Durations',
                                       labels={'usage_time_minutes': 'Session Duration (minutes)'},
                                       nbins=30)
        st.plotly_chart(fig_duration_dist, use_container_width=True)
    
    with tab2:
        if not df.empty:
            # Peak usage times analysis
            df['day_hour'] = df['timestamp'].dt.strftime('%A %H:00')
            peak_usage = df.groupby('day_hour').size().reset_index(name='count')
            peak_usage['day'] = peak_usage['day_hour'].str.split().str[0]
            peak_usage['hour'] = peak_usage['day_hour'].str.split().str[1].str.split(':').str[0].astype(int)
            
            # Create a pivot table for the heatmap
            peak_pivot = peak_usage.pivot(index='day', columns='hour', values='count')
            # Use explicit day order instead of calendar.day_name
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            peak_pivot = peak_pivot.reindex(day_order)
            
            fig_heatmap = px.imshow(peak_pivot,
                                   title='Peak Usage Times Heatmap',
                                   labels=dict(x='Hour of Day', y='Day of Week', color='Number of Sessions'),
                                   aspect='auto')
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No peak usage data available yet.")
    
    # User Engagement Analysis
    st.subheader("📱 User Engagement")
    
    if not df.empty:
        # Session frequency analysis
        user_frequency = df.groupby('student_id').agg({
            'timestamp': ['count', lambda x: (x.max() - x.min()).days + 1]
        }).reset_index()
        user_frequency.columns = ['student_id', 'total_sessions', 'days_span']
        user_frequency['sessions_per_day'] = user_frequency['total_sessions'] / user_frequency['days_span'].clip(lower=1)
        
        fig_frequency = px.histogram(user_frequency, x='sessions_per_day',
                                    title='Distribution of Session Frequency',
                                    labels={'sessions_per_day': 'Average Sessions per Day'},
                                    nbins=20)
        st.plotly_chart(fig_frequency, use_container_width=True)
        
        # Engagement metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_sessions_per_day = user_frequency['sessions_per_day'].mean()
            st.metric("Avg Sessions per Day", f"{avg_sessions_per_day:.2f}")
        
        with col2:
            retention_rate = (user_frequency['total_sessions'] > 1).mean() * 100
            st.metric("User Retention Rate", f"{retention_rate:.1f}%")
        
        with col3:
            avg_days_active = user_frequency['days_span'].mean()
            st.metric("Avg Days Active", f"{avg_days_active:.1f}")
        
        # Time between sessions analysis
        df_sorted = df.sort_values(['student_id', 'timestamp'])
        df_sorted['prev_timestamp'] = df_sorted.groupby('student_id')['timestamp'].shift(1)
        df_sorted['time_between_sessions'] = (df_sorted['timestamp'] - df_sorted['prev_timestamp']).dt.total_seconds() / 3600  # in hours
        
        # Filter out first sessions (no previous timestamp) and unreasonable values
        time_between = df_sorted[df_sorted['time_between_sessions'].between(0, 720)]  # up to 30 days
        
        fig_time_between = px.histogram(time_between, x='time_between_sessions',
                                       title='Time Between Sessions',
                                       labels={'time_between_sessions': 'Hours Between Sessions'},
                                       nbins=50)
        st.plotly_chart(fig_time_between, use_container_width=True)
    else:
        st.info("No user engagement data available yet.")
    
    # Academic Performance Metrics
    st.subheader("📊 Academic Performance")
    
    if not df.empty:
        # Grade level progression
        grade_order = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
        grade_usage = df.groupby(['grade', 'major']).agg({
            'student_id': 'count',
            'usage_time_minutes': 'mean'
        }).reset_index()
        
        fig_grade_usage = px.scatter(grade_usage, 
                                    x='grade', 
                                    y='usage_time_minutes',
                                    size='student_id',
                                    color='major',
                                    category_orders={'grade': grade_order},
                                    title='Usage Patterns by Grade Level and Major',
                                    labels={'grade': 'Grade Level', 
                                           'usage_time_minutes': 'Average Session Duration (min)',
                                           'student_id': 'Number of Sessions'})
        st.plotly_chart(fig_grade_usage, use_container_width=True)
    else:
        st.info("No academic performance data available yet.")
    
    # Course success metrics
    st.subheader("📊 Course Success Metrics")
    
    # Create columns for different metrics
    success_col1, success_col2 = st.columns(2)
    
    with success_col1:
        # Session feedback analysis
        if not feedback_df.empty:
            # Calculate average ratings
            avg_rating = feedback_df['rating'].mean()
            st.metric("Average Session Rating", f"{avg_rating:.1f}/5")
            
            # Rating distribution
            fig_ratings = px.histogram(feedback_df, x='rating',
                                     title='Distribution of Session Ratings',
                                     labels={'rating': 'Rating (1-5)'},
                                     nbins=5)
            st.plotly_chart(fig_ratings, use_container_width=True)
        else:
            st.info("No feedback data available yet")
    
    with success_col2:
        # Course completion tracking
        if not completion_df.empty:
            # Calculate completion rates
            completion_rate = (completion_df['completed'].sum() / len(completion_df)) * 100
            st.metric("Average Completion Rate", f"{completion_rate:.1f}%")
            
            # Completion by course
            course_completion = completion_df.groupby('course_id')['completed'].mean() * 100
            fig_completion = px.bar(x=course_completion.index, 
                                  y=course_completion.values,
                                  title='Completion Rates by Course',
                                  labels={'x': 'Course ID', 'y': 'Completion Rate (%)'})
            st.plotly_chart(fig_completion, use_container_width=True)
        else:
            st.info("No completion data available yet")
    
    # Most common topics/questions
    st.subheader("📝 Topic Analysis")
    
    if not topic_df.empty:
        # Create columns for different topic analyses
        topic_col1, topic_col2 = st.columns(2)
        
        with topic_col1:
            # Most common topics
            topic_counts = topic_df['topic'].value_counts().head(10)
            fig_topics = px.bar(x=topic_counts.index, 
                              y=topic_counts.values,
                              title='Top 10 Most Common Topics',
                              labels={'x': 'Topic', 'y': 'Number of Questions'})
            st.plotly_chart(fig_topics, use_container_width=True)
        
        with topic_col2:
            # Topic difficulty analysis
            if 'difficulty' in topic_df.columns:
                topic_difficulty = topic_df.groupby('topic')['difficulty'].mean().sort_values(ascending=False).head(10)
                fig_difficulty = px.bar(x=topic_difficulty.index,
                                      y=topic_difficulty.values,
                                      title='Most Challenging Topics',
                                      labels={'x': 'Topic', 'y': 'Average Difficulty (1-5)'})
                st.plotly_chart(fig_difficulty, use_container_width=True)
        
        # Topic trends over time
        topic_trends = topic_df.groupby([pd.Grouper(key='timestamp', freq='D'), 'topic']).size().unstack(fill_value=0)
        fig_trends = px.line(topic_trends,
                           title='Topic Trends Over Time',
                           labels={'value': 'Number of Questions', 'variable': 'Topic'})
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("No topic data available yet")
    
    # Demographic Analysis
    st.subheader("👥 User Demographics")
    
    if not df.empty:
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
    else:
        st.info("No demographic data available yet")
    
    # Cross Analysis
    st.subheader("🔄 Cross Analysis")
    
    if not df.empty:
        # Major vs Grade Level
        major_grade_dist = pd.crosstab(df['major'], df['grade'])
        fig_major_grade = px.imshow(major_grade_dist,
                                   title='Major vs Grade Level Distribution',
                                   aspect='auto')
        st.plotly_chart(fig_major_grade, use_container_width=True)
        
        # Usage Patterns by Major
        major_usage = df.groupby('major').agg({
            'usage_time_minutes': ['mean', 'count']
        }).reset_index()
        major_usage.columns = ['Major', 'Avg Minutes', 'Session Count']
        
        fig_major_usage = go.Figure()
        fig_major_usage.add_trace(go.Bar(
            x=major_usage['Major'],
            y=major_usage['Session Count'],
            name='Number of Sessions'
        ))
        fig_major_usage.add_trace(go.Scatter(
            x=major_usage['Major'],
            y=major_usage['Avg Minutes'],
            name='Avg Session Length (min)',
            yaxis='y2'
        ))
        fig_major_usage.update_layout(
            title='Usage Patterns by Major',
            yaxis2=dict(
                title='Avg Session Length (min)',
                overlaying='y',
                side='right'
            )
        )
        st.plotly_chart(fig_major_usage, use_container_width=True)
    else:
        st.info("No cross analysis data available yet")
    
    # Course Analysis
    st.subheader("📚 Course Analysis")
    
    if not df.empty:
        tab1, tab2 = st.tabs(["Course Distribution", "Professor Analysis"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                course_dist = df['course_name'].value_counts().head(10)
                fig_course = px.bar(x=course_dist.index, y=course_dist.values,
                                   title='Top 10 Most Common Courses')
                st.plotly_chart(fig_course, use_container_width=True)
            
            with col2:
                course_id_dist = df['course_id'].value_counts().head(10)
                fig_course_id = px.bar(x=course_id_dist.index, y=course_id_dist.values,
                                      title='Top 10 Course IDs')
                st.plotly_chart(fig_course_id, use_container_width=True)
        
        with tab2:
            prof_dist = df['professor'].value_counts()
            fig_prof = px.pie(values=prof_dist.values, names=prof_dist.index,
                             title='Distribution by Professor')
            st.plotly_chart(fig_prof, use_container_width=True)
    else:
        st.info("No course analysis data available yet")
    
    # Raw Data Section with enhanced filtering
    st.subheader("📝 Raw Registration Data")
    
    if not df.empty:
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Date filter
            date_range = st.date_input(
                "Filter by date range",
                value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
                min_value=df['timestamp'].min().date(),
                max_value=df['timestamp'].max().date()
            )
        
        with col2:
            # Major filter
            selected_majors = st.multiselect(
                "Filter by Major",
                options=sorted(df['major'].unique()),
                default=[]
            )
        
        with col3:
            # Campus filter
            selected_campuses = st.multiselect(
                "Filter by Campus",
                options=sorted(df['campus'].unique()),
                default=[]
            )
        
        with col4:
            # Professor filter
            selected_professors = st.multiselect(
                "Filter by Professor",
                options=sorted(df['professor'].unique()),
                default=[]
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['timestamp'].dt.date >= start_date) & 
                (filtered_df['timestamp'].dt.date <= end_date)
            ]
        
        if selected_majors:
            filtered_df = filtered_df[filtered_df['major'].isin(selected_majors)]
        
        if selected_campuses:
            filtered_df = filtered_df[filtered_df['campus'].isin(selected_campuses)]
            
        if selected_professors:
            filtered_df = filtered_df[filtered_df['professor'].isin(selected_professors)]
        
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
    else:
        st.info("No registration data available yet")

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")
    st.info("Some dashboard features may be limited until data becomes available.") 
