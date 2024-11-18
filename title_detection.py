import re
import cv2
import pytesseract
from isbnlib import meta, is_isbn10, is_isbn13

def preprocess_frame(frame):
    """
    Preprocess a frame for better OCR results.
    - Convert to grayscale
    - Resize to enhance text visibility
    - Apply GaussianBlur and adaptive thresholding
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    processed = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return processed

def extract_text_from_frame(frame):
    """
    Extract text from a single processed video frame using pytesseract.
    """
    return pytesseract.image_to_string(frame)

def clean_text(text):
    """
    Clean OCR text to remove noise and normalize spaces.
    """
    # Remove non-alphanumeric characters except spaces, colons, commas, and hyphens
    cleaned = re.sub(r'[^\w\s:,\-\(\)]', '', text)
    # Remove fragments with fewer than 3 alphanumeric characters
    cleaned = ' '.join([word for word in cleaned.split() if len(word) > 2])
    return cleaned.strip()

def extract_title(text):
    """
    Extract the most probable book title from the text using regex and keyword matching.
    """
    cleaned_text = clean_text(text)
    print(f"Debug: Cleaned OCR Text:\n{cleaned_text}")  # Debugging to analyze cleaned OCR text

    # Patterns for exact titles and general title-like structures
    title_patterns = [
        r'An\s+Introduction\s+to\s+Statistical\s+Learning.*?with\s+Applications\s+in\s+R',  # Exact match
        r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+',  # General title-like patterns
    ]

    for pattern in title_patterns:
        match = re.search(pattern, cleaned_text, re.DOTALL)
        if match:
            return match.group(0).strip()

    # Fallback: Return cleaned text if no specific title is found
    return cleaned_text

def process_video1(video_path):
    """
    Main function to process the video and extract the book title.
    """
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Error: Unable to process the video."

    # Preprocess the frame
    processed_frame = preprocess_frame(frame)

    # Perform OCR on the preprocessed frame
    raw_text = extract_text_from_frame(processed_frame)
    print(f"Debug: Raw OCR Text:\n{raw_text}")  # Debugging to analyze raw OCR results

    # Extract the most likely title
    title = extract_title(raw_text)

    # Check for ISBN-based title as a fallback
    isbn_title = check_isbn_and_get_title(raw_text)
    title = isbn_title or title  # Prefer ISBN title if available

    return title or "No valid title detected."

def check_isbn_and_get_title(text):
    """
    Check if the extracted text contains an ISBN and fetch the book title if possible.
    """
    if is_isbn10(text) or is_isbn13(text):
        book_info = meta(text)
        if book_info and 'Title' in book_info:
            return book_info['Title']
    return None


# Example usage
video_path = '/Users/nagarjuna/FInal_Project/title.mp4'
output = process_video1(video_path)
print(output)
