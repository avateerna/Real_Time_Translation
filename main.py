import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings


# Function to record audio and save to a WAV file
def record_audio(file_path, duration=5):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        st.write("Recording...")
        audio_data = recognizer.record(source, duration=duration)
        st.write("Finished recording.")

    with open(file_path, "wb") as f:
        f.write(audio_data.get_wav_data())


# Function to transcribe audio file to text using SpeechRecognition
def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
 
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="en-US")
        st.write(f"Transcription: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand the audio.")
        return ""
    except sr.RequestError as e:
        st.write(f"""Could not request results from
                 Google Speech Recognition service; {e}""")
        return ""


# Function to translate text to German
def translate_to_german(text):
    translator = Translator()
    result = translator.translate(text, src='en', dest='de')
    return result.text


# Function to convert text to speech in German
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang='de')
    tts.save(output_file)
    st.write(f"German audio saved to {output_file}")


# Streamlit UI
def main():
    st.title("Avateerna Demo App")

    # ask for permission to use microphone
    webrtc_ctx = webrtc_streamer(
        key="audio-input",
        mode=WebRtcMode.SENDONLY,
        client_settings=ClientSettings(
            audio=True,
            video=False,
            force_streaming=True,
            async_processing=True,
        ),
        )

    if not webrtc_ctx.state.playing:
        st.warning("Please allow microphone access.")
        return

    duration = st.slider("Recording Duration (seconds)",
                         min_value=1, max_value=20, value=20)

    if st.button("Record Audio"):
        file_path = 'output.wav'
        record_audio(file_path, duration)
        transcribed_text = transcribe_audio(file_path)

        if transcribed_text:
            translated_text = translate_to_german(transcribed_text)
            st.write(f"Translated Text (German): {translated_text}")

            output_audio_file = 'output_audio.mp3'
            text_to_speech(translated_text, output_audio_file)
            st.audio(output_audio_file, format='audio/mp3')


if __name__ == "__main__":
    main()
