from supabase import create_client
import os
import streamlit as st
from datetime import datetime
import pandas as pd

# Initialize Supabase client
def init_supabase():
    url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
    return create_client(supabase_url=url, supabase_key=key)

# Save registration data
def save_registration(user_data, start_time):
    supabase = init_supabase()
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
        "usage_time_minutes": 0,
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("registrations").insert(data).execute()

# Get all registrations
def get_all_registrations():
    supabase = init_supabase()
    response = supabase.table("registrations").select("*").execute()
    return pd.DataFrame(response.data)

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
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("feedback").insert(data).execute()

# Save topic
def save_topic(topic, difficulty, student_id, course_id):
    supabase = init_supabase()
    data = {
        "student_id": student_id,
        "course_id": course_id,
        "topic": topic,
        "difficulty": difficulty,
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("topics").insert(data).execute()

# Save completion
def save_completion(completed, student_id, course_id):
    supabase = init_supabase()
    data = {
        "student_id": student_id,
        "course_id": course_id,
        "completed": completed,
        "timestamp": datetime.now().isoformat()
    }
    supabase.table("completions").insert(data).execute()

# Get all feedback
def get_all_feedback():
    supabase = init_supabase()
    response = supabase.table("feedback").select("*").execute()
    return pd.DataFrame(response.data)

# Get all topics
def get_all_topics():
    supabase = init_supabase()
    response = supabase.table("topics").select("*").execute()
    return pd.DataFrame(response.data)

# Get all completions
def get_all_completions():
    supabase = init_supabase()
    response = supabase.table("completions").select("*").execute()
    return pd.DataFrame(response.data) 
