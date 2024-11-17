import speech_recognition as sr
from pydub import AudioSegment
import pyttsx3 


engine = pyttsx3.init()

rate = engine.getProperty('rate')  # Get current speech rate
engine.setProperty('rate', rate - 50)

def transcribe_audio_file(file_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file_path)

    with audio_file as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Request error: {e}"

def transcribe_live_audio():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # Adjust for ambient noise
        print("Adjusting for ambient noise. Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=3)

        # engine.say("Do you want to read this book?")
        # engine.runAndWait()

        print("Please say something (press Ctrl+C to end)...")
        try:
            # Listen for audio input
            audio = recognizer.listen(source)
            
            # Transcribe the audio to text
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"Request error: {e}"
        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
            return "Recording stopped."


# Example Usage
# print("Transcription from file:")
# print(transcribe_audio_file('path_to_your_audio_file.wav'))

# print("\nTranscription from microphone:")
# print(transcribe_live_audio())