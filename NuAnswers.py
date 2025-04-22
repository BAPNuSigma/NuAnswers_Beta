import streamlit as st
from openai import OpenAI
import pandas as pd
import datetime
import os
import tempfile
from pathlib import Path
from database import save_registration as db_save_registration

# Get data directory from environment variable or use current directory
DATA_DIR = os.environ.get('DATA_DIR', '.')
os.makedirs(DATA_DIR, exist_ok=True)

def save_registration(user_data, start_time):
    """Save registration data to database"""
    end_time = datetime.datetime.now()
    usage_time = (end_time - start_time).total_seconds() / 60
    
    # Save to database
    if db_save_registration(user_data, usage_time):
        st.success("Registration data saved successfully!")
    else:
        st.error("Failed to save registration data. Please try again.")

def save_registration_to_file(user_data, start_time):
    """Save registration data to session state DataFrame and persistent storage"""
    end_time = datetime.datetime.now()
    usage_time = (end_time - start_time).total_seconds() / 60
    
    # Create new registration entry
    new_registration = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "full_name": user_data["full_name"],
        "student_id": user_data["student_id"],
        "email": user_data["email"],
        "grade": user_data["grade"],
        "campus": user_data["campus"],
        "major": user_data["major"],
        "course_name": user_data["course_name"],
        "course_id": user_data["course_id"],
        "professor": user_data["professor"],
        "usage_time_minutes": usage_time
    }
    
    # Add new registration to the DataFrame
    st.session_state.registration_data = pd.concat([
        st.session_state.registration_data,
        pd.DataFrame([new_registration])
    ], ignore_index=True)
    
    # Save to CSV file for persistence
    try:
        # Load existing data if file exists
        csv_path = os.path.join(DATA_DIR, "registration_data.csv")
        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            combined_data = pd.concat([existing_data, pd.DataFrame([new_registration])], ignore_index=True)
        else:
            combined_data = pd.DataFrame([new_registration])
        
        # Save combined data back to CSV
        combined_data.to_csv(csv_path, index=False)
        
        # Create a backup
        backup_path = os.path.join(DATA_DIR, f"registration_data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        combined_data.to_csv(backup_path, index=False)
        
        # Keep only the 5 most recent backups
        backup_files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith('registration_data_backup_')])
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                os.remove(os.path.join(DATA_DIR, old_backup))
                
    except Exception as e:
        st.error(f"Failed to save registration data: {str(e)}") 