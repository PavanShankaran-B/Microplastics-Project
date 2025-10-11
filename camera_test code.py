import cv2
import time
import csv
from datetime import datetime
from inference_sdk import InferenceHTTPClient

# ================== CONFIG ==================
API_URL = "https://serverless.roboflow.com"
API_KEY = "ZFrihLfyssn0VAOzwxhM"     # ✅ Your working API key
MODEL_ID = "microplastic-lstyl/1"    # ✅ Your model ID
CAPTURE_INTERVAL = 1                 # seconds between captures
CAMERA_INDEX = 0                   # 0 = laptop cam, 1/2 = USB microscope
CSV_FILE = "detection_results.csv"

# ================== INIT ==================
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # Use DirectShow backend

# Set resolution for microscope (HD clarity)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

# Create CSV file header (if empty)
with open(CSV_FILE, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Class", "Confidence", "X", "Y", "Width", "Height"])

if not cap.isOpened():
    print("❌ Error: Could not open USB microscope. Try CAMERA_INDEX = 0,1,2")
    exit()

print("✅ Starting USB microscope capture and microplastic detection...")

# ================== LOOP ==================
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture image.")
            continue

        # ---- Image Enhancement (brightness/contrast) ----
        alpha = 1.5   # Contrast control (1.0–3.0)
        beta = 40     # Brightness control (0–100)
        enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        # Save debug frame (to verify image is captured properly)
        cv2.imwrite("debug_frame.jpg", enhanced)

        # Save temporary image for detection
        image_path = "latest_capture.jpg"
        cv2.imwrite(image_path, enhanced)

        # Run ML detection on current frame
        result = client.infer(image_path, model_id=MODEL_ID)

        # Print detection results
        print("=== Detection Result ===")
        if result['predictions']:
            for pred in result['predictions']:
                class_name = pred['class']
                confidence = pred['confidence']
                x = int(pred['x'])
                y = int(pred['y'])
                width = int(pred['width'])
                height = int(pred['height'])

                print(f"Detected: {class_name} ({confidence:.2f})")

                # Draw bounding box + label
                cv2.rectangle(enhanced, (x, y), (x + width, y + height), (0, 255, 0), 2)
                cv2.putText(enhanced, f"{class_name} {confidence:.2f}",
                            (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)

                # Save results to CSV
                with open(CSV_FILE, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([timestamp, class_name, confidence, x, y, width, height])
        else:
            print("No microplastic detected.")

        print("========================")

        # Show live video with detections
        cv2.imshow("USB Microscope Feed", enhanced)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Capture every 1 second
        time.sleep(CAPTURE_INTERVAL)

except KeyboardInterrupt:
    print("🛑 Stopping detection...")

finally:
    cap.release()
    cv2.destroyAllWindows()
