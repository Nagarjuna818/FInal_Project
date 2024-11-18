import cv2
import pytesseract
from skimage.metrics import structural_similarity as compare_ssim
import os
import pyttsx3
from audio_module import transcribe_live_audio

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)


def extract_frames(video_file, interval_seconds):
    """
    Extract frames from a video file at regular intervals.
    """
    vidcap = cv2.VideoCapture(video_file)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval_seconds)
    frame_count = 0
    frames = []
    success, image = vidcap.read()

    while success:
        if frame_count % interval_frames == 0:
            frames.append(image)
        success, image = vidcap.read()
        frame_count += 1

    vidcap.release()
    print(f"Debug: Extracted {len(frames)} frames from the video.")
    return frames


def compare_frames(frame1, frame2):
    """
    Compare two frames using Structural Similarity Index (SSIM).
    """
    grayA = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    score, _ = compare_ssim(grayA, grayB, full=True)
    return score


def detect_page_turns(frames, similarity_threshold=0.8):
    """
    Detect page turns based on frame similarity.
    """
    page_turns = []
    for i in range(len(frames) - 1):
        score = compare_frames(frames[i], frames[i + 1])
        if score < similarity_threshold:
            page_turns.append(i + 1)
    print(f"Debug: Detected page turns at indices: {page_turns}")
    return page_turns


def extract_text_from_image(image):
    """
    Extract text from a single image using pytesseract.
    """
    text = pytesseract.image_to_string(image)
    print("Debug: Extracted text from image.")
    return text.strip()


def process_video(video_file, interval_seconds=5, similarity_threshold=0.8):
    """
    Process a video file to extract text from frames corresponding to page turns.
    """
    try:
        # Start TTS process
        engine.say("Starting OCR process for the pages.")
        engine.runAndWait()

        # Extract frames and detect page turns
        frames = extract_frames(video_file, interval_seconds)
        if not frames:
            print("Debug: No frames extracted from the video.")
            engine.say("No frames extracted from the video. Unable to process OCR.")
            engine.runAndWait()
            return

        page_turns = detect_page_turns(frames, similarity_threshold)
        if not page_turns:
            print("Debug: No page turns detected.")
            engine.say("No page turns detected in the video. Unable to proceed.")
            engine.runAndWait()
            return

        # Iterate through detected pages
        for i, pagenum in enumerate(page_turns):
            text = extract_text_from_image(frames[pagenum])
            print(f"Debug: Text for page {i+1}: {text}")
            modify_text = f"Page {i+1}: {text} \nEnd of page {i+1}"

            # Speak the extracted text
            engine.say(modify_text)
            engine.runAndWait()

            # Ask user if they want to continue to the next page
            if i < len(page_turns) - 1:
                engine.say("Do you want to continue to the next page?")
                engine.runAndWait()
                response = transcribe_live_audio()
                if response and 'continue' in response.lower():
                    continue
                else:
                    print("Debug: User chose to stop.")
                    engine.say("Stopping the process as per your request.")
                    engine.runAndWait()
                    break
        else:
            print("Debug: All pages processed.")
            engine.say("OCR process completed. All pages have been processed.")
            engine.runAndWait()
    except Exception as e:
        print(f"Error: {e}")
        engine.say("An error occurred during OCR processing. Please try again.")
        engine.runAndWait()
