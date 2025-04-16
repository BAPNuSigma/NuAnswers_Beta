import streamlit as st
from openai import OpenAI
import pandas as pd
import datetime
import os

# Initialize session state for registration and tracking
if "registered" not in st.session_state:
    st.session_state.registered = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Function to save user data and usage time
def save_user_data(user_data, usage_time):
    # Create data directory if it doesn't exist
    if not os.path.exists("user_data"):
        os.makedirs("user_data")
    
    # Create or load the CSV file
    csv_path = "user_data/user_registrations.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(columns=[
            "timestamp", "full_name", "student_id", "email", "grade", "campus",
            "major", "course_name", "course_id", "professor", "usage_time_minutes"
        ])
    
    # Add new user data
    new_row = {
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
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_path, index=False)

# Registration form
if not st.session_state.registered:
    st.title("📝 Registration Form")
    st.write("Please complete the registration form to use NuAnswers.")
    
    with st.form("registration_form"):
        full_name = st.text_input("Full Name")
        student_id = st.text_input("FDU Student ID")
        email = st.text_input("FDU Student Email")
        grade = st.selectbox("Grade", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
        campus = st.selectbox("Campus", ["Florham", "Metro", "Vancouver"])
        major = st.selectbox("Major", ["Accounting", "Finance", "MIS [Management Information Systems]"])
        
        # Course-specific questions based on major
        if major == "Accounting":
            course_name = st.text_input("Which Accounting class are you taking that relates to what you need help in?")
        elif major == "Finance":
            course_name = st.text_input("Which Finance class are you taking that relates to what you need help in?")
        else:  # MIS
            course_name = st.text_input("Which MIS class are you taking that relates to what you need help in?")
        
        course_id = st.text_input("Course ID (EX: ACCT_####_##)")
        professor = st.text_input("Professor's Name")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not all([full_name, student_id, email, course_id, professor]):
                st.error("Please fill in all required fields.")
            else:
                st.session_state.user_data = {
                    "full_name": full_name,
                    "student_id": student_id,
                    "email": email,
                    "grade": grade,
                    "campus": campus,
                    "major": major,
                    "course_name": course_name,
                    "course_id": course_id,
                    "professor": professor
                }
                st.session_state.registered = True
                st.session_state.start_time = datetime.datetime.now()
                st.rerun()

# Show title and description only after registration
if st.session_state.registered:
    st.title("💬 NuAnswers")
    st.write(
        "Hello! I am NuAnswers, Beta Alpha Psi: Nu Sigma Chapter's AI Tutor Bot. I'm here to help you understand concepts and work through problems. "
        "Remember, I won't give you direct answers, but I'll guide you to find them yourself. "
        "I can help you with accounting equations, financial ratios, financial statements, and time value of money concepts."
    )

    # Get the API key from secrets.toml
    openai_api_key = st.secrets.get("OPENAI_API_KEY")

    if not openai_api_key or openai_api_key == "your-api-key-here":
        st.error("Please configure your OpenAI API key in .streamlit/secrets.toml")
        st.stop()

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Accounting & Finance Tutor. I'm here to help you understand concepts and work through problems. What would you like to work on today?"}
        ]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What would you like to work on today?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API with a system message to enforce tutoring behavior
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are an Accounting & Finance Tutor. Your role is to guide students through their homework and exam preparation through a conversational, step-by-step approach.

IMPORTANT RULES:
1. NEVER give direct answers or solutions
2. Ask ONE question at a time and wait for the student's response
3. After each student response, ask a follow-up question to guide their thinking
4. If the student's answer is incorrect, ask a guiding question to help them think differently
5. If the student asks for the answer, respond with a question that helps them think about the problem differently
6. Use simple, clear questions that build on each other
7. Focus on one concept or step at a time
8. Validate their understanding before moving to the next step
9. Use encouraging phrases like "Good thinking!" or "You're on the right track!"
10. If the student seems stuck, ask a simpler question that breaks down the problem

Example of good tutoring:
Student: "How do I solve this problem?"
Tutor: "Let's start with the first step. What information do we have in the problem?"
Student: [responds]
Tutor: "Good! Now, what do you think we should do with this information?"
[continue with one question at a time]

Example of bad tutoring:
"Here's how to solve it: First, do this, then do that, then calculate this..."
[giving multiple steps at once]"""},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a logout button
    if st.button("Logout"):
        # Calculate usage time
        end_time = datetime.datetime.now()
        usage_time = (end_time - st.session_state.start_time).total_seconds() / 60
        
        # Save user data and usage time
        save_user_data(st.session_state.user_data, usage_time)
        
        # Reset session state
        st.session_state.registered = False
        st.session_state.start_time = None
        st.session_state.user_data = {}
        st.session_state.messages = []
        st.rerun()
