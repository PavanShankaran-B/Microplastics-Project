from flask import Flask, render_template, jsonify
import pandas as pd
import os
import threading
import cv2
import csv
import time
from datetime import datetime
from inference_sdk import InferenceHTTPClient

# ================== CONFIG ==================
API_URL = "https://serverless.roboflow.com"
API_KEY = "ZFrihLfyssn0VAOzwxhM"   # ✅ Your Roboflow API key
MODEL_ID = "microplastic-lstyl/1" # ✅ Your model ID
CAPTURE_INTERVAL = 1              # seconds between captures
CAMERA_INDEX = 0                  # 0 = laptop cam, 1/2 = USB microscope
CSV_FILE = "detection_results.csv"

# ================== INIT ==================
app = Flask(__name__)
client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create CSV header if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Class", "Confidence", "X", "Y", "Width", "Height"])

# ================== BACKGROUND DETECTION ==================
def capture_and_detect():
    if not cap.isOpened():
        print("❌ Error: Could not open USB microscope. Try CAMERA_INDEX = 0,1,2")
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

        # Run inference
                # Run inference
        try:
            result = client.infer(image_path, model_id=MODEL_ID)
        except Exception as e:
            print("⚠️ Inference failed:", e)
            time.sleep(CAPTURE_INTERVAL)
            continue

        # Process predictions and draw boxes
        if result.get("predictions"):
            for pred in result["predictions"]:
                class_name = pred["class"]
                confidence = pred["confidence"]
                x, y = int(pred["x"]), int(pred["y"])
                width, height = int(pred["width"]), int(pred["height"])

                print(f"Detected: {class_name} ({confidence:.2f})")

                # ✅ Draw bounding box + label on frame
                cv2.rectangle(enhanced, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(enhanced, f"{class_name} {confidence:.2f}",
                            (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)

                # Save to CSV
                with open(CSV_FILE, mode="a", newline="") as f:
                    writer = csv.writer(f)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([timestamp, class_name, confidence, x, y, width, height])
        else:
            print("No microplastic detected.")

        # ✅ Save the annotated frame (with bounding boxes)
        cv2.imwrite("latest_annotated.jpg", enhanced)

        # ✅ Show in OpenCV window (debugging only)
        cv2.imshow("USB Microscope Feed", enhanced)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(CAPTURE_INTERVAL)

    cap.release()
    cv2.destroyAllWindows()

# Start detection in background thread
threading.Thread(target=capture_and_detect, daemon=True).start()

# ================== FLASK ROUTES ==================
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/results")
def get_latest_result():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return jsonify({"error": "No results yet"})

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return jsonify({"error": "No data"})

    # Get latest timestamp detections
    latest_time = df.tail(1)["Timestamp"].values[0]
    latest_group = df[df["Timestamp"] == latest_time]
    return jsonify(latest_group.to_dict(orient="records"))

@app.route("/all_results")
def get_all_results():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return jsonify({"error": "No results yet"})
    df = pd.read_csv(CSV_FILE)
    return jsonify(df.to_dict(orient="records"))

# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
