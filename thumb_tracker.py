from click import command
import mediapipe as mp
import cv2
import time
import math
import serial


BAUD_RATE = 115200
SEND_INTERVAL = 0.4

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

running = True

arduino = None

try:
        arduino = serial.Serial("COM3", BAUD_RATE, timeout=0.1)
        time.sleep(2)
        print("arduino connected")
except:
     print("arduino not found")

THUMB_MIN = 40
THUMB_MAX = 300

THUMB_MIN_OT = 0
THUMB_MAX_OT = 180


thumb_value = None
previous_value = None

last_command = "STOP"

def map_value(value, in_min, in_max, out_min, out_max):

    value = max(in_min, min(value, in_max))
    output = (
         (value - in_min)
         * (out_max - out_min)
         / (in_max - in_min)
         + out_min
    )

    return int(output)

def send_thumb_value(value):
     global prev_thumb_value
     if arduino is None:
        return

        if prev_thumb_value is None:
             prev_thumb_value = current_value
             return
        

        difference = current_value - prev_thumb_value 

        if difference > 2:
             command = "EXTEND/n"

        elif difference < -2:
            command = "RETRACT/n"
       
        else:
                command = "STOP/n"
    
        try:
            arduino.write(command.encode())

        except Exception as e:
             print("serial error:", e)

             previous_value = current_value

             return command

def main():

    cv2.namedWindow(
        "thumb tracking",
        cv2.WINDOW_NORMAL
    )
    
    cv2.resizeWindow(
        "thumb tracking",
        960,
        720
    )

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    ) as hands:
        while running:
            attempt = 0
            success, frame = cap.read()
            while not success and attempt < 5:
                time.sleep(0.2)
                success, frame = cap.read()
                attempt += 1
            if not success:
                print("Failed to read frame")
                break

            frame = cv2.flip(frame, 1)
            h,w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                    )

                    thumb_tip = hand_landmarks.landmark[
                         mp_hands.HandLandmark.THUMB_TIP
                    ]

                    ring_mcp = hand_landmarks.landmark[
                         mp_hands.HandLandmark.RING_FINGER_MCP
                    ]

                    thumb_x = int(thumb_tip.x * w)
                    thumb_y = int(thumb_tip.y * h)

                    ring_x = int(ring_mcp.x *w)
                    ring_y = int(ring_mcp.y *h)

                    distance = math.sqrt(
                         (thumb_x - ring_x) ** 2 +
                         (thumb_y - ring_y) ** 2
                    )

                    thumb_value = int(
                        (distance - THUMB_MIN)
                        / (THUMB_MAX - THUMB_MIN)
                        *100
                    )

                    thumb_value = max(
                         0,
                         min(100, thumb_value)
                    )

                    print(
                         "distance:",
                         distance,
                         "thumb_position:",
                         thumb_value,
                   )

                    send_thumb_value(thumb_value)

                    cv2.line(
                         frame,
                         (thumb_x, thumb_y),
                         (ring_x, ring_y),
                         (255, 0, 0),
                         3
                    )

                    cv2.putText(
                         frame,
                         f"Thumb: {thumb_value}%",
                         (30, 50),
                         cv2.FONT_HERSHEY_PLAIN,
                         1,
                         (0, 255, 0),
                         2
                    )

                    finger_tips = {
                            "Thumb": hand_landmarks.landmark[4],
                            "Index": hand_landmarks.landmark[8],
                            "Middle": hand_landmarks.landmark[12],
                            "Ring": hand_landmarks.landmark[16],
                            "Pinky": hand_landmarks.landmark[20],
                    }

                    for name, landmark in finger_tips.items():
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv2.putText(
                            frame,
                            name,
                            (x, y - 10),
                            cv2.FONT_HERSHEY_PLAIN,
                            0.5,
                            (225,225, 255),
                            1,
                        )
                


            cv2.imshow("thumb_tracking", 
                       frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
if __name__=="__main__":
        main()
