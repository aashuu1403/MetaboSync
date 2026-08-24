import cv2
import mediapipe as mp
import numpy as np
import requests

# Initialize MediaPipe Pose components
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """Calculates the angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

cap = cv2.VideoCapture(0)

# Tracking Variables
rep_count = 0
current_state = "STANDING"
min_angle_in_rep = 180  
last_score = 0          

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Isolate landmarks to check both coordinates AND visibility
            hip_landmark = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            knee_landmark = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            ankle_landmark = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            
            # Extract (x, y) coordinates
            hip = [hip_landmark.x, hip_landmark.y]
            knee = [knee_landmark.x, knee_landmark.y]
            ankle = [ankle_landmark.x, ankle_landmark.y]
            
            # TUNED SENSITIVITY FILTERS
            if (hip_landmark.visibility > 0.5 and 
                knee_landmark.visibility > 0.5 and 
                ankle_landmark.visibility > 0.5):
                
                # Calculate the real-time knee angle
                knee_angle = calculate_angle(hip, knee, ankle)
                
                # 1. Detect moving down 
                if knee_angle < 135 and current_state == "STANDING":
                    current_state = "DOWN"
                
                # 2. Track the lowest depth while down
                if current_state == "DOWN":
                    if knee_angle < min_angle_in_rep:
                        min_angle_in_rep = knee_angle
                        
                # 3. Detect standing back up 
                if knee_angle > 150 and current_state == "DOWN":
                    current_state = "STANDING"
                    rep_count += 1
                    
                    if min_angle_in_rep <= 90:
                        last_score = 100
                    else:
                        last_score = max(0, int((160 - min_angle_in_rep) / (160 - 90) * 100))
                        
                    min_angle_in_rep = 180 

                # Visualize the live angle over the knee
                cv2.putText(image, str(int(knee_angle)), 
                            tuple(np.multiply(knee, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Render the UI Dashboard
            cv2.rectangle(image, (0,0), (280,120), (24,24,24), -1)
            cv2.putText(image, f'REPS: {rep_count}', (15,40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(image, f'FORM: {last_score}%', (15,90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (24, 219, 190), 2, cv2.LINE_AA)
            
        except:
            pass
        
        # Render the wireframe
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(24, 219, 190), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(219, 24, 76), thickness=2, circle_radius=2))               
        
        cv2.imshow('MetaboSync AI Tracker', image)

        # Press 'q' to break the loop, close the window, and send data to n8n
        if cv2.waitKey(10) & 0xFF == ord('q'):
            print("Workout complete. Sending data to pipeline...")
            
            payload = {
                "total_reps": rep_count,
                "average_form_score": last_score
            }
            
            try:
                # Send the POST request to your local n8n webhook
                response = requests.post("http://localhost:5678/webhook-test/squat-data", json=payload)
                if response.status_code == 200:
                    print("SUCCESS: Data successfully caught by n8n!")
                else:
                    print(f"ERROR: n8n returned status code {response.status_code}")
            except Exception as e:
                print(f"CONNECTION FAILED: {e}")
                
            break

    cap.release()
    cv2.destroyAllWindows()