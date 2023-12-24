#Programming assignment 5
#Author: Akshatha, Swathi, Hasini
'''
    LightSwarm Raspberry Pi Logger 
    SwitchDoc Labs 
    December 2020
'''
#Submission date: 12/08/2023
from __future__ import print_function
import RPi.GPIO as GPIO 
from builtins import chr
from builtins import str
from builtins import range
import sys  
import time 
import random
import threading
import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from netifaces import interfaces, ifaddresses, AF_INET

from socket import *


# Define the GPIO pins
button = 6
yellowLed = 26
redLed = 20
greenLed = 13
blueLed = 19
ledPins = [20,13,19]
led_status = {}
# packet type definitions
LIGHT_UPDATE_PACKET = 0
RESET_SWARM_PACKET = 1
DEFINE_SERVER_LOGGER_PACKET = 2
LOG_TO_SERVER_PACKET = 3
MYPORT = 2910
LOG_FILE_PATH = "/home/pi/Desktop/Assignment/Assignment9/logs/"
log_file = None
log_start_time = time.time()
SWARMSIZE = 6
#previousSwarmID = 0
s=socket(AF_INET, SOCK_DGRAM)
host = 'localhost';
s.bind(('',MYPORT))
LSBFIRST = 1
MSBFIRST = 2
#define the pins connect to 74HC595
#LED MATRIC
DATAPIN = 17 #DS Pin of 74HC595(Pin14)
LATCHPIN = 27 #ST_CP Pin of 74HC595(Pin12)
CLOCKPIN = 22 #SH_CP Pin of 74HC595(Pin11)
pic = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
my_array = [0, 0, 0, 0, 0, 0, 0, 0]

#  #for 4*7 segment display
# LSBFIRST = 1
# MSBFIRST = 2
#define the pins connect to 74HC595
dataPin = 24#DS Pin of 74HC595(Pin14)
latchPin = 23 #ST_CP Pin of 74HC595(Pin12)
clockPin = 18 #SH_CP Pin of 74HC595(Pin11)
num = (0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90)
digitPin = (2,3,25,10) # Define the pin of 7-segment display common end
counter = 0 # Variable counter, the number will be dislayed by 7-segment display
t = 0 # define the Timer object


photo_data = []
master_devices = {}
# Initialize the plot
fig, (ax1,ax2) = plt.subplots(2, 1)

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(yellowLed, GPIO.OUT)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    #GPIO.setmode(GPIO.BOARD) # Number GPIOs by its physical location
    GPIO.setup(dataPin, GPIO.OUT) # Set pin mode to output
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)
    GPIO.setup(DATAPIN, GPIO.OUT)
    GPIO.setup(LATCHPIN, GPIO.OUT)
    GPIO.setup(CLOCKPIN, GPIO.OUT)
    for pin in digitPin:
        GPIO.setup(pin,GPIO.OUT)

    logString = ""

