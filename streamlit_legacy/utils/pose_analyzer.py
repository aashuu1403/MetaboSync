import cv2
import numpy as np
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_drawing_styles = mp.solutions.drawing_styles

def calculate_angle(a, b, c):
    a = np.array(a)  # First point (e.g., Hip)
    b = np.array(b)  # Mid point (e.g., Knee)
    c = np.array(c)  # End point (e.g., Ankle)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def analyze_pose(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        return None, "Error: Could not load image."

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_height, image_width, _ = image.shape

    with mp_pose.Pose(static_image_mode=True, model_complexity=1, enable_segmentation=False) as pose:
        results = pose.process(image_rgb)

        if not results.pose_landmarks:
            return image, "No pose landmarks detected."

        # Draw the pose annotation on the image
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        # Extract landmarks and calculate angles (example for knee)
        landmarks = results.pose_landmarks.landmark
        
        # Example: Left Knee Angle
        try:
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * image_width,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * image_height]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x * image_width,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y * image_height]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x * image_width,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * image_height]
            
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            cv2.putText(annotated_image, f"L_Knee: {int(left_knee_angle)}", 
                        tuple(np.multiply(left_knee, [1, 1]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        except:
            left_knee_angle = None
            cv2.putText(annotated_image, "L_Knee: N/A", 
                        (50,50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        return annotated_image, {"left_knee_angle": left_knee_angle}

if __name__ == '__main__':
    # Example usage (replace 'test_image.jpg' with your image file)
    # Make sure to have a test_image.jpg in the same directory or provide full path
    processed_image, analysis_results = analyze_pose('test_image.jpg')
    
    if processed_image is not None and isinstance(analysis_results, dict):
        cv2.imwrite('annotated_test_image.jpg', processed_image)
        print("Analysis Results:", analysis_results)
    else:
        print(analysis_results) # This will print the error message
