from flask import Flask, render_template, jsonify
import pandas as pd
import os
import threading
import cv2
import csv
import time
import math
from datetime import datetime
from ultralytics import YOLO  # ✅ Using your local trained YOLOv8 model

# ================== CONFIG ==================
MODEL_PATH = r"C:\Users\Eahumalai\Downloads\microplastic.v1i.yolov8\runs\detect\train2\weights\best.pt"            # ✅ Your trained YOLOv8 model file
CAPTURE_INTERVAL = 1                       # seconds between captures
CAMERA_INDEX = 0                           # 0 = laptop cam, 1/2 = USB microscope
CSV_FILE = "detection_results.csv"
MICRON_PER_PIXEL = 2.0                     # 🔧 Microscope calibration

# ================== INIT ==================
app = Flask(__name__)

# ✅ Load your trained YOLOv8 model
print("🔄 Loading YOLOv8 model...")
model = YOLO(MODEL_PATH)
print("✅ Model loaded successfully!")

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create CSV header if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Class", "Confidence", "X", "Y", "Width", "Height", "ParticleSize_µm"])

# ================== BACKGROUND DETECTION ==================
def capture_and_detect():
    if not cap.isOpened():
        print("❌ Error: Could not open USB microscope. Try CAMERA_INDEX = 0, 1, or 2.")
        return

    print("✅ Starting USB microscope capture and microplastic detection...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image.")
            continue

        # ---- Image Enhancement ----
        alpha, beta = 1.5, 40
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        # Save temporary image
        image_path = "latest_capture.jpg"
        cv2.imwrite(image_path, enhanced)

        # Run YOLOv8 detection (local model)
        try:
            results = model.predict(source=image_path, conf=0.5, save=False, verbose=False)
        except Exception as e:
            print("⚠ Inference failed:", e)
            time.sleep(CAPTURE_INTERVAL)
            continue

        particle_counts = {}

        # Process predictions
        if len(results) > 0:
            for r in results:
                for box in r.boxes:
                    class_id = int(box.cls)
                    class_name = model.names[class_id]
                    confidence = float(box.conf)
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    width = x2 - x1
                    height = y2 - y1
                    particle_counts[class_name] = particle_counts.get(class_name, 0) + 1

                    # Calculate particle size in µm
                    width_um = width * MICRON_PER_PIXEL
                    height_um = height * MICRON_PER_PIXEL
                    diameter_um = math.sqrt(width_um * height_um)

                    print(f"Detected: {class_name} ({confidence:.2f}) | Size ≈ {diameter_um:.2f} µm")

                    # Draw bounding box and label
                    cv2.rectangle(enhanced, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(enhanced, f"{class_name} {confidence:.2f}", (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Save to CSV
                    with open(CSV_FILE, mode="a", newline="") as f:
                        writer = csv.writer(f)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([
                            timestamp, class_name, confidence, x1, y1, width, height, round(diameter_um, 2)
                        ])
        else:
            print("No microplastic detected.")

        # Log total count per frame
        if particle_counts:
            with open(CSV_FILE, mode="a", newline="") as f:
                writer = csv.writer(f)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for cls, count in particle_counts.items():
                    writer.writerow([timestamp, f"{cls}_count", count, "", "", "", "", ""])

        # Save annotated frame
        cv2.imwrite("latest_annotated.jpg", enhanced)

        # Optional: Show video feed (press 'q' to quit)
        cv2.imshow("USB Microscope Feed", enhanced)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(CAPTURE_INTERVAL)

    cap.release()
    cv2.destroyAllWindows()

# ================== BACKGROUND THREAD ==================
threading.Thread(target=capture_and_detect, daemon=True).start()

# ================== FLASK ROUTES ==================
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/results")
def get_latest_result():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No results yet"})
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return jsonify({"error": "No data"})

    latest_time = df.tail(1)["Timestamp"].values[0]
    latest_group = df[df["Timestamp"] == latest_time]
    latest_group = latest_group.drop(columns=["Timestamp"], errors="ignore")
    return jsonify(latest_group.to_dict(orient="records"))

@app.route("/all_results")
def get_all_results():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No results yet"})
    df = pd.read_csv(CSV_FILE)
    df = df.drop(columns=["Timestamp"], errors="ignore")
    return jsonify(df.to_dict(orient="records"))

# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
