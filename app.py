# Import necessary libraries
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment

# Set up Gemini API key from Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

# Load Gemini model (fast and cost-efficient version)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat()

# Streamlit page configuration
st.set_page_config(page_title="Visual Chatbot", layout="centered")
st.title("Speak or Type to the Visual Chatbot")

# UI message for user
st.markdown("Ask in **English**, **German**, **Arabic**, **Urdu**, **Chinese**, **Spanish**, or **Hindi** by typing, speaking, or uploading audio!")

# ----------------------------- #
def detect_language(text):
    urdu_chars = set("ٹںھئےۓ")
    arabic_chars = set("اأإآءئبتثجحخدذرزسشصضطظعغفقكلمنهوىي")
    hindi_chars = set("ऀ-ॿ")
    chinese_chars = set("的一是不了人我在有他这为之大来以个中上们")
    spanish_chars = set("áéíóúñü¿¡")
    if any(c in text for c in urdu_chars): return "ur"
    elif any(c in text for c in arabic_chars): return "ar"
    elif any(c in text for c in hindi_chars): return "hi"
    elif any(c in text for c in chinese_chars): return "zh-CN"
    elif any(c in text for c in spanish_chars): return "es"
    elif any(c in text for c in "äöüß"): return "de"
    else: return "en"

# ----------------------------- #
def speak_text(text, lang_code):
    try:
        supported_langs = ["en", "de", "ar", "ur", "hi", "zh-CN", "es"]
        tts_lang = lang_code if lang_code in supported_langs else "en"
        tts = gTTS(text=text, lang=tts_lang)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# ----------------------------- #
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say something...")
        audio_data = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio_data)
        except:
            return None

# ----------------------------- #
def transcribe_uploaded_audio(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            audio = AudioSegment.from_file(uploaded_file)
            audio.export(tmp_wav.name, format="wav")
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_wav.name) as source:
                audio_data = recognizer.record(source)
                return recognizer.recognize_google(audio_data)
    except Exception as e:
        st.error(f"Transcription Error: {e}")
        return None

# ----------------------------- #
# Choose input method
input_method = st.radio("Choose Input Method:", ["Type", "Speak", "Upload Audio"])
question = ""

# Text input
if input_method == "Type":
    question = st.text_input("Type your question:")

# Speech input
elif input_method == "Speak":
    st.markdown("Speak your question:")
    if st.button("Start Recording"):
        recognized_text = recognize_speech_from_mic()
        if recognized_text:
            st.success(f"Recognized Text: {recognized_text}")
            question = recognized_text
        else:
            st.error("Could not recognize speech. Please try again.")

# Uploaded audio input
else:
    uploaded_audio = st.file_uploader("Upload an audio file", type=["mp3", "m4a", "wav", "flac", "ogg", "wma", "aac"])
    if uploaded_audio and st.button("Transcribe Audio"):
        question = transcribe_uploaded_audio(uploaded_audio)
        if question:
            st.success(f"Transcribed Text: {question}")
        else:
            st.error("Could not transcribe audio. Please try a clearer recording.")

# ----------------------------- #
if st.button("Ask Question") and question:
    with st.spinner("Thinking..."):
        prompt = f"""
You are a multilingual AI chatbot.
Respond to the user's question in the **same language** it is asked — supported languages include: English, German, Arabic, Urdu, Chinese, Spanish, and Hindi.
Do **not** mention or explain the detected language. Just return the appropriate answer based on the question.

Question:
{question}
"""
        try:
            response = chat.send_message(prompt)
            answer = response.text.strip()
            st.success("Answer:")
            st.markdown(answer)
            lang_code = detect_language(answer)
            audio_file = speak_text(answer, lang_code)
            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                os.remove(audio_file)
        except Exception as e:
            st.error(f"Error: {e}")








