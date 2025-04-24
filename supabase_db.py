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
def save_registration_data(user_data, start_time=None):
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
            "timestamp": datetime.now(timezone.utc).isoformat()
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
    try:
        supabase = init_supabase()
        response = supabase.table("registrations").select("*").execute()
        df = pd.DataFrame(response.data)
        
        # Convert timezone-aware timestamps to timezone-naive timestamps
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        
        return df
    except Exception as e:
        st.error(f"Error retrieving registrations: {str(e)}")
        return pd.DataFrame()

# Get filtered registrations
def get_filtered_registrations(start_date=None, end_date=None, majors=None, campuses=None):
    try:
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
        df = pd.DataFrame(response.data)
        
        # Convert timezone-aware timestamps to timezone-naive timestamps
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        
        return df
    except Exception as e:
        st.error(f"Error retrieving filtered registrations: {str(e)}")
        return pd.DataFrame()

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

# OpenAI pricing as of 2025 (in USD per 1M tokens)
MODEL_PRICING = {
    "gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00
    },
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00
    }
}

def save_api_usage(input_tokens, output_tokens, model="gpt-3.5-turbo"):
    """Save API usage data to Supabase"""
    try:
        supabase = init_supabase()
        if not supabase:
            st.error("Failed to initialize Supabase client")
            return None

        # Calculate cost based on model
        input_cost = (input_tokens / 1000000) * MODEL_PRICING[model]["input"]
        output_cost = (output_tokens / 1000000) * MODEL_PRICING[model]["output"]
        total_cost = input_cost + output_cost

        data = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table("api_usage").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error saving API usage: {str(e)}")
        return None

def get_api_usage_summary(start_date=None, end_date=None):
    """Get summary of API usage and costs with date filtering"""
    try:
        supabase = init_supabase()
        query = supabase.table("api_usage").select("*")
        
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
            
        response = query.execute()
        df = pd.DataFrame(response.data)
        
        if df.empty:
            return pd.DataFrame(), 0, 0, 0, 0, {}
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        
        # Calculate totals
        total_input_tokens = df['input_tokens'].sum()
        total_output_tokens = df['output_tokens'].sum()
        total_cost = df['total_cost'].sum()
        
        # Calculate usage by model
        model_usage = df.groupby('model').agg({
            'input_tokens': 'sum',
            'output_tokens': 'sum',
            'total_cost': 'sum'
        }).to_dict('index')
        
        return df, total_input_tokens, total_output_tokens, total_cost, model_usage
    except Exception as e:
        st.error(f"Error retrieving API usage: {str(e)}")
        return pd.DataFrame(), 0, 0, 0, 0, {}

def get_credit_balance():
    """Get the current credit balance"""
    try:
        supabase = init_supabase()
        response = supabase.table("credit_balance").select("*").order("timestamp", desc=True).limit(1).execute()
        
        if not response.data:
            return 0.0
            
        return float(response.data[0]['balance'])
    except Exception as e:
        st.error(f"Error retrieving credit balance: {str(e)}")
        return 0.0

def update_credit_balance(new_balance):
    """Update the credit balance"""
    try:
        supabase = init_supabase()
        data = {
            "balance": new_balance,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = supabase.table("credit_balance").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error updating credit balance: {str(e)}")
        return None 
