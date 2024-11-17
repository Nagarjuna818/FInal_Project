from ultralytics import YOLO
import os
import pyttsx3
import cv2  # Assuming you use OpenCV to save frames
import numpy as np

# Initialize the text-to-speech engine
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)

# Load your trained model
model = YOLO('/Users/ngujjula/Desktop/Final_Project/best.pt')

def results(input_video):
    # Run the model on the video stream
    results = model(input_video, stream=True, vid_stride=5, imgsz=320)
    
    # Prepare output directory for saving detected frames
    output_dir = '/Users/ngujjula/Desktop/Final_Project/output_frames/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process results frame by frame
    for result in results:
        if result.boxes:
            for box in result.boxes:
                # Assuming class '0' represents a book
                if box.cls == 0:  
                    print("Book detected!")
                    engine.say("Textbook detected in the video.")
                    engine.runAndWait()

                    # Extract the frame (result.orig_img is assumed to be the frame in BGR format)
                    frame = np.array(result.orig_img)

                    # Save the detected frame
                    frame_filename = os.path.join(output_dir, 'detected_frame.jpg')
                    cv2.imwrite(frame_filename, frame)  # Save frame using OpenCV

                    return True  # Stop processing after detecting a book
    return False
