#Libraries

import gpiozero 
import RPi.GPIO as GPIO
import time
import random
import subprocess

voices = ['voice_1.wav', 'voice_3.wav', 'voice_2.flac']
SEEN_DIST = 40
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_BUZZER = 25
GPIO_BUTTON = 8
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)
GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def buzzer_on():
    print ("buzzer on")
    GPIO.output(GPIO_BUZZER, True)

def buzzer_off():
    print ("buzzer off")
    GPIO.output(GPIO_BUZZER, False)

def headset_is_down():
    status = GPIO.input(GPIO_BUTTON)==GPIO.HIGH
    print ("headset is down:", status)
    return status

def play_voice():
    voice = random.choice(voices)
    print ("playing voice", voice)
    player = subprocess.Popen(["mplayer", voice])
    time.sleep(3)

def stop_playing_voice():
    stopper = subprocess.Popen(["pkill", "mplayer"])
    time.sleep(5)

try:
    while True:
        dist = distance()
        print ("Measured Distance = %.1f cm" % dist)
        if headset_is_down():
            print ("headset down")
            if dist < SEEN_DIST:
                print ("setting buzzer on")
                buzzer_on()
            else:
                print ("setting buzzer off")
                buzzer_off()
        else: # someone answered the phone
            print ("headset is on use")
            buzzer_off()
            print ("playing voice")
            play_voice() #play voice while phone is back down
            while not headset_is_down():
                pass
            stop_playing_voice() 

        time.sleep(1)
 
    # Reset by pressing CTRL + C
except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
