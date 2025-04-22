import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String)
    student_id = Column(String)
    email = Column(String)
    grade = Column(String)
    campus = Column(String)
    major = Column(String)
    course_name = Column(String)
    course_id = Column(String)
    professor = Column(String)
    usage_time_minutes = Column(Float)

# Create tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)

def save_registration(user_data, usage_time):
    """Save registration data to database"""
    try:
        session = Session()
        new_registration = Registration(
            timestamp=datetime.now(),
            full_name=user_data["full_name"],
            student_id=user_data["student_id"],
            email=user_data["email"],
            grade=user_data["grade"],
            campus=user_data["campus"],
            major=user_data["major"],
            course_name=user_data["course_name"],
            course_id=user_data["course_id"],
            professor=user_data["professor"],
            usage_time_minutes=usage_time
        )
        session.add(new_registration)
        session.commit()
        return True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        return False
    finally:
        session.close()

def get_all_registrations():
    """Get all registrations as a pandas DataFrame"""
    try:
        return pd.read_sql_table('registrations', engine)
    except Exception as e:
        print(f"Error reading from database: {str(e)}")
        return pd.DataFrame()

def get_filtered_registrations(start_date=None, end_date=None, majors=None, campuses=None):
    """Get filtered registrations as a pandas DataFrame"""
    try:
        query = 'SELECT * FROM registrations WHERE 1=1'
        params = {}
        
        if start_date:
            query += ' AND timestamp >= :start_date'
            params['start_date'] = start_date
        
        if end_date:
            query += ' AND timestamp <= :end_date'
            params['end_date'] = end_date
        
        if majors:
            query += ' AND major = ANY(:majors)'
            params['majors'] = majors
        
        if campuses:
            query += ' AND campus = ANY(:campuses)'
            params['campuses'] = campuses
        
        return pd.read_sql_query(query, engine, params=params)
    except Exception as e:
        print(f"Error reading from database: {str(e)}")
        return pd.DataFrame() 