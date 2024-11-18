import os
import sys
import cv2
import datetime
import pyttsx3
import speech_recognition as sr
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QStackedWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# Import your main logic modules
from textbook_detection import results as detect_book
from ocr_module import extract_text_from_image, extract_frames, detect_page_turns
from title_detection import process_video1 as detect_title


class JarvisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._title_detected = False  # Track if the title has been detected
        self._ocr_running = False  # Track if OCR is already running
        self._last_spoken = None  # Track the last text spoken
        self._current_page = 0  # Initialize current page index

        # File paths
        self.video_path = "/Users/nagarjuna/FInal_Project/title.mp4"
        self.video_path1 = "/Users/nagarjuna/FInal_Project/pages.mp4"
        self.video_path2 = "/Users/nagarjuna/FInal_Project/title.mp4"

        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        rate = self.tts_engine.getProperty('rate')
        self.tts_engine.setProperty('rate', rate - 100)

        # Window setup
        self.setWindowTitle("JARVIS - AI Book Reader")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #1e1e1e; color: #1F51FF;")

        # Central widget
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Create different screens
        self.init_screen = self.create_init_screen()
        self.video_screen = self.create_video_screen()
        self.detected_frame_screen = self.create_detected_frame_screen()
        self.text_display_screen = self.create_text_display_screen()

        # Add screens to the stacked widget
        self.central_widget.addWidget(self.init_screen)
        self.central_widget.addWidget(self.video_screen)
        self.central_widget.addWidget(self.detected_frame_screen)
        self.central_widget.addWidget(self.text_display_screen)

        # Show the initialization screen
        self.central_widget.setCurrentWidget(self.init_screen)

        # Initialize the AI with voice interaction
        QTimer.singleShot(1000, self.start_interaction)

    def create_init_screen(self):
        """Create the initial screen with the JARVIS symbol and options"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.jarvis_label = QLabel("JARVIS")
        self.jarvis_label.setStyleSheet("font-size: 48px; color: #1F51FF;")
        layout.addWidget(self.jarvis_label, alignment=Qt.AlignCenter)

        self.greeting_label = QLabel("Hello, I am JARVIS. How can I assist you today?")
        self.greeting_label.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(self.greeting_label, alignment=Qt.AlignCenter)

        # Initialize the message label for JARVIS messages
        self.message_label = QLabel("Welcome to JARVIS!")
        self.message_label.setStyleSheet("font-size: 16px; color: #1F51FF; margin-top: 20px;")
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        screen.setLayout(layout)
        return screen


    def create_video_screen(self):
        """Create the screen for video playback"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(1000, 600)
        layout.addWidget(self.video_widget)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; margin: 20px; color: #FFF;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        screen.setLayout(layout)
        return screen

    def on_video_status_changed(self, status):
        """Handle video playback status changes"""
        if status == QMediaPlayer.EndOfMedia:
            print("Debug: Video playback completed.")  # Logs video completion
            self.speak("Video completed. Detecting book in the video...")
            self.detect_book_in_video()
        elif status == QMediaPlayer.InvalidMedia:
            self.speak("Error playing video. Please check the file path.")
            print("Error: Invalid media file.")  # Logs the error
        elif status == QMediaPlayer.NoMedia:
            print("Debug: No media loaded.")  # Logs no media error
            self.speak("No video file loaded. Please try again.")

    def create_text_display_screen(self):
        """Create the screen for displaying extracted text and JARVIS messages."""
        screen = QWidget()
        layout = QVBoxLayout()

        # Label to display extracted text
        self.text_display_label = QLabel("Extracted Text Will Appear Here")
        self.text_display_label.setStyleSheet("font-size: 18px; color: #FFF;")
        layout.addWidget(self.text_display_label, alignment=Qt.AlignCenter)

        # Label to display what JARVIS is speaking
        self.message_label = QLabel("JARVIS Messages Will Appear Here")
        self.message_label.setStyleSheet("font-size: 16px; color: #1F51FF; margin-top: 20px;")
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        screen.setLayout(layout)
        return screen


    def create_detected_frame_screen(self):
        """Create the screen for displaying detected frames"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.detected_frame_label = QLabel()
        self.detected_frame_label.setFixedSize(1000, 600)
        self.detected_frame_label.setStyleSheet("background-color: #000; color: #FFF;")
        layout.addWidget(self.detected_frame_label, alignment=Qt.AlignCenter)

        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-size: 24px; color: #1F51FF; margin-top: 20px;")
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        screen.setLayout(layout)
        return screen

    def create_text_display_screen(self):
        """Create the screen for displaying extracted text"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.text_display_label = QLabel("Extracted Text Will Appear Here")
        self.text_display_label.setStyleSheet("font-size: 18px; color: #FFF;")
        layout.addWidget(self.text_display_label, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 18px; color: #FFF; margin-top: 20px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        screen.setLayout(layout)
        return screen

    def start_interaction(self):
        """Start the voice interaction loop"""
        self.speak("Hello, I am JARVIS. How can I assist you today?")
        self.greeting_label.setText("Hello, I am JARVIS. Say 'start' to begin or ask for the date or time.")
        self.listen_for_voice_input(self.handle_user_response)

    def speak(self, text):
        """Text-to-speech output with dynamic UI update and terminal logging."""
        if hasattr(self, '_last_spoken') and self._last_spoken == text:
            print(f"Debug: Skipping redundant speech: {text}")  # Avoid duplicate speech
            return

        self._last_spoken = text  # Track the last spoken text
        print(f"JARVIS: {text}")  # Logs spoken text
        self.message_label.setText(text)  # Update the JARVIS message label on the UI
        self.status_label.setText(text)  # Update the status label for clarity
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()






    def listen_for_voice_input(self, callback):
        """Listen for voice input and pass the result to the callback."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Listening... You have 10 seconds to respond.")
            self.status_label.setText("Listening for your response...")
            print("Debug: Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)

            try:
                # Listen for audio input
                print("Debug: Listening for user input...")
                audio = recognizer.listen(source, timeout=10)  # Increased timeout
                print("Debug: Processing audio input...")
                command = recognizer.recognize_google(audio)
                print(f"User: {command}")  # Logs the user's spoken text
                callback(command)
            except sr.UnknownValueError:
                self.speak("I couldn't understand what you said. Please try again.")
                self.status_label.setText("Error: Could not understand the audio.")
                print("Error: Could not understand audio.")  # Logs an error message
                callback(None)
            except sr.RequestError as e:
                self.speak(f"Sorry, there seems to be an issue with the voice service: {e}")
                self.status_label.setText(f"Error: Voice service request failed: {e}")
                print(f"Error: Voice service request failed: {e}")  # Logs an error message
                callback(None)
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything. Please respond more quickly.")
                self.status_label.setText("Listening timed out. Please respond faster.")
                print("Error: Listening timed out.")  # Logs timeout
                callback(None)



    def handle_user_response(self, response):
        """Handle user's response from voice input"""
        if not response:
            self.start_interaction()  # Restart interaction if no valid response
            return

        if 'start' in response:
            self.speak("Starting the book detection process.")
            self.central_widget.setCurrentWidget(self.video_screen)
            self.play_video(self.video_path2)
        elif 'date' in response:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today's date is {current_date}.")
            self.start_interaction()  # Loop back to interaction
        elif 'time' in response:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}.")
            self.start_interaction()  # Loop back to interaction
        elif 'stop' in response or 'exit' in response:
            self.speak("Goodbye!")
            self.close()
        else:
            self.speak("I did not understand. Please try again.")
            self.start_interaction()

    def play_video(self, video_path):
        """Play the video file"""
        video_url = QUrl.fromLocalFile(video_path)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.on_video_status_changed)  # Connect the updated method
        self.media_player.setMedia(QMediaContent(video_url))
        self.media_player.play()

    def detect_book_in_video(self):
        """Step 1: Detect book in video"""
        print("Debug: Starting book detection.")  # Logs progress
        self.speak("Detecting book in the video...")
        bookfound, detected_frame = detect_book(self.video_path2)

        if bookfound:
            print("Debug: Book detected!")  # Logs success
            self.display_detected_frame(detected_frame)  # Display detected frame in the UI
            self.speak("Book detected! Moving to title detection.")
            QTimer.singleShot(2000, self.detect_title_in_video)  # Proceed to title detection
        else:
            print("Debug: No book detected.")  # Logs failure
            self.speak("No book detected in the video. Returning to the main screen.")
            self.central_widget.setCurrentWidget(self.init_screen)



    def on_video_finished(self, status):
        """Handle video playback finished event"""
        if status == QMediaPlayer.EndOfMedia:
            print("Debug: Video playback completed.")  # Logs video completion
            self.detect_book_in_video()  # Transition directly to book detection

        elif status == QMediaPlayer.InvalidMedia:
            self.speak("Error playing video. Please check the file path.")
            print("Error: Invalid media file.")  # Logs the error


    def set_ui_message(self, message):
        """Helper method to update UI and speak a message."""
        self.status_label.setText(message)
        self.speak(message)

