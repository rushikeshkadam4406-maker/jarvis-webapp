from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import google.generativeai as genai
from faster_whisper import WhisperModel

import tempfile
import shutil
import os

# =========================================================
# GEMINI API KEY
# Get your free API key:
# https://aistudio.google.com
# =========================================================

GOOGLE_API_KEY = "AIzaSyCMxpKpte5NZWn6gd0bMKi8XnCvn4d3S1c"

# =========================================================
# GEMINI SETUP
# =========================================================

genai.configure(api_key=GOOGLE_API_KEY)

gemini_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    system_instruction=(
        "You are Jarvis, a smart AI voice assistant. "
        "Reply naturally, shortly, and helpfully. "
        "You can understand English, Hindi, and Marathi."
    )
)

# =========================================================
# WHISPER MODEL
# =========================================================

print("Loading Whisper model...")

# small = better accuracy than tiny.en
# supports Hindi + Marathi + English

whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")

print("Whisper loaded successfully.")

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="Jarvis AI Assistant")

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# STATIC FILES
# =========================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


# =========================================================
# TRANSCRIBE AUDIO
# =========================================================

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:

        # Save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            shutil.copyfileobj(audio.file, tmp)
            temp_audio_path = tmp.name

        # Whisper transcription
        segments, info = whisper_model.transcribe(
            temp_audio_path,
            beam_size=5
        )

        # Combine all segments
        text = " ".join(segment.text for segment in segments).strip()

        # Debug print
        print("===================================")
        print("Detected language:", info.language)
        print("TRANSCRIBED:", text)
        print("===================================")

        # Delete temp file
        os.unlink(temp_audio_path)

        return {
            "success": True,
            "text": text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription error: {str(e)}"
        )


# =========================================================
# CHAT REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str
    history: list = []


# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat")
async def chat(req: ChatRequest):

    try:

        # Build conversation memory
        history_text = ""

        for turn in req.history[-8:]:

            role = "User"

            if turn["role"] == "assistant":
                role = "Jarvis"

            history_text += f"{role}: {turn['text']}\n"

        # Final prompt
        final_prompt = (
            history_text +
            f"User: {req.message}\nJarvis:"
        )

        # Generate response
        response = gemini_model.generate_content(final_prompt)

        reply = response.text.strip()

        print("USER:", req.message)
        print("JARVIS:", reply)

        return {
            "success": True,
            "reply": reply
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini error: {str(e)}"
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "running"
    }


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )