import cv2
import threading
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Path to your video
VIDEO_PATH = "videos/bus1.mp4"

# Bus configuration
TOTAL_SEATS = 40

# Global data
passenger_count = 0
available_seats = TOTAL_SEATS
crowd_level = "Low"

# Function to process video
def process_video():
    global passenger_count, available_seats, crowd_level

    cap = cv2.VideoCapture(VIDEO_PATH)

    # ✅ Video open check (ADDED CORRECTLY)
    if not cap.isOpened():
        print("❌ ERROR: Video not found")
        return
    else:
        print("✅ Video opened successfully")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("🔁 Restarting video...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Run YOLO detection
        results = model(frame)

        count = 0

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # Class 0 = person
                    count += 1

        passenger_count = count
        available_seats = max(TOTAL_SEATS - passenger_count, 0)

        # Crowd level logic
        if passenger_count < 15:
            crowd_level = "Low"
        elif passenger_count < 30:
            crowd_level = "Medium"
        else:
            crowd_level = "High"

# Start detection in separate thread
def start_ai_detection():
    thread = threading.Thread(target=process_video)
    thread.daemon = True
    thread.start()

# Function to send data to app.py
def get_bus_data(bus_id):
    return {
        "passengers": passenger_count,
        "available": available_seats,
        "crowd": crowd_level
    } 
      
