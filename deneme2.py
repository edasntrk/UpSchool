import streamlit as st
import subprocess
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ensure temp directories exist
os.makedirs("temp_video", exist_ok=True)
os.makedirs("temp_audio", exist_ok=True)

# Predefined list of languages
languages = ['English', 'Turkish', 'French', 'German', 'Spanish', 'Italian', 'Chinese', 'Japanese', 'Arabic']

# Streamlit App Title
st.title("Multilingual Video Transcription and Translation App")

# Language Selection
st.header("Select Languages for Translation")
selected_languages = st.multiselect(
    "Choose one or more languages:",
    options=languages
)

# Video File Upload
st.header("Upload a Video File")
uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv'])

def convert_video_to_audio(video_file, audio_file):
    # Replace 'C:\\path\\to\\ffmpeg.exe' with the full path to your ffmpeg executable
    ffmpeg_path = "C:\\Users\\LENOVO\\Downloads\\ffmpeg-master-latest-win64-gpl-shared\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"
    command = f'"{ffmpeg_path}" -i "{video_file}" -q:a 0 -map a "{audio_file}" -y'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        st.error(f"Error converting video to audio: {result.stderr}")
        return False
    return True

def transcribe_audio(audio_file):
    if not os.path.exists(audio_file):
        st.error(f"Audio file not found: {audio_file}")
        return ""
    with open(audio_file, "rb") as f:
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=f
        )
    return response['text']

def translate_text(text, target_language):
    # Construct a chat-based prompt
    prompt = f"Translate the following text into {target_language}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Use the latest chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

if uploaded_file is not None:
    # Save the uploaded file temporarily
    video_path = os.path.join("temp_video", uploaded_file.name)
    with open(video_path, 'wb') as f:
        f.write(uploaded_file.read())
    st.success("Video uploaded successfully.")

    # Convert Video to Audio
    audio_path = os.path.join("temp_audio", "audio.wav")
    if convert_video_to_audio(video_path, audio_path):
        st.success("Video converted to audio successfully.")

        # Transcribe Audio
        st.header("Transcribing Audio...")
        transcription = transcribe_audio(audio_path)
        if transcription:
            st.text_area("Transcription:", transcription, height=200)

            # Translate Transcription
            if selected_languages:
                st.header("Translating Transcription...")
                translations = {}
                for lang in selected_languages:
                    st.write(f"Translating to {lang}...")
                    translation = translate_text(transcription, lang)
                    translations[lang] = translation
                    st.success(f"Translation to {lang} completed.")

                # Display and Download Translations
                st.header("Translated Texts")
                for lang, text in translations.items():
                    st.subheader(f"Translation in {lang}")
                    st.text_area(f"{lang} Translation", text, height=200)

                    # Prepare file for download
                    file_name = f"translation_{lang}.txt"
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(text)
                    with open(file_name, 'rb') as f:
                        st.download_button(
                            label=f"Download {lang} Translation",
                            data=f,
                            file_name=file_name,
                            mime='text/plain'
                        )
# Instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload an audio file (MP4, AVI, MOV, MKV or MPEG4 format).
2. Enter the desired language for translation.
3. Click 'Transcribe and Translate' to process the audio.
4. View the translated subtitles and download the file.
""")