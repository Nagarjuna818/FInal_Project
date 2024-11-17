import sys
import cv2
import datetime
import pyttsx3
import speech_recognition as sr
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtGui import QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# Import your main logic modules
from textbook_detection import results as detect_book
from audio_module import transcribe_live_audio
from ocr_module import detect_page_turns, extract_frames, extract_text_from_image, process_video as ocr_process
from title_detection import process_video1 as detect_title

class JarvisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # File paths
        self.video_path = "/Users/ngujjula/Desktop/Final_Project/title.mp4"
        self.video_path1 = "/Users/ngujjula/Desktop/Final_Project/input_videos/pages.mp4"
        self.video_path2 = "/Users/ngujjula/Desktop/Final_Project/title.mp4"
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Set a slower speech rate
        rate = self.tts_engine.getProperty('rate')
        self.tts_engine.setProperty('rate', rate - 100)
        
        # Window setup
        self.setWindowTitle("JARVIS - AI Book Reader")
        self.setGeometry(100, 100, 1200, 800)  # Adjusted window size
        self.setStyleSheet("background-color: #1e1e1e; color: #1F51FF;")
        
        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        layout = QVBoxLayout()
        
        # Welcome Label
        self.welcome_label = QLabel("Initializing JARVIS...")
        self.welcome_label.setStyleSheet("font-size: 24px; margin: 10px;")
        layout.addWidget(self.welcome_label, alignment=Qt.AlignCenter)
        
        # Status Label (for showing processing updates)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; margin: 20px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Label for Detected Frame (this should be properly sized and placed)
        self.detected_frame_label = QLabel("Detected Frame Will Appear Here")
        self.detected_frame_label.setFixedSize(1000, 600)  # Adjust size as needed
        self.detected_frame_label.setStyleSheet("background-color: #000; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.detected_frame_label)

        # Initialize the text display label for OCR text display
        self.text_display_label = QLabel("OCR Text Will Appear Here")
        self.text_display_label.setStyleSheet("font-size: 18px; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.text_display_label, alignment=Qt.AlignCenter)

        # Video Player Widget (with larger size)
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(1000, 600)  # Increased size for the video
        layout.addWidget(self.video_widget)

        # Media Player for Video Playback
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Detect when video finishes playing
        self.media_player.mediaStatusChanged.connect(self.on_video_finished)

        # Setting layout
        self.central_widget.setLayout(layout)
        
        # Initialize the AI with voice interaction
        QTimer.singleShot(1000, self.start_interaction)  # Start interaction after 1 second

    def start_interaction(self):
        """Start the voice interaction loop"""
        # Greet the user
        self.speak("Hello, I am JARVIS. How can I assist you today?")
        self.welcome_label.setText("Hello, I am JARVIS. How can I assist you today?")
        
        # Present user with options
        self.speak("Would you like to start the book detection process, or do you have other tasks for me?")
        self.status_label.setText("Waiting for user's voice input...")

        # Listen for voice input and handle the response
        response = transcribe_live_audio()
        if response:
            self.handle_user_response(response.lower())
        else:
            self.speak("I didn't quite catch that. Please repeat.")
            self.status_label.setText("I didn't quite catch that. Please repeat.")
            self.start_interaction()  # Retry interaction if response is unclear

    def handle_user_response(self, response):
        """Handle user's response after introduction"""
        if 'start' in response or 'book detection' in response:
            self.speak("Starting the book detection process.")
            self.status_label.setText("Starting book detection process...")
            self.play_video(self.video_path2)  # Play video for book detection
        elif 'other' in response or 'something else' in response:
            self.speak("What other tasks can I assist you with?")
            self.status_label.setText("Waiting for further input...")
            # Listen for new tasks (you can add more functionality here based on the user's needs)
            new_task = transcribe_live_audio()
            self.handle_user_response(new_task.lower())  # Process new task request
        elif 'date' in response:
            # Respond with the current date
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {current_date}.")
            self.status_label.setText(f"Today's date is {current_date}.")
        elif 'time' in response:
            # Respond with the current time
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}.")
            self.status_label.setText(f"The current time is {current_time}.")
        elif 'stop' in response or 'exit' in response:
            self.speak("Okay, stopping the interaction. Feel free to call me again when needed.")
            self.status_label.setText("Interaction stopped by user.")
        else:
            # If the response is unclear, ask again
            self.speak("I did not understand. Please say 'start' to begin book detection, or tell me what else I can assist with.")
            self.status_label.setText("Waiting for clearer input from user...")
            self.start_interaction()  # Restart the interaction


    def play_video(self, video_path):
        """Play the video file"""
        # Hide the detected frame label when the video starts
        self.detected_frame_label.setVisible(False)
        
        try:
            video_url = QUrl.fromLocalFile(video_path)
            # Set video output to self.video_widget only
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.setMedia(QMediaContent(video_url))
            self.media_player.play()  # Play the video
            self.status_label.setText("Video is playing...")
        except Exception as e:
            print(f"Error playing video: {e}")
            self.status_label.setText("Error playing video.")



    def on_video_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.status_label.setText("Video completed. Now detecting book in the video...")
            self.speak("Video completed. Now detecting book in the video...")
            self.detected_frame_label.setVisible(True)  # Show the label again
            self.detect_book_in_video()


    def detect_book_in_video(self):
        """Step 1: Detect book in video"""
        self.status_label.setText("Detecting book in the video...")
        
        # Run book detection on video_path2
        bookfound, detected_frame = detect_book(self.video_path2)
        if bookfound:
            self.status_label.setText("Book detected! Running title detection model...")
            self.speak("Book detected! Running title detection model...")
            
            self.display_detected_frame(detected_frame)
            # Step 2: Detect title
            self.detect_title_in_video()
        else:
            self.status_label.setText("No book detected in the video.")
            self.speak("No book detected in the video.")

    def detect_title_in_video(self):
        """Step 2: Detect title in the book"""
        result = detect_title(self.video_path)
        
        if result != "":
            self.status_label.setText(f"Title Detected: {result}")
            self.speak(f"Title Detected: {result}. Would you like to proceed with reading the book?")
            
            # Step 3: Prompt user for voice input
            self.prompt_user_for_confirmation()
        else:
            self.status_label.setText("No title detected in the book.")
            self.speak("No title detected in the book.")

    def prompt_user_for_confirmation(self):
        """Step 3: Ask user for confirmation to proceed"""
        self.status_label.setText("Waiting for user's voice input...")
        self.speak("Please say 'yes' to proceed or 'no' to stop.")
        
        # Listen for voice input
        response = transcribe_live_audio()
        if response and 'yes' in response.lower():
            self.status_label.setText("User confirmed. Running OCR model...")
            self.speak("User confirmed. Running OCR model.")
            
            # Step 4: Run OCR model
            self.run_ocr_on_pages()
        else:
            self.status_label.setText("User did not confirm. OCR model will not be run.")
            self.speak("User did not confirm. OCR model will not be run.")

    def run_ocr_on_pages(self):
        """Step 4: Run OCR model on the pages"""
        self.status_label.setText("Running OCR on pages...")
        self.speak("Running OCR on pages. Please wait while I extract the text.")
        
        output_frames = "/Users/ngujjula/Desktop/Final_Project/output_frames"
        # Process video for OCR and page turns
        frames = extract_frames(self.video_path1, interval_seconds=5, output_frames = output_frames)
        page_turns = detect_page_turns(frames, similarity_threshold=0.8)
        
        print(f"Detected page turns at frames: {page_turns}")

        # Iterate through pages and extract text
        for i, pagenum in enumerate(page_turns):
            text = extract_text_from_image(frames[pagenum])
            self.display_extracted_text(text, page_number=i+1)

            # Speak the extracted text for the current page
            self.speak(f"Reading page {i+1}.")
            self.speak(text)

            # Check if there are more pages to process
            if i < len(page_turns) - 1:
                # Ask the user if they want to continue to the next page
                self.speak("Do you want to continue to the next page?")
                response = transcribe_live_audio()
                response = response.lower() if response else ""

                # Debugging: Display the response in the status label
                self.status_label.setText(f"User response: {response}")

                if 'continue' in response:
                    # Continue to the next page
                    self.status_label.setText(f"Continuing to page {i+2}...")
                    continue
                else:
                    # User does not want to continue or response was unclear
                    self.status_label.setText("Stopping OCR process as per user request.")
                    self.speak("Stopping OCR process as per your request.")
                    break  # Exit the loop if the user doesn't want to continue
            else:
                # This is the last page, no need to ask to continue
                self.status_label.setText("OCR completed! All pages have been processed.")
                self.speak("OCR completed! All pages have been processed.")



    def display_detected_frame(self, frame_path):
        """Load and display the detected frame in the UI"""
        # Load the image from the saved frame path
        pixmap = QPixmap(frame_path)

        # Display the pixmap in the detected frame label
        self.detected_frame_label.setPixmap(pixmap)
        self.detected_frame_label.setScaledContents(True)  # Scale the image to fit the label

    def display_extracted_text(self, text, page_number):
        """Display the extracted text in the UI"""
        # Update the QLabel with the extracted text
        self.text_display_label.setText(f"Page {page_number}:\n{text}")

    def speak(self, text):
        """Function to provide voice feedback"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    

    def listen_for_voice(self):
        """Function to listen for voice input from the microphone"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Listening...")
            self.status_label.setText("Listening...")
            audio_data = recognizer.listen(source)
            try:
                # Recognize the spoken words
                user_input = recognizer.recognize_google(audio_data)
                return user_input.lower()
            except sr.UnknownValueError:
                self.speak("Sorry, I could not understand. Please try again.")
                self.status_label.setText("Sorry, I could not understand. Please try again.")
                return None

# Initialize the app
app = QApplication(sys.argv)

# Customizing the application palette for JARVIS-like style
palette = QPalette()
palette.setColor(QPalette.Window, QColor("#1e1e1e"))  # Dark background
palette.setColor(QPalette.WindowText, QColor("#1F51FF"))  # Neon green text
app.setPalette(palette)

window = JarvisApp()
window.show()
sys.exit(app.exec_())
