Computer Vision Controlled Prosthetics

This project explores the use of computer vision alongside EMG signal data to control a Prototype prosthetic device. Using a webcam and Google MediaPipe hand-tracking data, the program tracks the positions of a hand and fingers and relays the data to the Arduino to be controlled by linear actuators.

Preface:
This project uses the vision-controlled data to test and experiment with the prosthetic prototype and the limitations involved. The final device will utilize the EMG muscle sensors to relay data from a person's movements.

How It Works (thumb_tracker):
1. Hand Tracking: MediaPipe detects the hand landmarks through the camera
2. Measurement: The program calculates the distance between the thumb tip and the ring finger MCP joint
3. Value Mapping: The measured distance is mapped to a range of 0-180
4. Smoothing: The program utilizes an exponential moving average that reduces changes/variations in the tracking data
5. Arduino: Python sends the data to an Arduino over a USB serial connection
6. Actuator control: The Arduino sends the signals to several one-channel relays to control the direction of a linear actuator.
