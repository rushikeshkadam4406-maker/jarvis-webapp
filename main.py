from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from faster_whisper import WhisperModel
import tempfile
import os
import shutil

# =========================================
# ⚠️  EDIT THIS — Add your Gemini API key
# Get free key at: https://aistudio.google.com
# =========================================

GOOGLE_API_KEY = "your_gemini_api_key_here"

# =========================================
# GEMINI SETUP
# =========================================

genai.configure(api_key=GOOGLE_API_KEY)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash-lite",
    system_instruction=(
        "You are Jarvis, an advanced AI assistant. "
        "Reply in one short, precise sentence. Be direct and helpful."
    )
)

# =========================================
# WHISPER SETUP (runs on server)
# =========================================

print("Loading Whisper model...")
whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
print("Whisper loaded.")

# =========================================
# FASTAPI APP
# =========================================

app = FastAPI(title="Jarvis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


# =========================================
# TRANSCRIBE ENDPOINT
# Browser sends audio blob → Whisper transcribes
# =========================================

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            shutil.copyfileobj(audio.file, tmp)
            tmp_path = tmp.name

        segments, _ = whisper_model.transcribe(
            tmp_path,
            language="en",
            beam_size=1
        )
        text = "".join(seg.text for seg in segments).strip()
        os.unlink(tmp_path)

        return {"text": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# CHAT ENDPOINT
# =========================================

class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        history_text = ""
        for turn in req.history[-6:]:
            role = "User" if turn["role"] == "user" else "Jarvis"
            history_text += f"{role}: {turn['text']}\n"

        prompt = history_text + f"User: {req.message}"
        response = gemini_model.generate_content(prompt)
        reply = response.text.strip()
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================
# RUN
# =========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
