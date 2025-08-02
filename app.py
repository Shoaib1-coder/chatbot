import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import tempfile
import os

# Load API key from Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure the Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat()

# Streamlit UI setup
st.set_page_config(page_title=" Chatbot", layout="centered")
st.title("AI Chatbot")
st.markdown("Ask in **German**, **Arabic**, **Urdu**, **Hindi**, **Chinese**, **Spanish**, or **English**!")

# Detect language based on specific script characters
def detect_language(text):
    urdu_chars = set("ٹںھئےۓ")
    arabic_chars = set("اأإآءئبتثجحخدذرزسشصضطظعغفقكلمنهوىي")
    hindi_chars = set("अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह")
    chinese_chars = set("的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞")

    if any(c in text for c in urdu_chars):
        return "ur"
    elif any(c in text for c in arabic_chars):
        return "ar"
    elif any(c in text for c in hindi_chars):
        return "hi"
    elif any(c in text for c in chinese_chars):
        return "zh"
    elif any(c in text for c in "ñáéíóú"):
        return "es"
    elif any(c in text for c in "äöüß"):
        return "de"
    else:
        return "en"

# Convert text to speech and return path to audio file
def speak_text(text, lang_code):
    try:
        supported_langs = ["en", "de", "ar", "ur", "hi", "zh", "es"]
        if lang_code not in supported_langs:
            lang_code = "en"
        tts = gTTS(text=text, lang=lang_code)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# --- INPUT TEXT ONLY ---
st.markdown(" Type your question below")
user_input = st.text_input("Your question:")

# --- SEND TO GEMINI ---
if st.button("Ask Question") and user_input:
    with st.spinner("Thinking..."):
        prompt = f"""
You are a Visual AI chatbot assistant.
Detect the language of the question (German, Arabic, Urdu, Hindi, Spanish, Chinese, or English).
Do **not** mention or explain the detected language and answer it in the same language.
Do not translate — give a real answer based on meaning.

Question:
{user_input}
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