# Example usage in `detect_title_in_video`
    def detect_title_in_video(self):
        """Step 2: Detect title in the book"""
        if not self._title_detected:
            print("Debug: Detecting title...")  # Logs detection start
            self.status_label.setText("Detecting title in the video...")
            
            # Get the detected title from title_detection
            result = detect_title(self.video_path)

            if result and result != "No valid title detected.":
                self._title_detected = True
                detected_title = f"Title Detected: {result}"
                print(f"Debug: {detected_title}")
                
                # Update the UI with the detected title
                self.title_label.setText(detected_title)
                self.central_widget.setCurrentWidget(self.detected_frame_screen)
                
                # Speak the title only after displaying it
                self.speak(f"{detected_title}. Do you want to read this book?")
                self.listen_for_voice_input(self.process_reading_decision)
            else:
                self.speak("No title detected.")
                self.central_widget.setCurrentWidget(self.init_screen)




    def process_reading_decision(self, response):
        """Process user's decision to read the book"""
        if response and 'yes' in response.lower():
            self.run_ocr_on_pages()
        else:
            self.speak("Okay, stopping the process.")
            self.central_widget.setCurrentWidget(self.init_screen)

    def run_ocr_on_pages(self):
        """Step 4: Run OCR model on the pages."""
        # Check if the frames and page_turns were already calculated
        if not hasattr(self, '_frames') or not hasattr(self, '_page_turns'):
            self.status_label.setText("Running OCR on pages...")
            self.speak("Running OCR on pages. Please wait while I extract the text.")

            output_frames = "/Users/nagarjuna/FInal_Project/output_frames"
            os.makedirs(output_frames, exist_ok=True)

            # Process video for OCR and detect page turns
            self._frames = extract_frames(self.video_path1, interval_seconds=5)
            self._page_turns = detect_page_turns(self._frames, similarity_threshold=0.8)

            if not self._frames or not self._page_turns:
                self.status_label.setText("No pages detected for OCR.")
                self.speak("No pages detected for OCR. Returning to the main screen.")
                print("Debug: No pages detected for OCR.")
                self.central_widget.setCurrentWidget(self.init_screen)
                return

            print(f"Debug: Detected page turns at frames: {self._page_turns}")
            self._current_page = 0  # Reset to the first page

        # Continue processing from the current page
        if self._current_page < len(self._page_turns):
            frame_index = self._page_turns[self._current_page]
            text = extract_text_from_image(self._frames[frame_index])
            self.display_extracted_text(text, page_number=self._current_page + 1)

            # Speak the extracted text for the current page
            print(f"Debug: Displaying text for page {self._current_page + 1}.")
            self.speak(f"Page {self._current_page + 1}: {text.strip()}")

            # Check if there are more pages to process
            if self._current_page < len(self._page_turns) - 1:
                self.speak("Do you want to continue to the next page?")
                self.listen_for_voice_input(self.handle_page_response)
            else:
                # All pages processed
                self.status_label.setText("OCR completed! All pages have been processed.")
                self.speak("OCR completed! All pages have been processed.")
                print("Debug: All pages processed.")
                self.central_widget.setCurrentWidget(self.init_screen)
        else:
            print("Debug: All pages already processed.")
            self.speak("OCR process completed. Returning to the main screen.")
            self.central_widget.setCurrentWidget(self.init_screen)

    def handle_page_response(self, response):
        """Handle user's response to continue or stop OCR."""
        if response and 'continue' in response.lower():
            print(f"Debug: User chose to continue to page {self._current_page + 2}.")
            self._current_page += 1  # Move to the next page
            self.run_ocr_on_pages()  # Continue processing
        else:
            print("Debug: User chose to stop OCR.")
            self.speak("Stopping OCR process as per your request.")
            self.central_widget.setCurrentWidget(self.init_screen)


    def display_extracted_text(self, text, page_number):
        """
        Dynamically update the UI with extracted text for a specific page.
        """
        # Format the page text
        formatted_text = f"Page {page_number}:\n{text}"
        print(f"Debug: Displaying text for page {page_number}.")  # Debugging log

        # Update the QLabel with the extracted text
        self.text_display_label.setText(formatted_text)

        # Switch to the text display screen dynamically
        self.central_widget.setCurrentWidget(self.text_display_screen)

        # Update status and log
        self.status_label.setText(f"Displaying text for page {page_number}...")
        self.message_label.setText(f"JARVIS is processing page {page_number}.")



    def process_page_decision(self, response, frames):
        """Process user's decision to continue to the next page"""
        if response and 'continue' in response.lower():
            print("Debug: User chose to continue.")  # Logs user decision
            self.process_next_page(frames)  # Continue to the next page
        else:
            print("Debug: User chose to stop.")  # Logs user decision
            self.speak("Stopping the reading process as per your request.")
            self.central_widget.setCurrentWidget(self.init_screen)

    
    def display_detected_frame(self, detected_frame):
        """Display the detected frame in the UI"""
        # Ensure the output directory exists
        frame_path = "/Users/nagarjuna/FInal_Project/output_frames"
        os.makedirs(frame_path, exist_ok=True)
        frame_file = os.path.join(frame_path, "detected_frame.jpg")

        # Save the detected frame as an image file
        cv2.imwrite(frame_file, detected_frame)  # Save the detected frame to file

        # Load the image file into a QPixmap
        pixmap = QPixmap(frame_file)

        # Set the QPixmap in the detected_frame_label
        self.detected_frame_label.setPixmap(pixmap)
        self.detected_frame_label.setScaledContents(True)  # Scale the image to fit the label

        # Switch to the detected frame screen
        self.central_widget.setCurrentWidget(self.detected_frame_screen)



# Run the app
app = QApplication(sys.argv)
window = JarvisApp()
window.show()
sys.exit(app.exec_())
