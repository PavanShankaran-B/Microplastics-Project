# Smart Portable Sensor for Real-Time Microplastic Detection

## Overview
This project presents a smart portable sensor system for the real-time detection and quantification of microplastics in water. The system combines UV fluorescence, imaging, and AI/ML-based classification to provide a low-cost, battery-powered, and field-deployable alternative to conventional laboratory methods.

Traditional microplastic detection methods often depend on bulky and expensive instruments such as FTIR and Raman spectroscopy. This project aims to reduce that dependency by offering a portable, efficient, and practical solution for on-site water quality monitoring.

## Problem Statement
Microplastics have become a major environmental concern due to their presence in freshwater, oceans, and even drinking water. Existing detection approaches are often expensive, time-consuming, and restricted to laboratory use.

This project addresses the need for:
- Real-time detection of microplastics in water
- Low-cost and portable monitoring
- Reduced reliance on advanced laboratory instruments
- Faster and more accessible field-based analysis

## Proposed Solution
The proposed solution is a Portable Optical Sensor System designed to integrate UV fluorescence, imaging, and AI/ML for the detection and quantification of microplastics in real time.

The system is designed to:
- Provide real-time microplastic detection in water
- Reduce dependency on bulky and expensive instruments like FTIR and Raman
- Enable on-site and rapid monitoring in remote or resource-limited environments
- Improve detection accuracy using AI/ML classification
- Support field-friendly and scalable environmental monitoring

## Workflow
The system follows this process:

Water Sample → Optical Detection → AI/ML Classification → Real-Time Results

## Key Features
- Real-time microplastic detection
- Portable and battery-powered design
- UV fluorescence-assisted sensing
- AI/ML-based particle classification
- Low-cost alternative to laboratory equipment
- Suitable for field deployment
- Scalable for cloud or mobile dashboard integration

## Innovation and Uniqueness
- **Low-Cost Alternative**  
  Uses simple optical sensing instead of expensive laboratory instruments.

- **AI-Powered Detection**  
  Machine learning helps classify particles by optical signatures in real time.

- **Portable and Battery-Based**  
  Designed for operation without complex lab infrastructure.

- **Fast and On-Site Analysis**  
  Provides quick results with minimal sample preparation.

- **Scalable System Design**  
  Can be extended with IoT, cloud logging, and mobile dashboards.

## Technologies Used

### Programming Languages
- C++
- Python

### Tools and Frameworks
- Arduino IDE
- OpenCV
- CNN-based classification
- IoT integration with WiFi logging
- Cloud / Mobile Dashboard support

## Hardware Components
- ESP32-CAM (OV2640)
- UV LED with MOSFET
- Peristaltic Pump with Driver
- USB Microscope
- Li-ion Battery

## Applications
- Water quality monitoring
- Freshwater and environmental analysis
- Microplastic pollution detection
- Research and academic studies
- Smart environmental monitoring systems
- Field-based inspection and testing

## Benefits
- Portable and practical for field use
- Lower cost compared to lab-based methods
- Faster detection and monitoring
- Supports wider environmental deployment
- Improves accessibility in remote and resource-limited areas

## Future Scope
- Improve model accuracy with larger datasets
- Build a dedicated mobile app
- Add real-time cloud data storage and analytics
- Enhance particle characterization
- Develop a compact commercial prototype
- Expand monitoring to different water sources and environments

## Folder Structure
```text
Microplastic-Detection-Project/
│
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── image_processing.py
│   ├── classification_model.py
│   ├── sensor_control.py
│   └── utils.py
│
├── hardware/
│   ├── esp32_cam_code.ino
│   ├── circuit_diagram.png
│   └── component_list.txt
│
├── data/
│   ├── sample_images/
│   ├── processed_images/
│   └── dataset_info.txt
│
├── models/
│   └── trained_model.h5
│
├── outputs/
│   ├── logs/
│   └── results/
│
└── docs/
    ├── presentation.pptx
    └── research_references.txt

## author
    Mythreyan S