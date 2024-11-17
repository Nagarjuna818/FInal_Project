import cv2
import pytesseract
from skimage.metrics import structural_similarity as compare_ssim
import os
import pyttsx3 
from audio_module import transcribe_live_audio

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)

def extract_frames(video_file, interval_seconds):
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
    return frames

def compare_frames(frame1, frame2):
    grayA = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    score, diff = compare_ssim(grayA, grayB, full=True)
    return score

def detect_page_turns(frames, similarity_threshold=0.8):
    page_turns = []
    for i in range(len(frames) - 1):
        score = compare_frames(frames[i], frames[i + 1])
        if score < similarity_threshold:
            page_turns.append(i + 1)
    return page_turns

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

def process_video(video_file, interval_seconds=5, similarity_threshold=0.8):
    engine.say("Starting OCR process for the pages.")
    engine.runAndWait()

    frames = extract_frames(video_file, interval_seconds)
    page_turns = detect_page_turns(frames, similarity_threshold)

    for i, pagenum in enumerate(page_turns):
        text = extract_text_from_image(frames[pagenum])
        modify_text = f"{text} \nEnd of page {i+1}"

        engine.say(modify_text)
        engine.runAndWait()

        if i < len(page_turns) - 1:
            engine.say("Do you want to continue to the next page?")
            engine.runAndWait()
            response = transcribe_live_audio()
            if 'continue' in response:
                continue
            else:
                break
