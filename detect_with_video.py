import RPi.GPIO as GPIO
import time
import pygame
from threading import Thread
GPIO.setmode(GPIO.BCM)
import RPi.GPIO as GPIO
import serial
import pynmea2
import cv2
import numpy as np

port = serial.Serial("/dev/ttySOFT0", baudrate=4800, timeout=1)
BUZZER = 5
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
buzzState = False
GPIO.setup(BUZZER, GPIO.OUT)

TRIG = 23
ECHO = 24
pygame.mixer.init()


GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

net = cv2.dnn.readNet("tiny_yolov3_model.weights", "yolov3-tiny.cfg")
classes = ["traffic light",
                   "road markers",
                   "streets"]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))


class VideoStream:
    """Camera object that controls video streaming from the Picamera"""

    def __init__(self, resolution=(10, 10), framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True


class detect(Thread):
    def __int__(self):
        super(detect, self).__int__()
    def run(self):
        # Initialize video stream
        videostream = VideoStream(resolution=(1280, 720), framerate=30).start()
        time.sleep(1)

        # for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        while True:
            # Grab frame from video stream
            frame = videostream.read()

            height, width, channel = frame.shape

            # Detecting objects
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            outs = net.forward(output_layers)

            # Showing informations on the screen
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.3:
                        # Object detected
                        # print("Road markers detected")
                        print(classes[class_id])
                        print("Phat hien nga tu")
                        playmp3("quarter_detected.mp3")
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)

                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            # font = cv2.FONT_HERSHEY_PLAIN
            # for i in range(len(boxes)):
            #     if i in indexes:
            #         x, y, w, h = boxes[i]
            #         label = str(classes[class_ids[i]])
            #         color = colors[class_ids[i]]
            #         cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            #         cv2.putText(frame, label, (x, y + 30), font, 3, color, 2)

            # # All the results have been drawn on the frame, so it's time to display it.
            # cv2.imshow('Object detector', frame)

            key = cv2.waitKey(1)

        # Clean up
        cv2.destroyAllWindows()
        videostream.stop()




class ultra_sonic(Thread):
    def __int__(self):
        super(ultra_sonic, self).__int__()

    def run(self):
        try:
            while True:

                GPIO.output(TRIG, False)
                time.sleep(1)

                GPIO.output(TRIG, True)
                time.sleep(0.00001)
                GPIO.output(TRIG, False)

                while GPIO.input(ECHO) == 0:
                    pulse_start = time.time()

                while GPIO.input(ECHO) == 1:
                    pulse_end = time.time()

                pulse_duration = pulse_end - pulse_start

                distance = pulse_duration * 17150

                distance = round(distance, 2)

                if (distance < 150):
                    print("Distance:", distance, "cm")
                    playmp3("ultra_sonic.mp3")
                    time.sleep(3)


        except KeyboardInterrupt:  # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program and cleanup
            print("Cleaning up!")
            gpio.cleanup()



def playmp3(name):

    pygame.mixer.music.load(name)
    pygame.mixer.music.play()

class send_sms(Thread):
    def __int__(self):
        super(send_sms, self).__int__()

    def run(self):
        while True:
            bien = GPIO.input(25)
            time.sleep(0.1)
            if bien:
                print("Da nhan nut")
                while True:
                    gpsport = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=4)

                    # dataout = pynmea2.NMEAStreamReader()
                    newdata = gpsport.readline()
                    if newdata[0:6] == b"$GPRMC":
                        newmsg = pynmea2.parse(newdata.decode("utf-8"))
                        lat = newmsg.latitude
                        lng = newmsg.longitude
                        sms = "https://maps.google.com/?q=" + str(lat) + "," + str(lng)
                        if lat != 0:
                            port.write(b'AT+CMGF=1\r\n')
                            time.sleep(1)

                            port.write(b'AT+CMGS="+84922024223"\r\n')
                            time.sleep(1)
                            hi = sms + '\r\n'
                            port.write(hi.encode())

                            port.write(b"\x1A")  # Enable to send SMS
                            playmp3("send_sms.mp3")
                            time.sleep(5)
                            break



if __name__ == '__main__':
    t1 = ultra_sonic()
    t2 = send_sms()
    t3 = detect()
    t1.start()
    t2.start()
    t3.start()