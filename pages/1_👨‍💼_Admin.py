import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import io
from database import get_filtered_registrations, get_all_registrations

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
    # Load data from database
    df = get_all_registrations()
    
    if df.empty:
        st.info("No registration data available yet.")
        st.stop()
        
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
    
    # Return User Analysis
    st.subheader("🔄 Return User Analysis")
    user_sessions = df.groupby('student_id').size()
    return_users = (user_sessions > 1).sum()
    total_users = len(user_sessions)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Return Users", return_users)
    with col2:
        st.metric("Return Rate", f"{(return_users/total_users)*100:.1f}%")
    with col3:
        avg_sessions = user_sessions.mean()
        st.metric("Avg Sessions per User", f"{avg_sessions:.1f}")
    
    # Time-based Analysis
    st.subheader("📈 Usage Trends")
    
    tab1, tab2, tab3 = st.tabs(["Daily Stats", "Weekly Patterns", "Hourly Distribution"])
    
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
        # Weekly patterns
        df['day_of_week'] = df['timestamp'].dt.day_name()
        weekly_stats = df.groupby('day_of_week').agg({
            'student_id': 'count',
            'usage_time_minutes': 'mean'
        }).reindex(calendar.day_name)
        
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
        # Hourly distribution
        hourly_dist = df.groupby(df['timestamp'].dt.hour)['student_id'].count().reset_index()
        hourly_dist.columns = ['Hour', 'Count']
        
        fig_hourly = px.bar(hourly_dist, x='Hour', y='Count',
                           title='Usage Distribution by Hour of Day')
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Time-Based Performance
    st.subheader("⏰ Time-Based Performance")
    
    tab1, tab2 = st.tabs(["Session Duration Analysis", "Peak Usage Times"])
    
    with tab1:
        # Average session duration by time of day
        hourly_duration = df.groupby(df['timestamp'].dt.hour)['usage_time_minutes'].mean().reset_index()
        hourly_duration.columns = ['Hour', 'Avg Duration']
        
        fig_duration = px.line(hourly_duration, x='Hour', y='Avg Duration',
                             title='Average Session Duration by Hour of Day',
                             labels={'Hour': 'Hour of Day', 'Avg Duration': 'Average Duration (minutes)'})
        st.plotly_chart(fig_duration, use_container_width=True)
        
        # Session duration distribution
        fig_duration_dist = px.histogram(df, x='usage_time_minutes',
                                       title='Distribution of Session Durations',
                                       labels={'usage_time_minutes': 'Session Duration (minutes)'},
                                       nbins=30)
        st.plotly_chart(fig_duration_dist, use_container_width=True)
    
    with tab2:
        # Peak usage times analysis
        df['day_hour'] = df['timestamp'].dt.strftime('%A %H:00')
        peak_usage = df.groupby('day_hour').size().reset_index(name='count')
        peak_usage['day'] = peak_usage['day_hour'].str.split().str[0]
        peak_usage['hour'] = peak_usage['day_hour'].str.split().str[1].str.split(':').str[0].astype(int)
        
        # Create a pivot table for the heatmap
        peak_pivot = peak_usage.pivot(index='day', columns='hour', values='count')
        peak_pivot = peak_pivot.reindex(calendar.day_name)
        
        fig_heatmap = px.imshow(peak_pivot,
                               title='Peak Usage Times Heatmap',
                               labels=dict(x='Hour of Day', y='Day of Week', color='Number of Sessions'),
                               aspect='auto')
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Academic Performance Metrics
    st.subheader("📊 Academic Performance")
    
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
    
    # Course success metrics (if feedback system is implemented)
    st.info("💡 Tip: Consider implementing a feedback system to track course success metrics")
    
    # Most common topics/questions
    st.info("💡 Tip: Consider implementing a topic tracking system to analyze common questions")
    
    # User Engagement Analysis
    st.subheader("📱 User Engagement")
    
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
    
    # Document Upload Analysis
    if 'uploaded_documents' in st.session_state:
        st.subheader("📄 Document Analysis")
        
        # Get document statistics from session state
        doc_stats = pd.DataFrame([
            {
                'student_id': doc.get('student_id'),
                'file_type': Path(doc['name']).suffix.lower(),
                'upload_time': doc.get('upload_time', pd.NaT)
            }
            for doc in st.session_state.uploaded_documents
        ])
        
        if not doc_stats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # File type distribution
                file_type_dist = doc_stats['file_type'].value_counts()
                fig_file_types = px.pie(values=file_type_dist.values,
                                      names=file_type_dist.index,
                                      title='Document Types Distribution')
                st.plotly_chart(fig_file_types)
            
            with col2:
                # Documents per student
                docs_per_student = doc_stats.groupby('student_id').size()
                fig_docs_per_student = px.histogram(x=docs_per_student.values,
                                                  title='Documents per Student',
                                                  labels={'x': 'Number of Documents'},
                                                  nbins=20)
                st.plotly_chart(fig_docs_per_student)
        else:
            st.info("No document upload data available yet")
    
    # Chat Interaction Analysis
    if 'messages' in st.session_state:
        st.subheader("💬 Chat Analysis")
        
        # Analyze chat messages
        messages = pd.DataFrame(st.session_state.messages)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_messages = len(messages)
            st.metric("Total Messages", total_messages)
        
        with col2:
            avg_message_length = messages['content'].str.len().mean()
            st.metric("Avg Message Length", f"{avg_message_length:.0f} chars")
        
        with col3:
            user_messages = len(messages[messages['role'] == 'user'])
            st.metric("User Messages", user_messages)
        
        # Message length distribution
        message_lengths = messages['content'].str.len()
        fig_message_lengths = px.histogram(x=message_lengths,
                                         title='Message Length Distribution',
                                         labels={'x': 'Message Length (characters)'},
                                         nbins=30)
        st.plotly_chart(fig_message_lengths, use_container_width=True)
    else:
        st.info("No chat interaction data available yet")
    
    # Course Analysis
    st.subheader("📚 Course Analysis")
    
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
    
    # Cross Analysis
    st.subheader("🔄 Cross Analysis")
    
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
    
    # Raw Data Section with enhanced filtering
    st.subheader("📝 Raw Registration Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
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
    
    # Get filtered data from database
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = get_filtered_registrations(
            start_date=start_date,
            end_date=end_date,
            majors=selected_majors if selected_majors else None,
            campuses=selected_campuses if selected_campuses else None
        )
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
        excel_data = io.BytesIO()
        with pd.ExcelWriter(excel_data, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        excel_data = excel_data.getvalue()
        st.download_button(
            label="📊 Download as Excel",
            data=excel_data,
            file_name="nuanswers_registration_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}") 