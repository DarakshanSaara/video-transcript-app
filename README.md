# 🎥 Video Transcript App

A web application that fetches **YouTube video transcripts** (including timestamps) and displays them alongside the video.  
Built for creators, learners, and researchers who want **real-time captions**, **highlighting**, and **searchable transcripts** without needing to manually download subtitles.

---

## 🚀 Features

- **YouTube Transcript Fetching**  
  Get transcripts for any public YouTube video using its URL.
  
- **Timestamps Included**  
  Every caption comes with start time & duration.

- **Real-time Highlighting**  
  Highlight the current transcript line while the video is playing.

- **Search Within Transcript**  
  Quickly find keywords or phrases in the video’s spoken content.

- **Dark/Light Mode Toggle**  
  Smooth theme switching for better user experience.

- **Error Handling**  
  Handles cases where transcripts are unavailable or disabled.

---

## 🛠 Tech Stack

### **Frontend**
- React.js (UI framework)
- Tailwind CSS / CSS Modules (styling)
- Axios (API calls)

### **Backend**
- Python (Flask REST API)
- youtube-transcript-api (for fetching YouTube transcripts)
- requests (for making HTTP calls)
- OpenAI API (for summarization and language tasks)
- Hugging Face Transformers (for question generation)
- Translation & Speech Tools (for voice translation features)

### **Development Tools**
- Python virtual environment (venv)
- npm/yarn
- Git & GitHub for version control

---

## 📂 Project Structure

video-transcript-app/
│
├── backend/ # Flask API backend
│ ├── app.py # Main backend entry point
│ ├── requirements.txt # Backend dependencies
│ └── venv/ # Python virtual environment
│
├── frontend/ # React frontend
│ ├── src/ # React source code
│ ├── package.json # Frontend dependencies
│ └── public/
│
└── README.md

---

## ⚙️ Installation & Setup

### **1️⃣ Clone the repository**
```
git clone https://github.com/DarakshanSaara/video-transcript-app.git
cd video-transcript-app
```
2️⃣ Backend Setup
```
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```
Run the backend:
```
python app.py
```
Backend runs on http://localhost:5000.

3️⃣ Frontend Setup
```
cd frontend
npm install
npm start
```
Frontend runs on http://localhost:3000.

## 🔗 API Endpoint
POST /get_transcript
Fetches transcript with timestamps for a given YouTube video.

Request Example:
```
{
  "video_url": "https://www.youtube.com/watch?v=example"
}
```
Response Example:
```
[
  {
    "text": "Hello and welcome...",
    "start": 0.0,
    "duration": 4.5
  },
  {
    "text": "In this video, we will...",
    "start": 4.5,
    "duration": 3.0
  }
]
```

🎯 Future Enhancements

Auto-sync highlighting for live video playback.
Multi-language transcript support.
Download transcript as text/PDF.
AI-powered video summarization.

👩‍💻 Author
Saara Darakshan
B.Tech CSE | Full Stack Developer | AI & Web Enthusiast