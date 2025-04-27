import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os


st.set_page_config(page_title="Visual Chatbot", layout="centered")
st.title(" Visual Chatbot")
st.markdown("Ask in **German**, **Arabic**, **Urdu **, or **English ** by typing or uploading an audio file")


API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)


model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat()


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

def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code if lang_code in ["en", "de", "ar", "ur"] else "en")
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


input = st.radio("Choose Input Method:", ["Type ", "Upload Audio "])
question = ""

if input == "Type ":
    question = st.text_input("Type your question:")
else:
    uploaded_audio = st.file_uploader("Upload an audio file (M4A, MP3, MP4, WAV)", type=["m4a", "mp3", "mp4", "wav"])
    if uploaded_audio:
        with st.spinner("Recognizing speech..."):
            recognized_text = recognize_speech(uploaded_audio)
            if recognized_text:
                st.success(f" Recognized Text: {recognized_text}")
                question = recognized_text
            else:
                st.error(" Could not recognize speech. Please try again.")


if st.button("Ask ") and question:
    with st.spinner("Thinking... "):
        prompt = f"""
You are a Visual AI Assistant.
Detect the language of the question (German, Arabic, Urdu, or English) and answer it  in the same language.


Question:
{question}
"""
        try:
            response = chat.send_message(prompt)
            answer = response.text.strip()

            st.success(" Answer:")
            st.markdown(answer)

            lang_code = detect_language(answer)
            audio_file = speak_text(answer, lang_code)

            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                os.remove(audio_file)

        except Exception as e:
            st.error(f" Error: {e}")



