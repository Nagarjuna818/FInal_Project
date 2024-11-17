from textbook_detection import results
from audio_module import transcribe_live_audio
from ocr_module import process_video
from title_detection import process_video1

# File paths
video_path = "/Users/ngujjula/Desktop/Final_Project/title.mp4"
video_path1 = "/Users/ngujjula/Desktop/Final_Project/input_videos/pages.mp4"
video_path2 = "/Users/ngujjula/Desktop/Final_Project/input.mp4"

def main():
    # Step 1: Detect if a book is found in the video
    bookfound = results(video_path2)
    if bookfound:
        print("Book detected! Running title detection model...")
        
        # Step 2: Detect title in the book
        result = process_video1(video_path)
        
        if result != "":
            print(f"Title Detected: {result}")
            print("Prompting user for voice input...")
            
            # Step 3: Ask user if they want to proceed
            response = transcribe_live_audio()
            
            if response and 'yes' in response.lower():
                print("User confirmed. Running OCR model...")
                
                # Step 4: Run OCR model
                process_video(video_path1, interval_seconds=5, similarity_threshold=0.8)
            else:
                print("User did not confirm. OCR model will not be run.")
        else:
            print("No title detected in the book.")
    else:
        print("No book detected in the video.")

# Ensure that the main function runs only when this script is executed directly
if __name__ == "__main__":
    main()
