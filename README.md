# Emotion Recognition Web App

A full-stack web application for facial emotion recognition using Deep Learning. 
Supports real-time webcam analysis, image upload and video analysis with temporal emotion evolution charts.

## Features

📷 **Live webcam analysis** — real-time emotion detection updated every 1.5 seconds 

🖼️ **Image upload** — analyze facial emotions from JPG, JPEG, PNG files

🎬 **Video upload** — analyze emotions across video frames with temporal timeline (MP4, AVI, MOV, MKV)

📊 **Interactive dashboard** — bar charts, confidence scores, and temporal evolution charts

⚠️ **Smart warnings** — detects missing faces, low confidence results, and corrupted files

## Tech Stack

**Backend**
- Python 3.11
- FastAPI
- DeepFace
- OpenCV
- TensorFlow / Keras
- Pydantic


**Frontend**
- React
- Vite
- Recharts


## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/andrapadurar/emotion-recognition-web-app.git
cd emotion-recognition-web-app

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install the root dependencies
npm install

# Run the application 
npm run dev
```

The API will be available at `http://127.0.0.1:8000`  
Interactive API docs at `http://127.0.0.1:8000/docs`

The app will be available at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | API status |
| POST | `/analyze-image/` | Analyze emotion from image |
| POST | `/analyze-video/` | Analyze emotions from video |
| GET | `/supported-formats` | List supported file formats |

## Supported Formats
Image: JPG, JPEG, PNG (10 MB)

Video: MP4, AVI, MOV, MKV (100 MB)

## Detected Emotions

The application detects 7 basic emotions:
`Angry` · `Disgust` · `Fear` · `Happy` · `Sad` · `Surprise` · `Neutral`
