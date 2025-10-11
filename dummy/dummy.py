from flask import Flask, render_template, jsonify
import pandas as pd
import os
import threading
import cv2
import csv
import time
import math
from datetime import datetime
from inference_sdk import InferenceHTTPClient

# ================== CONFIG ==================
API_URL = "https://serverless.roboflow.com"
API_KEY = "ZFrihLfyssn0VAOzwxhM"           # ✅ Your Roboflow API key
MODEL_ID = "microplastic-lstyl/1"          # ✅ Your model ID
CAPTURE_INTERVAL = 1                       # seconds between captures
CAMERA_INDEX = 0                           # 0 = laptop cam, 1/2 = USB microscope
CSV_FILE = "detection_results.csv"
MICRON_PER_PIXEL = 2.0                     # 🔧 Update this after microscope calibration

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
        writer.writerow(["Timestamp", "Class", "Confidence", "X", "Y", "Width", "Height", "ParticleSize_µm"])

# ================== BACKGROUND DETECTION ==================
def capture_and_detect():
    if not cap.isOpened():
        print("❌ Error: Could not open USB microscope. Try CAMERA_INDEX = 0, 1, 2.")
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
        try:
            result = client.infer(image_path, model_id=MODEL_ID)
        except Exception as e:
            print("⚠ Inference failed:", e)
            time.sleep(CAPTURE_INTERVAL)
            continue
        # Initialize dictionary to count particles
        particle_counts = {}

        # Process predictions
        if result.get("predictions"):
            for pred in result["predictions"]:
                class_name = pred["class"]
                confidence = pred["confidence"]
                x, y = int(pred["x"]), int(pred["y"])
                width, height = int(pred["width"]), int(pred["height"])
                particle_counts[class_name] = particle_counts.get(class_name, 0) + 1

                # Calculate particle size in µm (diameter)
                width_um = width * MICRON_PER_PIXEL
                height_um = height * MICRON_PER_PIXEL
                diameter_um = math.sqrt(width_um * height_um)

                print(f"Detected: {class_name} ({confidence:.2f}) | Size ≈ {diameter_um:.2f} µm")

                # Optional: Draw bounding box and label
                cv2.rectangle(enhanced, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(enhanced, f"{class_name} {confidence:.2f}", (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Save to CSV
                with open(CSV_FILE, mode="a", newline="") as f:
                    writer = csv.writer(f)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([
                        timestamp, class_name, confidence, x, y, width, height, round(diameter_um, 2)
                    ])
        else:
            print("No microplastic detected.")
        # Save counts of all particle types in CSV as an extra row
        if particle_counts:
            with open(CSV_FILE, mode="a", newline="") as f:
                writer = csv.writer(f)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for cls, count in particle_counts.items():
                    writer.writerow([timestamp, f"{cls}_count", count, "", "", "", "", ""])

        # Save the annotated frame
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
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return jsonify({"error": "No results yet"})

    df = pd.read_csv(CSV_FILE, encoding="cp1252")
    if df.empty:
        return jsonify({"error": "No data"})

    latest_time = df.tail(1)["Timestamp"].values[0]
    latest_group = df[df["Timestamp"] == latest_time]
    # 🚨 Drop Timestamp before sending
    latest_group = latest_group.drop(columns=["Timestamp"], errors="ignore").where(pd.notnull(latest_group), None)

    return jsonify(latest_group.to_dict(orient="records"))

@app.route("/all_results")
def get_all_results():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return jsonify({"error": "No results yet"})

    df = pd.read_csv(CSV_FILE, encoding="cp1252")
        # 🚨 Drop timestamp + convert NaN → None
    df = df.drop(columns=["Timestamp"], errors="ignore").where(pd.notnull(df), None)
    return jsonify(df.to_dict(orient="records"))
#display details for visualization
@app.route("/latest_agg")
def get_latest_agg():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return jsonify({"error": "No results yet"})

    df = pd.read_csv(CSV_FILE, encoding="cp1252")
    if df.empty:
        return jsonify({"error": "No data"})

    if "Timestamp" not in df.columns:
        return jsonify({"error": "CSV missing Timestamp column"})

    # Drop summary rows that don’t have numeric confidence values
    df_clean = df[pd.to_numeric(df["Confidence"], errors="coerce").notnull()]

    if df_clean.empty:
        return jsonify({"error": "No detection data available"})

    latest_time = df_clean["Timestamp"].iloc[-1]
    latest_df = df_clean[df_clean["Timestamp"] == latest_time]


    type_counts = {}
    type_sizes = {}
    size_cats = {"Small": 0, "Medium": 0, "Large": 0}
    total = 0
    confidences = []

    # Define dangerous priority order
    danger_priority = ["PS", "LDPE", "HDPE", "PET"]

    for _, row in latest_df.iterrows():
        cls = str(row["Class"]).upper()
        if cls.endswith("_COUNT"):
            continue

        conf = float(row.get("Confidence", 0))
        if conf > 0:
            confidences.append(conf)

        particle_size = float(row.get("ParticleSize_µm", 0))
        size_mm = particle_size / 1000.0

        # Count per type
        type_counts[cls] = type_counts.get(cls, 0) + 1
        type_sizes[cls] = type_sizes.get(cls, 0) + particle_size
        total += 1

        # Size categories
        if size_mm <= 0.5:
            size_cats["Small"] += 1
        elif size_mm <= 1.5:
            size_cats["Medium"] += 1
        else:
            size_cats["Large"] += 1

    # Average confidence
    avg_conf = (sum(confidences) / len(confidences)) if confidences else 0

    # Most common type
    most_common = max(type_counts, key=type_counts.get) if total > 0 else None

    # Largest average size
    largest_avg_type, largest_avg_value = None, 0
    for t, total_size in type_sizes.items():
        avg_size = total_size / type_counts[t]
        if avg_size > largest_avg_value:
            largest_avg_value = avg_size
            largest_avg_type = t

    # Determine most dangerous based on priority and presence
    most_dangerous = None
    for p in danger_priority:
        if type_counts.get(p, 0) > 0:
            most_dangerous = p
            break

    return jsonify({
        "type_counts": type_counts,
        "size_cats": size_cats,
        "total": total,
        "avg_confidence": avg_conf * 100,  # percentage
        "most_common": most_common,
        "largest_avg_size": {
            "type": largest_avg_type,
            "size_um": round(largest_avg_value, 2)
        },
        "most_dangerous": most_dangerous
    })


# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
