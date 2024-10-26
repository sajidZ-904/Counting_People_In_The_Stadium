# -*- coding: utf-8 -*-
"""Counting_People.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bxikwodoOyL7eptimIDkw9Ot3j__m7Vx

# People Counting with YOLO in Video

## Objective
This notebook implements a computer vision solution to count the number of people entering and exiting the street from a designated area in a video using the YOLO object detection algorithm.

## Approach
1. **Load YOLO Model**: The YOLO model is loaded with pre-trained weights and configuration files.
2. **Process Video**: Each frame of the video is analyzed to detect people. The count of people entering and exiting is tracked.
3. **Display Results**: The processed frames are displayed, and the final counts are printed.

## Instructions
1. Make sure you upload the required YOLO files (`yolov3.weights`, `yolov3.cfg`, `coco.names`) to the Colab environment.
2. Upload your video file.
3. Run the notebook cells sequentially.
4. Download the output video with the counts annotated.

## Evaluation
The solution will be evaluated based on accuracy, efficiency, code structure, and creativity in handling edge cases.

# Import Necessary Libraries
"""

# Install required libraries
!pip install tensorflow==2.11.0
!pip install opencv-python
!pip install opencv-python-headless
!pip install numpy
!pip install matplotlib
!pip install pillow

# Download YOLOv3 weights, config, and names file
!wget https://pjreddie.com/media/files/yolov3.weights -O yolov3.weights
!wget https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg?raw=true -O yolov3.cfg
!wget https://github.com/pjreddie/darknet/blob/master/data/coco.names?raw=true -O coco.names

"""# Import Libraries and Load the Video"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from google.colab.patches import cv2_imshow

# Load YOLO model
def load_yolo_model():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    # Get the indices of the output layers, reshaping if necessary
    output_layers_indices = net.getUnconnectedOutLayers()
    # If output_layers_indices is a 1D array, reshape it to a 2D array
    if output_layers_indices.ndim == 1:
        output_layers_indices = output_layers_indices.reshape(1, -1)
    # Access the first element of each inner list (or the single element if it's a 1D array)
    output_layers = [layer_names[i[0] - 1] for i in output_layers_indices]
    return net, output_layers

# Load video
video_path = "video.mp4"  # Update this path after uploading your video
cap = cv2.VideoCapture(video_path)

"""#  Define Functions for Object Detection and Counting People"""

# Load YOLO model
net, output_layers = load_yolo_model()

# Count variables
enter_count = 0
exit_count = 0

# Define detection function
def detect_people(frame):
    global enter_count, exit_count

    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # Confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-max suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = (0, 255, 0)  # Green color for detected boxes
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Count people entering or exiting
            if label == 'person':
                if y < height // 2:  # Condition for entering
                    enter_count += 1
                else:  # Condition for exiting
                    exit_count += 1

    return frame

# Load class labels
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

"""# Process the video frame by frame"""

# Process video frames
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_people(frame)

    # Display the result
    cv2_imshow(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture
cap.release()

# Print counts
print(f"People Entered: {enter_count}, People Exited: {exit_count}")

"""# Save the Output Video"""

# Save the output video
output_path = "output_video.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

cap = cv2.VideoCapture(video_path)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_people(frame)
    out.write(frame)

cap.release()
out.release()
print("Output video saved.")