# 💬 NuAnswers - AI Tutoring Bot

NuAnswers is an intelligent tutoring bot developed by Beta Alpha Psi: Nu Sigma Chapter. It provides personalized assistance in accounting, finance, and related subjects while encouraging learning through guided problem-solving rather than direct answers.

## 🌟 Features

### 🎓 Intelligent Tutoring
- Step-by-step guidance through problems
- Encourages critical thinking
- Avoids giving direct answers
- Personalized learning experience
- Supports accounting, finance, and related topics

### 📚 Document Support
- Upload and process various file formats:
  - PDF documents
  - Word documents (DOCX)
  - Text files (TXT)
  - PowerPoint presentations (PPTX)
  - Excel spreadsheets (XLS, XLSX)
  - CSV files
- Search within uploaded documents
- Manage and reorder documents
- Context-aware tutoring based on uploaded materials

### ⏰ Smart Availability
- Automatically manages access based on in-person tutoring hours
- Encourages in-person tutoring during scheduled sessions
- Available 24/7 outside of tutoring hours

### 📊 Usage Tracking
- Records student usage statistics
- Tracks session duration
- Maintains user registration data

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Streamlit account (for deployment)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd NuAnswers
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-api-key-here"
ADMIN_PASSWORD = "your-admin-password-here"
```

### Running Locally

```bash
streamlit run streamlit_app.py
```

### Deployment on Render

1. Create a new Web Service on Render
2. Connect your repository
3. Add environment variables:
   - `OPENAI_API_KEY`
   - `ADMIN_PASSWORD`
4. Deploy the service

## 🔧 Configuration

### Tutoring Hours
Modify the `TUTORING_HOURS` dictionary in `streamlit_app.py`:
```python
TUTORING_HOURS = {
    "Monday": [("10:30", "12:30")],    # 10:30 AM - 12:30 PM
    "Tuesday": [("17:00", "19:00")],   # 5:00 PM - 7:00 PM
    "Wednesday": [("12:00", "14:00")], # 12:00 PM - 2:00 PM
    "Thursday": [("10:30", "12:30")],  # 10:30 AM - 12:30 PM
    "Friday": [("13:00", "15:00")],    # 1:00 PM - 3:00 PM
}
```

### File Upload Limits
- Maximum file size: 200MB
- Supported formats: PDF, DOCX, TXT, PPTX, CSV, XLS, XLSX

## 👥 User Types

### Students
- Complete registration form
- Upload course materials
- Interact with the tutoring bot
- Search and manage uploaded documents

### Administrators
- Access usage statistics
- Download registration data
- Monitor student interactions

## 📝 Registration Data
The system collects:
- Full Name
- Student ID
- Email
- Grade Level
- Campus
- Major
- Course Information
- Usage Statistics

## 🔒 Security Features
- Password-protected admin access
- Secure API key management
- User data encryption
- Session management

## 🤝 Contributing
We welcome contributions! Please feel free to submit pull requests.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Beta Alpha Psi: Nu Sigma Chapter
- OpenAI for GPT API
- Streamlit for the web framework
