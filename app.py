import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from langdetect import detect
import tempfile
import os

# Streamlit page config
st.set_page_config(page_title="Multilingual Visual Chatbot", layout="centered")
st.markdown("<h2 style='color: red;'>Author: <span style='font-size: 24px;'>Muhammad Shoaib</span></h2>", unsafe_allow_html=True)
st.title("🌐AI Chatbot")
st.markdown("Type or upload an audio file in multiple languages and get answers in text and audio.")

# Configure Gemini API
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat()

def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

def recognize_speech(uploaded_file):
    try:
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".input")
        temp_input.write(uploaded_file.read())
        temp_input.flush()

        sound = AudioSegment.from_file(temp_input.name)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        sound.export(temp_wav.name, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        os.remove(temp_input.name)
        os.remove(temp_wav.name)
        return text
    except Exception as e:
        st.error(f"Speech Recognition Failed: {e}")
        return None

# Input method
input_method = st.radio("Choose Input Method:", ["Type", "Upload Audio"])
question = ""
detected_lang = "en"

if input_method == "Type":
    question = st.text_input("Type your question:")
    if question:
        try:
            detected_lang = detect(question)
            # Fallback for short questions
            if len(question.split()) <= 3 and detected_lang != "en":
                detected_lang = "en"
        except:
            detected_lang = "en"

else:
    uploaded_audio = st.file_uploader("Upload an audio file (M4A, MP3, MP4, WAV)", type=["m4a", "mp3", "mp4", "wav"])
    if uploaded_audio:
        with st.spinner("Recognizing speech..."):
            recognized_text = recognize_speech(uploaded_audio)
            if recognized_text:
                st.success(f"🗣️ Recognized Text: {recognized_text}")
                question = recognized_text
                try:
                    detected_lang = detect(question)
                except:
                    detected_lang = "en"
            else:
                st.error("❌ Could not recognize speech. Please try again.")

# Send to Gemini and speak answer
if st.button("Ask") and question:
    with st.spinner("Thinking..."):
      prompt = f"""You are a multilingual AI assistant. Answer the following question in the same language it is asked, without explaining the detected language.

          Question: {question}
                  """



    try:
            response = chat.send_message(prompt)
            answer = response.text.strip()

            st.success("🤖 Answer:")
            st.markdown(answer)

            audio_file = speak_text(answer, detected_lang)
            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                os.remove(audio_file)
    except Exception as e:
            st.error(f"Error: {e}")




