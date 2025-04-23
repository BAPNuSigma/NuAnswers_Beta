from supabase import create_client
import os
import streamlit as st
from datetime import datetime, timezone
import pandas as pd

# Initialize Supabase client
def init_supabase():
    try:
        url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
        if not url or not key:
            st.error("Supabase credentials not found. Please check your environment variables or secrets.")
            return None
        client = create_client(supabase_url=url, supabase_key=key)
        return client
    except Exception as e:
        st.error(f"Error initializing Supabase client: {str(e)}")
        return None

# Save registration data
def save_registration(user_data, start_time):
    try:
        supabase = init_supabase()
        if not supabase:
            st.error("Failed to initialize Supabase client")
            return None

        # Log the data being sent
        st.write("Debug - Saving registration data:", user_data)
        
        data = {
            "full_name": user_data["full_name"],
            "student_id": user_data["student_id"],
            "email": user_data["email"],
            "grade": user_data["grade"],
            "campus": user_data["campus"],
            "major": user_data["major"],
            "course_name": user_data["course_name"],
            "course_id": user_data["course_id"],
            "professor": user_data["professor"],
            "professor_email": user_data["professor_email"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "start_time": start_time.isoformat() if start_time else None
        }

        # Log the formatted data
        st.write("Debug - Formatted data for Supabase:", data)
        
        response = supabase.table("registrations").insert(data).execute()
        
        if not response.data:
            st.error("No data returned from Supabase after insert")
            return None
            
        st.success("Registration saved successfully!")
        return response.data[0]
    except Exception as e:
        st.error(f"Detailed error saving registration: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

# Get all registrations
def get_all_registrations():
    supabase = init_supabase()
    response = supabase.table("registrations").select("*").execute()
    df = pd.DataFrame(response.data)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Get filtered registrations
def get_filtered_registrations(start_date=None, end_date=None, majors=None, campuses=None):
    supabase = init_supabase()
    query = supabase.table("registrations").select("*")
    
    if start_date:
        query = query.gte("timestamp", start_date.isoformat())
    if end_date:
        query = query.lte("timestamp", end_date.isoformat())
    if majors:
        query = query.in_("major", majors)
    if campuses:
        query = query.in_("campus", campuses)
        
    response = query.execute()
    return pd.DataFrame(response.data)

# Save feedback
def save_feedback(rating, topic, difficulty, student_id, course_id):
    supabase = init_supabase()
    data = {
        "student_id": student_id,
        "course_id": course_id,
        "rating": rating,
        "topic": topic,
        "difficulty": difficulty,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    supabase.table("feedback").insert(data).execute()

# Get all feedback
def get_all_feedback():
    supabase = init_supabase()
    response = supabase.table("feedback").select("*").execute()
    df = pd.DataFrame(response.data)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Save topic
def save_topic(topic, difficulty, student_id, course_id):
    supabase = init_supabase()
    data = {
        "student_id": student_id,
        "course_id": course_id,
        "topic": topic,
        "difficulty": difficulty,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    supabase.table("topics").insert(data).execute()

# Get all topics
def get_all_topics():
    supabase = init_supabase()
    response = supabase.table("topics").select("*").execute()
    df = pd.DataFrame(response.data)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Save completion
def save_completion(completed, student_id, course_id):
    supabase = init_supabase()
    data = {
        "student_id": student_id,
        "course_id": course_id,
        "completed": completed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    supabase.table("completions").insert(data).execute()

# Get all completions
def get_all_completions():
    supabase = init_supabase()
    response = supabase.table("completions").select("*").execute()
    df = pd.DataFrame(response.data)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df 
