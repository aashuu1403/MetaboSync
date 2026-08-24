import cv2
from app.core.pose_tracker import BiomechanicalTracker

def main():
    # Initialize our AI tracker
    tracker = BiomechanicalTracker()

    # Load your squat video
    cap = cv2.VideoCapture('squat_test.mp4')

    if not cap.isOpened():
        print("Error: Could not open the video file. Check the name and location.")
        return

    print("Processing video... Press 'q' on your keyboard to stop.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Video finished processing.")
            break

        # Pass the frame to our tracker
        processed_frame, results = tracker.process_frame(frame)

        # Display the output in a new window
        cv2.imshow('MetaboSync AI - Pose Tracking Test', processed_frame)

        # Wait 10ms between frames, break if 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Clean up when done
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()