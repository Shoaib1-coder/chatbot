import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
import tempfile
import os

# Load API key from Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

# Initialize Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="Gemini 2.0 Flash")  # Correct model call
chat = model.start_chat()

# Streamlit UI
st.set_page_config(page_title="🎤 Multilingual Chatbot", layout="centered")
st.title("🌍 Speak or Type to the Multilingual Chatbot 🎙️")
st.markdown("Ask in **German 🇩🇪, Arabic 🇸🇦, Urdu 🇵🇰, or English 🇺🇸** by typing or speaking!")

# Language detection function
def detect_language(text):
    urdu_chars = set("ٹںھئےۓ")
    arabic_chars = set("اأإآءئبتثجحخدذرزسشصضطظعغفقكلمنهوىي")

    if any(c in text for c in urdu_chars):
        return "ur"
    elif any(c in text for c in arabic_chars):
        return "ar"
    elif any(c in text for c in "äöüß"):
        return "de"
    else:
        return "en"

# Text-to-speech function
def speak_text(text, lang_code):
    try:
        if lang_code in ["en", "de", "ar", "ur"]:
            tts = gTTS(text=text, lang=lang_code)
        else:
            tts = gTTS(text=text, lang="en")  # fallback
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# Speech-to-text function
def recognize_speech_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

# --- Input Section ---
input_method = st.radio("Choose Input Method:", ["Type ✍️", "Speak 🎤"])
question = ""

if input_method == "Type ✍️":
    question = st.text_input("💬 Type your question:")
else:
    st.markdown("🎤 Record your voice and upload:")
    uploaded_audio = st.file_uploader("Upload a .wav file", type=["wav"])
    if uploaded_audio:
        with st.spinner("Recognizing speech..."):
            temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_audio_path.write(uploaded_audio.read())
            temp_audio_path.close()

            recognized_text = recognize_speech_from_audio(temp_audio_path.name)
            os.remove(temp_audio_path.name)

            if recognized_text:
                st.success(f"✅ Recognized Text: {recognized_text}")
                question = recognized_text
            else:
                st.error("❌ Could not recognize speech. Please try again.")

# --- Ask Gemini ---
if st.button("Ask Gemini") and question:
    with st.spinner("Thinking... 🤔"):
        prompt = f"""
You are a multilingual assistant.
Detect the language of the question (German, Arabic, Urdu, or English) and answer it intelligently in the same language.
Do not translate — give a real answer based on meaning.

Question:
{question}
"""
        try:
            response = chat.send_message(prompt)
            answer = response.text.strip()

            st.success("✅ Gemini's Answer:")
            st.markdown(answer)

            lang_code = detect_language(answer)
            audio_file = speak_text(answer, lang_code)

            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                os.remove(audio_file)

        except Exception as e:
            st.error(f"❌ Error: {e}")
