import cv2
import threading
import numpy as np
import time
from ultralytics import YOLO

model = YOLO("yolov8s.pt")

# 🔵 QUALITY CONTROL (100 = best quality)
QUALITY = 100   # try: 100, 80, 60, 40, 20

def apply_quality(frame, quality):
    if quality == 100:
        return frame

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', frame, encode_param)

    if not result:
        return frame

    decimg = cv2.imdecode(encimg, 1)
    return decimg


BUS_SEATS = {
    1: 18,
    2: 20,
    3: 16
}

VIDEO_PATHS = {
    1: "videos/bus1.mp4",
    2: "videos/bus2.mp4",
    3: "videos/bus3.mp4"
}

bus_data = {
    1: {"passengers": 0, "available": 18, "crowd": "Low"},
    2: {"passengers": 0, "available": 20, "crowd": "Low"},
    3: {"passengers": 0, "available": 16, "crowd": "Low"}
}

latest_frames = {
    1: None,
    2: None,
    3: None
}

SEAT_POSITIONS = {
    1: [(50,100,150,200),(160,100,260,200),(270,100,370,200)],
    2: [(60,120,160,220),(180,120,280,220),(300,120,400,220)],
    3: [(70,130,170,230),(190,130,290,230),(310,130,410,230)]
}


def process_video(bus_id):

    cap = cv2.VideoCapture(VIDEO_PATHS[bus_id])

    if not cap.isOpened():
        print(f"❌ Could not open video for Bus {bus_id}")
        return

    print(f"✅ AI started for Bus {bus_id}")

    prev_passengers = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 480))

        # 🔵 APPLY QUALITY ONLY
        frame = apply_quality(frame, QUALITY)

        # ✅ SPEED MEASUREMENT START
        start_time = time.time()

        results = model(frame)

        # ✅ SPEED MEASUREMENT END
        end_time = time.time()

        fps = 1 / (end_time - start_time)

        print(f"Bus {bus_id} FPS: {fps:.2f}")

        passengers = 0
        person_boxes = []

        for r in results:
            for box in r.boxes:

                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf > 0.3:

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(frame,
                                  (x1, y1),
                                  (x2, y2),
                                  (0, 255, 0),
                                  2)

                    passengers += 1
                    person_boxes.append((x1, y1, x2, y2))

        passengers = int((passengers + prev_passengers) / 2)
        prev_passengers = passengers

        # Seat visualization only
        seat_regions = SEAT_POSITIONS.get(bus_id, [])

        for seat in seat_regions:
            sx1, sy1, sx2, sy2 = seat
            occupied = False

            for (x1, y1, x2, y2) in person_boxes:
                if not (x2 < sx1 or x1 > sx2 or y2 < sy1 or y1 > sy2):
                    occupied = True
                    break

            color = (0, 0, 255) if occupied else (255, 0, 0)
            cv2.rectangle(frame, (sx1, sy1), (sx2, sy2), color, 2)

        capacity = BUS_SEATS[bus_id]

        available = capacity - passengers
        if available < 0:
            available = 0

        occupancy = passengers / capacity

        if occupancy < 0.4:
            crowd = "Low"
        elif occupancy < 0.75:
            crowd = "Medium"
        else:
            crowd = "High"

        bus_data[bus_id] = {
            "passengers": passengers,
            "available": available,
            "crowd": crowd
        }

        latest_frames[bus_id] = frame


def start_ai_detection():

    for bus_id in VIDEO_PATHS:

        thread = threading.Thread(
            target=process_video,
            args=(bus_id,)
        )

        thread.daemon = True
        thread.start()


def get_bus_data(bus_id):

    return bus_data.get(bus_id, {
        "passengers": 0,
        "available": BUS_SEATS.get(bus_id, 15),
        "crowd": "Low"
    })


def get_frame(bus_id):

    frame = latest_frames.get(bus_id)

    if frame is None:
        return None

    ret, buffer = cv2.imencode('.jpg', frame)

    if not ret:
        return None

    return buffer.tobytes()