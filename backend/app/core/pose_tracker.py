import cv2
import mediapipe as mp
import numpy as np

class BiomechanicalTracker:
    def __init__(self):
        # Initialize MediaPipe Pose model
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # 1 is a good balance of speed and accuracy
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def calculate_angle(self, a, b, c):
        """
        Calculates the angle between three points.
        Useful for calculating squat depth (hip-knee-ankle) or back posture.
        """
        a = np.array(a) # First point (e.g., hip)
        b = np.array(b) # Mid point (e.g., knee)
        c = np.array(c) # End point (e.g., ankle)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def process_frame(self, frame):
        """
        Processes a single video frame, extracts landmarks, and draws connections.
        """
        # Convert BGR (OpenCV default) to RGB (MediaPipe requirement)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        
        # Make detection
        results = self.pose.process(image_rgb)
        
        # Convert back to BGR for OpenCV rendering
        image_rgb.flags.writeable = True
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Draw the biomechanical skeleton over the frame
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                image_bgr, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
        return image_bgr, results