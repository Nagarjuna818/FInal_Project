import speech_recognition as sr


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
        print("Adjusting for ambient noise. Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=2)

        print("Please say something (press Ctrl+C to stop)...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Error: Could not understand audio.")
            return "Error: Could not understand audio."
        except sr.RequestError as e:
            print(f"Error: Request failed: {e}")
            return f"Error: Request failed: {e}"
        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
            return "Recording stopped."



# Example Usage
# print("Transcription from file:")
# print(transcribe_audio_file('path_to_your_audio_file.wav'))

# print("\nTranscription from microphone:")
# print(transcribe_live_audio())