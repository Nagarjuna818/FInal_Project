# import nltk
import re
# import easyocr
import cv2
import pytesseract
from isbnlib import meta, is_isbn10, is_isbn13
# from gtts import gTTS
# from IPython.display import Audio
import pyttsx3 

engine = pyttsx3.init()

rate = engine.getProperty('rate')  # Get current speech rate
engine.setProperty('rate', rate - 50)

# Assuming 'text' variable holds the text you want to convert


# Function to extract text from video
def video_to_text(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read() # Read only the first frame
    cap.release()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return pytesseract.image_to_string(gray)
    else:
        return ""

# Function to check if text is a book title
def is_book_title(text):
    if is_isbn10(text) or is_isbn13(text):
        book_info = meta(text)
        if book_info:
            return book_info['Title']
    return None

# Main function
def process_video1(video_path):

    text = video_to_text(video_path)
    # Remove "g)" and surrounding non-alphanumeric characters
    text = re.sub(r'\W*g\)\W*', '', text)
    # Extract title using regular expression
    match = re.search(r'An Introduction.*?Leaming.*?with Applications in R', text, re.DOTALL)
    if match:
        title = match.group(0).strip()
        print(f"Potential Title Detected: {title}")  # Debugging line
        engine.say(f"The detected book title is: {title}")
        engine.runAndWait()
        return f"Book Title: {title}"
    # Extract title using the is_book_title function
    else:
        return text.strip()


# Example usage
# video_path = '/Users/ngujjula/Desktop/Final_Project/title.mp4'
# output_text = process_video1(video_path)
# # tts = gTTS(output_text)
# engine.say(output_text)
# engine.runAndWait()

# tts.save("output.mp3")
# Audio("output.mp3", autoplay=True)