import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Accounting & Finance Tutor")
st.write(
    "Hello! I'm your Accounting & Finance Tutor. I'm here to help you understand concepts and work through problems. "
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
