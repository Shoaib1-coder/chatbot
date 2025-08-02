# Import necessary libraries
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
import tempfile
import os

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
st.markdown("Ask in **English**, **German**, **Arabic**, **Urdu**, **Chinese**, **Spanish**, or **Hindi** by typing or speaking!")

# ----------------------------- #
# Function to detect language based on character sets
def detect_language(text):
    urdu_chars = set("ٹںھئےۓ")
    arabic_chars = set("اأإآءئبتثجحخدذرزسشصضطظعغفقكلمنهوىي")
    hindi_chars = set("ऀ-ॿ")
    chinese_chars = set("的一是不了人我在有他这为之大来以个中上们")
    spanish_chars = set("áéíóúñü¿¡")

    # Check for presence of language-specific characters
    if any(c in text for c in urdu_chars):
        return "ur"
    elif any(c in text for c in arabic_chars):
        return "ar"
    elif any(c in text for c in hindi_chars):
        return "hi"
    elif any(c in text for c in chinese_chars):
        return "zh-CN"
    elif any(c in text for c in spanish_chars):
        return "es"
    elif any(c in text for c in "äöüß"):
        return "de"
    else:
        return "en"  # Default to English

# ----------------------------- #
# Function to convert text to speech using gTTS
def speak_text(text, lang_code):
    try:
        # Supported language codes for gTTS
        supported_langs = ["en", "de", "ar", "ur", "hi", "zh-CN", "es"]
        tts_lang = lang_code if lang_code in supported_langs else "en"
        
        # Generate TTS audio
        tts = gTTS(text=text, lang=tts_lang)
        
        # Save TTS audio to temporary MP3 file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# ----------------------------- #
# Function to recognize speech from microphone using Google Speech Recognition
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say something...")
        audio_data = recognizer.listen(source)
        try:
            # Convert audio to text
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None  # No speech recognized
        except sr.RequestError:
            return None  # API issue

# ----------------------------- #
# Choose input method: type or speak
input_method = st.radio("Choose Input Method:", ["Type", "Speak"])
question = ""

# If user chooses to type
if input_method == "Type":
    question = st.text_input("Type your question:")
else:
    st.markdown("Speak your question:")
    if st.button("Start Recording"):
        recognized_text = recognize_speech_from_mic()
        if recognized_text:
            st.success(f"Recognized Text: {recognized_text}")
            question = recognized_text
        else:
            st.error("Could not recognize speech. Please try again.")

# ----------------------------- #
# Ask Gemini model if question is provided
if st.button("Ask Question") and question:
    with st.spinner("Thinking..."):
        # Gemini prompt with instruction to reply in same language
        prompt = f"""
You are a multilingual AI chatbot.

Respond to the user's question in the **same language** it is asked — supported languages include: English, German, Arabic, Urdu, Chinese, Spanish, and Hindi.

Do **not** mention or explain the detected language. Just return the appropriate answer based on the question.

Question:
{question}
"""
        try:
            # Send the prompt to Gemini model
            response = chat.send_message(prompt)
            answer = response.text.strip()

            # Display the answer
            st.success("Answer:")
            st.markdown(answer)

            # Detect language of the answer
            lang_code = detect_language(answer)
            st.caption(f"🔍 Detected Language Code: {lang_code}")

            # Convert answer to speech
            audio_file = speak_text(answer, lang_code)

            # Play audio if generated successfully
            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                os.remove(audio_file)  # Clean up temporary file

        except Exception as e:
            st.error(f"Error: {e}")







