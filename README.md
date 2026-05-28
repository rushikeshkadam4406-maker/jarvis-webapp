# J.A.R.V.I.S — Voice AI Web App

A voice chatbot powered by **Whisper** (speech-to-text) + **Gemini AI** + **Browser TTS** (text-to-speech).

## 📁 Project Structure

```
jarvis-webapp/
├── main.py              ← FastAPI backend
├── requirements.txt     ← Python packages
├── .gitignore
├── README.md
└── static/
    └── index.html       ← Frontend UI
```

## ⚙️ Setup on Cloud Server

### 1. Clone the repository
```bash
git clone https://github.com/YOURUSERNAME/jarvis-webapp.git
cd jarvis-webapp
```

### 2. Add your Gemini API key
```bash
nano main.py
# Find this line and replace with your key:
# GOOGLE_API_KEY = "your_gemini_api_key_here"
```
Get a free key at: https://aistudio.google.com

### 3. Install system dependencies
```bash
sudo apt update
sudo apt install ffmpeg python3-pip -y
```

### 4. Install Python packages
```bash
pip install -r requirements.txt
```

### 5. Run the app
```bash
python main.py
```

Open in browser: **http://YOUR_SERVER_IP:8000**

## 🔑 Get Gemini API Key (Free)
1. Go to https://aistudio.google.com
2. Click **Get API Key**
3. Copy and paste into `main.py`

## 💡 Features
- 🎤 Voice input (recorded → Whisper on server)
- 🔊 Voice output (browser text-to-speech)
- 📷 Photo attachments
- 📄 File attachments
- ⌨️ Text input fallback
- 💬 Conversation history
