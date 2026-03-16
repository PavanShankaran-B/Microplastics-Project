Microplastics Detection System using ESP32 Camera and Machine Learning

Overview

Microplastics are extremely small plastic particles that pose serious environmental and health risks. Detecting these particles manually is difficult and time-consuming. This project proposes an **IoT-based microplastics detection system** that uses an **ESP32 camera module and a machine learning model** to automatically detect microplastics in captured images.

The system captures images using the ESP32 camera, processes them using a Python-based machine learning model, and identifies microplastic particles. The detection results are visualized through annotated images and performance metrics such as confusion matrices.

This solution aims to support **environmental monitoring and research** by providing a low-cost automated microplastics detection system.
---
Objectives

* Detect microplastics automatically using image processing and machine learning.
* Use an ESP32 camera module for capturing real-time images.
* Analyze captured images using a trained detection model.
* Provide detection results and evaluation metrics.
* Support environmental monitoring and research on microplastic pollution.
---
System Architecture

The system consists of three main components:

1. Image Capture

   * ESP32 camera captures images from the environment.
   * Images are transmitted to the processing system.

2. Image Processing and Detection

   * Python scripts process the captured images.
   * Machine learning algorithms detect microplastic particles.

3. Result Visualization

   * Detection results are displayed using annotated images.
   * Performance metrics such as confusion matrix are generated.
---
Technologies Used

Hardware

* ESP32 Camera Module
* Microcontroller

Software

* Python
* OpenCV
* Machine Learning algorithms
* Arduino IDE

Tools and Libraries

* NumPy
* Pandas
* Matplotlib
* Scikit-learn
* Flask (for web interface if used)
---
Project Structure

```
Microplastics-Project
│
├── arduino-esp32-master/       # ESP32 camera related libraries
├── dummy/                      # Testing scripts and confusion matrix results
│   └── confusion_matrix/
│
├── esp32_microplastic.ino      # ESP32 camera code
├── app.py                      # Main Python application
├── camera_test.py              # Camera testing script
├── camera_test_code.py         # Image capture testing
├── detection_results.csv       # Detection output data
├── latest_capture.jpg          # Captured image
├── latest_annotated.jpg        # Detection result image
└── README.md                   # Project documentation
```
---
How the System Works

1. The ESP32 camera captures images from the sample environment.
2. The captured image is transmitted to the processing system.
3. Python scripts analyze the image using image processing techniques.
4. The machine learning model detects microplastic particles.
5. The detected particles are highlighted in the output image.
6. Results are stored and evaluated using performance metrics.

---
Installation and Setup
1. Clone the Repository

```
git clone https://github.com/PavanShankaran-B/Microplastics-Project.git
cd Microplastics-Project
```
2. Install Required Python Libraries

```
pip install opencv-python
pip install numpy
pip install pandas
pip install matplotlib
pip install scikit-learn
```
3. Upload ESP32 Code

1. Open **Arduino IDE**
2. Connect the **ESP32 Camera Module**
3. Upload the file:

```
esp32_microplastic.ino
```
4. Run the Detection Program

```
python app.py
```
---
Output

The system produces:

* Captured images from the ESP32 camera
* Annotated images showing detected microplastics
* CSV files containing detection results
* Confusion matrix for model evaluation

Example outputs include:

* `latest_capture.jpg`
* `latest_annotated.jpg`
* `detection_results.csv`
---
Performance Evaluation

To evaluate the detection model, a **confusion matrix** is generated. This helps analyze:

* True Positives
* False Positives
* True Negatives
* False Negatives

These metrics help measure the accuracy and reliability of the detection model.
---
Applications

* Environmental monitoring
* Marine pollution analysis
* Water quality monitoring
* Research on plastic pollution
* Automated laboratory analysis
---
Future Improvements

* Improve model accuracy using deep learning models such as CNN.
* Integrate cloud storage for remote monitoring.
* Develop a real-time dashboard for visualization.
* Expand dataset for better training.
* Implement mobile notifications for detection alerts.
---
Contributors

PavanShankaran-B
---
License

This project is developed for educational and research purposes.