def shiftOut(dPin,cPin,order,val):
    for i in range(0,8):
        GPIO.output(cPin,GPIO.LOW);
        if(order == LSBFIRST):
            GPIO.output(dPin,(0x01&(val>>i)==0x01) and GPIO.HIGH or GPIO.LOW)
        elif(order == MSBFIRST):
            GPIO.output(dPin,(0x80&(val<<i)==0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin,GPIO.HIGH)
 
def outData(data): #function used to output data for 74HC595
    GPIO.output(latchPin,GPIO.LOW)
    shiftOut(dataPin,clockPin,MSBFIRST,data)
    GPIO.output(latchPin,GPIO.HIGH)
 
def selectDigit(digit): # Open one of the 7-segment display and close the remaining three, theparameter digit is optional for 1,2,4,8
    GPIO.output(digitPin[0],GPIO.LOW if ((digit&0x08) == 0x08) else GPIO.HIGH)
    GPIO.output(digitPin[1],GPIO.LOW if ((digit&0x04) == 0x04) else GPIO.HIGH)
    GPIO.output(digitPin[2],GPIO.LOW if ((digit&0x02) == 0x02) else GPIO.HIGH)
    GPIO.output(digitPin[3],GPIO.LOW if ((digit&0x01) == 0x01) else GPIO.HIGH)

def display(dec): #display function for 7-segment display
    outData(0xff) #eliminate residual display
    selectDigit(0x01) #Select the first, and display the single digit
    outData(num[dec%10])
    time.sleep(0.003) #display duration
    outData(0xff)
    selectDigit(0x02) # Select the second, and display the tens digit
    outData(num[dec%100//10])
    time.sleep(0.003)
    outData(0xff)
    selectDigit(0x04) # Select the third, and display the hundreds digit
    outData(num[dec%1000//100])
    time.sleep(0.003)
    outData(0xff)
    selectDigit(0x08) # Select the fourth, and display the thousands digit
    outData(num[dec%10000//1000])
    time.sleep(0.003)

#def timer(): #timer function
#    global counter
##    global t
 #   t = threading.Timer(1.0,timer) #reset time of timer to 1s
 #   t.daemon=True
 #   t.start() #Start timing
    #counter+=1 
    #print ("counter : %d"%counter)

def open_log_file():
    global log_file
    log_file = f"{LOG_FILE_PATH}{time.strftime('%Y-%m-%d_%H-%M-%S')}_log.csv"
    #with open(f"{LOG_FILE_PATH}{time.strftime('%Y-%m-%d_%H-%M-%S')}_log.txt", "w") as log_file:
    #print(log_file)
    log_file = open(log_file, "a")

def close_log_file():
    global log_file
    if log_file:
        print("Closing the log file")
        log_file.close()

def log_message(message):
    global log_file
    if log_file:
        log_file.write(message + "\n")



def handler_stop_signals(signum, frame):
    GPIO.output(whiteLed, False)
    GPIO.output(redLed, False)
    GPIO.output(greenLed, False)
    GPIO.output(blueLed, False)
    close_log_file()
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

def shiftOut(dPin,cPin,order,val):
    for i in range(0,8):
        GPIO.output(cPin,GPIO.LOW);
        if(order == LSBFIRST):
            GPIO.output(dPin,(0x01&(val>>i)==0x01) and GPIO.HIGH or GPIO.LOW)
        elif(order == MSBFIRST):
            GPIO.output(dPin,(0x80&(val<<i)==0x80) and GPIO.HIGH or GPIO.LOW)
            GPIO.output(cPin,GPIO.HIGH);

def ledMatrix():
    pic1 = pic2 = pic3 = pic4 = pic5 = pic6 = pic7 = pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    #pic2 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    for j in range(0,500):# Repeat enough times to display the smiling face a period of time
        x=0x80
        sensorValue = getPhotoData()
        print("sensorValue",sensorValue)
        for i in sensorValue:
            #print("SensorValue array elements",i)
            if i == sensorValue[0]:
                i = sensorValue[0]
                #print("1st array element",i)
                i = int(i)
                if(i < 128):
                    pic1 = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic1 = [0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic1 = [0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic1 = [0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 512 and i < 640):
                    #print("Entering 1st time")
                    pic1 = [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                    #time.sleep(1)
                elif(i > 640 and i < 768):
                    pic1 = [0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic1 = [0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic1 = [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
#                     for j in range(0,8):
#                         GPIO.output(latchPin,GPIO.LOW)
#                         shiftOut(dataPin,clockPin,MSBFIRST,pic1[j]) #first shift data of line information to first stage 74HC959
#                         shiftOut(dataPin,clockPin,MSBFIRST,~x) #then shift data of column information to second stage 74HC959
#                         GPIO.output(latchPin,GPIO.HIGH)# Output data of two stage 74HC595 at the same time
#                         time.sleep(0.001)# display the next column
#                         x>>=1
            elif  i == sensorValue[1]:
                i = sensorValue[1]
                i = int(i)
                #print("2nd array element",i)
                if(i < 128):
                 #   print("Entering 2nd time this loop")
                 #   print(pic)
                    pic2 = [0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic2 = [0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic2 = [0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic2 = [0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic2 = [0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 640 and i < 768):
                    pic2 = [0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic2 = [0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic2 = [0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
#                     for j in range(0,8):
#                         GPIO.output(latchPin,GPIO.LOW)
#                         shiftOut(dataPin,clockPin,MSBFIRST,pic[j]) #first shift data of line information to first stage 74HC959
#                         shiftOut(dataPin,clockPin,MSBFIRST,~x) #then shift data of column information to second stage 74HC959
#                         GPIO.output(latchPin,GPIO.HIGH)# Output data of two stage 74HC595 at the same time
#                         time.sleep(0.001)# display the next column
#                         x>>=1
            elif  i == sensorValue[2]:
                i = sensorValue[2]
                i = int(i)
         #       print("3rd array element",i)
                if(i < 128):
                    #print("Entering 2nd time this loop")
                    #print(pic)
                    pic3 = [0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]
                    #time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic3 = [0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic3 = [0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic3 = [0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic3 = [0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 640 and i < 768):
                    pic3 = [0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic3 = [0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic3 = [0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00]
            elif  i == sensorValue[3]:
                i = sensorValue[3]
                i = int(i)
          #      print("4th array element",i)
                if(i < 128):
                #    print("Entering 2nd time this loop")
                 #   print(pic)
                    pic4 = [0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic4 = [0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic4 = [0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic4 = [0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic4 = [0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]
                elif(i > 640 and i < 768):
                    pic4 = [0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic4 = [0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic4 = [0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00]
            elif  i == sensorValue[4]:
                i = sensorValue[4]
                i = int(i)
           #     print("5th array element",i)
                if(i < 128):
                #    print("Entering 2nd time this loop")
                 #   print(pic)
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00]
                elif(i > 512 and i < 640):
            #        print("Am I entering here?")
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00]
                elif(i > 640 and i < 768):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic5 = [0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00]

            elif  i == sensorValue[5]:
                i = sensorValue[5]
               # print("2nd array element",i)
                i = int(i)
                if(i < 128):
                #    print("Entering 2nd time this loop")
                 #   print(pic)
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00]
                elif(i > 256 and i < 384):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00]
                elif(i > 384 and i < 512):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00]
                elif(i > 640 and i < 768):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00]
                elif(i > 768 and i < 896):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00]
                elif(i > 896 and i < 1024):
                    pic6 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00]

            elif  i == sensorValue[6]:
                i = sensorValue[6]
               # print("2nd array element",i)
                i = int(i)
                if(i < 128):
                #    print("Entering 2nd time this loop")
                 #   print(pic)
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00]
                elif(i > 256 and i < 384):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00]
                elif(i > 384 and i < 512):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00]
                elif(i > 640 and i < 768):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00]
                elif(i > 768 and i < 896):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00]
                elif(i > 896 and i < 1024):
                    pic7 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00]

            elif  i == sensorValue[7]:
                i = sensorValue[7]
               # print("2nd array element",i)
                i = int(i)
                if(i < 128):
                #    print("Entering 2nd time this loop")
                 #   print(pic)
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
                  #  time.sleep(1)
                    #print("Inside loop")
                elif(i > 128 and i < 256):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02]
                elif(i > 256 and i < 384):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04]
                elif(i > 384 and i < 512):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08]
                elif(i > 512 and i < 640):
                    #print("Am I entering here?")
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10]
                elif(i > 640 and i < 768):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20]
                elif(i > 768 and i < 896):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40]
                elif(i > 896 and i < 1024):
                    pic8 = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80]

            pic = [a | b | c | d | e | f | g | h for a,b,c,d,e,f,g,h in zip(pic1,pic2,pic3,pic4,pic5,pic6,pic7,pic8)]
            print(pic)
            for j in range(0,8):
                GPIO.output(LATCHPIN,GPIO.LOW)
                shiftOut(DATAPIN,CLOCKPIN,MSBFIRST,pic[j]) #first shift data of line information to first stage 74HC959
                shiftOut(DATAPIN,CLOCKPIN,MSBFIRST,~x) #then shift data of column information to second stage 74HC959
                GPIO.output(LATCHPIN,GPIO.HIGH)# Output data of two stage 74HC595 at the same time
                time.sleep(0.1)# display the next column
                x>>=1
# 
# def update_photo_trace(i):
#     global photo_data
#     global incomingSwarmID
#     photo_data.append(get_photo_reading())
#     photo_data = photo_data[-30:]  # Keep only the last 30 data points
#     ax1.clear()
# 
#     # Check the incomingSwarmID and set the color accordingly
#     if incomingSwarmID == 37:
#         line_color = 'red'
#     elif incomingSwarmID == 110:
#         line_color = 'green'
#     else:
#         line_color = 'blue'
# 
#     ax1.plot(photo_data, label='Photocell Data Trace', color=line_color)
#     ax1.set_title('Photocell Data Trace')
#     ax1.set_xlabel('Time (s)')
#     ax1.set_ylabel('Photocell Reading')
#     ax1.legend()
#     plt.pause(0.1)
# 
def getPhotoData():
    #my_array = random.randint(30)#546,101,800,230,536,201,700,630]
    for i in range(len(my_array)):
        sensorData = random.randint(1,1024)
        my_array[i] = sensorData
    return my_array
# 
# 
# # Function to get photocell reading
# def get_photo_reading():
#     global sensorValue
#      # Replace this with your actual code to read the photocell data
#     return sensorValue  # Example value
# 
# # Function to update bar chart showing master devices
# def update_master_chart(i):
#     update_master_devices()
#     ax2.clear()
#     # Assign unique colors to each device
#     colors = ['red', 'green', 'blue']  # Add more colors if needed
#     #device_colors = {device: colors[i] for i, device in enumerate(master_devices.keys())}
#     device_colors = {
#     '192.168.126.37': 'red',
#     '192.168.126.110': 'green',
#     '192.168.126.134': 'blue',
#     # Add more devices as needed
#     }
#     ax2.bar(range(len(master_devices)), master_devices.values(), color=[device_colors[device] for device in master_devices.keys()])
#     ax2.set_xticks(range(len(master_devices)))
#     ax2.set_xticklabels(list(master_devices.keys()))
#     ax2.set_title('Master Devices')
#     ax2.set_xlabel('IP Address')
#     ax2.set_ylabel('Time as Master (s)')
#   
# def update_master_devices():
#     global master_devices
#     current_master = get_master_device()
#     print(f"Current Master Device: {current_master}")  # Debug print
#     if current_master not in master_devices:
#         print(f"Adding {current_master} to master_devices")  # Debug print
#         master_devices[current_master] = 1
#     else:
#         print(f"Incrementing count for {current_master}")  # Debug print
#         master_devices[current_master] += 1
# 
# def get_master_device():
#     # Replace this with your actual code to determine the master device
#     global incomingSwarmID
#     return '192.168.126.' + str(incomingSwarmID)  # Example IP address



def SendDEFINE_SERVER_LOGGER_PACKET(s):
    print("DEFINE_SERVER_LOGGER_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# get IP address
    for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            print('%s: %s' % (ifaceName, ', '.join(addresses)))
  
    # last interface (wlan0) grabbed 
    print(addresses) 
    myIP = addresses[0].split('.')
    print(myIP) 
    data= ["" for i in range(7)]

    
    data[0] = int("F0", 16).to_bytes(1,'little') 
    data[1] = int(DEFINE_SERVER_LOGGER_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swarm)
    data[3] = int(myIP[0]).to_bytes(1,'little') # 1 octet of ip
    data[4] = int(myIP[1]).to_bytes(1,'little') # 2 octet of ip
    data[5] = int(myIP[2]).to_bytes(1,'little') # 3 octet of ip
    data[6] = int(myIP[3]).to_bytes(1,'little') # 4 octet of ip
    mymessage = ''.encode()
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))
 
#def log_master_data(device_ip, duration, raw_data, log_file):
#    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
#    log_entry = f"{timestamp} - IP: {device_ip}, Duration: {duration}s, Raw Data: {raw_data}\n"
#    log_file.write(log_entry)

# def save_log_file(new_button_state):
#     global master_devices_data
#     current_time = time.time()
#     last_button_press_time = current_time
#     while True:
#         button_state = new_button_state
#         if button_state == 0:
#             current_time = time.time()
#             if current_time - last_button_press_time > 1:  # Avoid accidental multiple presses
#                 last_button_press_time = current_time
#                 with open(f"{LOG_FILE_PATH}{time.strftime('%Y-%m-%d_%H-%M-%S')}_log.txt", "w") as log_file:
#                     for data in master_devices_data:
#                          log_master_data(data['device_ip'], data['duration'], data['raw_data'], log_file)
#                     print("##############################Log file saved.#################################")
#                 #master_devices_data = []  # Clear the data after saving the log
#         time.sleep(0.1)  # Adjust the sleep duration based on your requirements


def SendRESET_SWARM_PACKET(s):
    print("RESET_SWARM_PACKET Sent") 
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    data= ["" for i in range(7)]

    data[0] = int("F0", 16).to_bytes(1,'little')
    
    data[1] = int(RESET_SWARM_PACKET).to_bytes(1,'little')
    data[2] = int("FF", 16).to_bytes(1,'little') # swarm id (FF means not part of swar
    data[3] = int(0x00).to_bytes(1,'little')
    data[4] = int(0x00).to_bytes(1,'little')
    data[5] = int(0x00).to_bytes(1,'little')
    data[6] = int(0x00).to_bytes(1,'little')
    mymessage = ''.encode()
    s.sendto(mymessage.join(data), ('<broadcast>'.encode(), MYPORT))

def parseLogPacket(message):
       
	incomingSwarmID = setAndReturnSwarmID((message[2]))
	print("Log From SwarmID:",(message[2]))
	print("Swarm Software Version:", (message[4]))
	print("StringLength:",(message[3]))
	logString = ""
	for i in range(0,(message[3])):
		logString = logString + chr((message[i+5]))

	return logString	

def setAndReturnSwarmID(incomingID):
    global swarmStatus
  
    for i in range(0,SWARMSIZE):
        if (swarmStatus[i][5] == incomingID):
            return i
        else:
            if (swarmStatus[i][5] == 0):  # not in the system, so put it in
    
                swarmStatus[i][5] = incomingID;
                print("incomingID %d " % incomingID)
                print("assigned #%d" % i)
                return i
    
  
    # if we get here, then we have a new swarm member.   
    # Delete the oldest swarm member and add the new one in 
    # (this will probably be the one that dropped out)
  
    oldTime = time.time();
    oldSwarmID = 0
    for i in range(0,SWARMSIZE):
        if (oldTime > swarmStatus[i][1]):
            ldTime = swarmStatus[i][1]
            oldSwarmID = i
  		
    # remove the old one and put this one in....
    swarmStatus[oldSwarmID][5] = incomingID;
    # the rest will be filled in by Light Packet Receive
    print("oldSwarmID %i" % oldSwarmID)
 
    return oldSwarmID 
 
def button_thread():
    try:
        while True:
            new_button_state = GPIO.input(button)
            if new_button_state == 0:
                print("Button Pressed")
                SendRESET_SWARM_PACKET(s)
                resetFlag=True
                #sock.sendto(str.encode(msg), (esp8266_ip, MYPORT))
                #save_log_file(new_button_state)
                blink_yellow_led(3)
                open_log_file()
#                 plt.ion()
#                 ani1 = animation.FuncAnimation(fig, update_photo_trace, interval=1000)
#                 ani2 = animation.FuncAnimation(fig, update_master_chart, interval=1000) 
            time.sleep(0.01)
    except KeyboardInterrupt:
         quit()


# Function to blink the yellow LED for a specified duration
def blink_yellow_led(duration):
    GPIO.output(yellowLed, True)
    time.sleep(duration)
    GPIO.output(yellowLed, False)
    resetFlag = False

def main():
    try:
        global log_start_time
        global swarmStatus
        global master_devices_data
        global incomingSwarmID
        global sensorValue
        global t
        global counter
        resetFlag = False
        previousSwarmID = 0
        prev_device_ip = 0
        previousduration = 0
        prev_raw_data = 0
        count1 = count2 = count3 = count4 = count5 = count6 = 0
#         count2=0
#         count3=0
        sensorValue = 0
        durationMaster = 0
        init()
        t_button = threading.Thread(target=button_thread)
        t_button.daemon = True
        t_button.start()
        
        t_LedMatrix = threading.Thread(target=ledMatrix)
        t_LedMatrix.daemon = True
        t_LedMatrix.start()        
        #t = threading.Timer(1.0,timer) #set the timer
        #t.daemon = True
        #t.start() # Start timing

        open_log_file()
        
        swarmStatus = [[0 for x  in range(6)] for x in range(SWARMSIZE)]
    #     # first send out DEFINE_SERVER_LOGGER_PACKET to tell swarm where to send logging information 
    # 
        SendDEFINE_SERVER_LOGGER_PACKET(s)
        time.sleep(3)
        SendDEFINE_SERVER_LOGGER_PACKET(s)
        for i in range(0,SWARMSIZE):
            swarmStatus[i][0] = "NP"
            swarmStatus[i][5] = 0
        while True:
            #display(counter)
            # receive datclient (data, addr)
            d = s.recvfrom(1024)

            message = d[0]
            addr = d[1]

            if (len(message) == 7):
                if (message[1] == LIGHT_UPDATE_PACKET):
                    incomingSwarmID = setAndReturnSwarmID((message[2]))
                    swarmStatus[incomingSwarmID][0] = "P"
                    swarmStatus[incomingSwarmID][1] = time.time()
                if ((message[1]) == RESET_SWARM_PACKET):
                    print("Swarm RESET_SWARM_PACKET Received")
                    print("received from addr:", addr)
                    #log_message(f"RESET_SWARM_PACKET received from {addr}")

                if ((message[1]) == DEFINE_SERVER_LOGGER_PACKET):
                    print("Swarm DEFINE_SERVER_LOGGER_PACKET Received")
                    print("received from addr:", addr)
                    #log_message(f"DEFINE_SERVER_LOGGER_PACKET received from {addr}")

            else:
                if ((message[1]) == LOG_TO_SERVER_PACKET):
                    print("Swarm LOG_TO_SERVER_PACKET Received")
                    #log_message("LOG_TO_SERVER_PACKET received")

                    # process the Log Packet
                    logString = parseLogPacket(message)
                    swarmList = logString.split("|")
                    raw_data = swarmList
                    temp = swarmList[0].split(",")
                    sensorValue = temp[2]
                    for i in range(0, SWARMSIZE):
                        swarmElement = swarmList[i].split(",")
                        print("Swarm Element", swarmElement)
                        incomingSwarmID = message[2]
                        print(incomingSwarmID)
                        display(incomingSwarmID)
                        #ledMatrix()
                        if resetFlag != True:
                            previousduration = durationMaster
                            if incomingSwarmID != previousSwarmID and previousSwarmID != 0:
                             #   print("Inside if loop - Duration Master, count1, count2, count3", previousduration, count1, count2, count3)
                                log_message(f" Master Swarm: {previousSwarmID}, IP: {prev_device_ip}, Duration: {previousduration}s, SensorVal: {prevSensorVal}, Raw Data: {prev_raw_data}")
                                #previousSwarmID = incomingSwarmID
                            if (incomingSwarmID == 2):
                                print('Swarm1')
                                GPIO.output(20, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(20, False)
                                count1 += 1
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                count5 = 0
                                count6 = 0
                            elif (incomingSwarmID == 4):
                                print('Swarm2')
                                GPIO.output(13, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(13, False)
                                count2 += 1
                                count1 = 0
                                count3 = 0
                                count4 = 0
                                count5 = 0
                                count6 = 0
                            elif (incomingSwarmID == 195):
                                print('Swarm3')
                                GPIO.output(19, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(19, False)
                                count3 += 1
                                count2 = 0
                                count1 = 0
                                count4 = 0
                                count5 = 0
                                count6 = 0
                            elif (incomingSwarmID == 24):
                                print('Swarm4')
                                GPIO.output(20, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(20, False)
                                count4 += 1
                                count2 = 0
                                count3 = 0
                                count1 = 0
                                count5 = 0
                                count6 = 0
                            elif (incomingSwarmID == 145):
                                print('Swarm5')
                                GPIO.output(13, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(13, False)
                                count5 += 1
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                count1 = 0
                                count6 = 0
                            else:
                                print('Swarm6')
                                GPIO.output(19, True)
                                time.sleep(0.1)  # Adjust the delay as needed
                                GPIO.output(19, False)
                                count6 += 1
                                count2 = 0
                                count3 = 0
                                count4 = 0
                                count5 = 0
                                count1 = 0
                            device_ip = "192.168.0."+str(message[2])
                            durationMaster = count1 or count2 or count3
                            previousSwarmID = incomingSwarmID
                            prev_raw_data = raw_data
#                           print("raw_data",raw_data[0][2])
                            prev_device_ip = device_ip
                            prevSensorVal = sensorValue

                else:
                    print("error message length = ", len(message))
                #plt.pause(0.1)
    except (KeyboardInterrupt, SystemExit):
        GPIO.output(26, False)
        GPIO.output(20, False)
        GPIO.output(13, False)
        GPIO.output(19, False)
        close_log_file()
    finally:
        GPIO.output(26, False)
        GPIO.output(20, False)
        GPIO.output(13, False)
        GPIO.output(19, False)
        close_log_file()
        
if __name__ == '__main__':
    main()





