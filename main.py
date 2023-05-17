

import serial.tools.list_ports
import random
import time
import  sys
from string import Template
from Adafruit_IO import MQTTClient


AIO_FEED_IDS = ["bbc-led","bbc-humi","bbc-hir"]
AIO_USERNAME = "dlhcmut"
AIO_KEY = "aio_DSdv08B4n07hxZDuifw02Rsil40e"

def  connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)

def  subscribe(client , userdata , mid , granted_qos):
    print("Subcribe thanh cong...")

def  disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)

def  message(client , feed_id , payload):
    if feed_id == "bbc-led":
        if payload == "a":
            uart_write("a")
        else:
            uart_write("b")
    elif feed_id == "bbc-fan":
        if payload == "c":
            uart_write("c")
        else:
            uart_write("d")
    elif feed_id == "fire-alarm":
        uart_write(payload)
    if isMicrobitConnected:
        ser.write((str(payload) + "#").encode())

def uart_write(data):
    ser.write(str(data).encode())
    return

client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        # print(strPort)
        if "USB-SERIAL" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    print(commPort)
    return commPort

isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial( port=getPort(), baudrate=115200)
    isMicrobitConnected = True


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    print(data)
    splitData = data.split(":")
    # print(splitData)
    # x = Template('{"temp": $temp, "humidity": $humidity}')
    # bbc-json 
    try:
        if splitData[0] == "HIR":
            client.publish("bbc-hir", splitData[1])
        if splitData[0] == "TEMP":
            client.publish("bbc-temp", splitData[1])    
            # "{"temp": splitData[1]"
        if splitData[2] == "HUMI":
            client.publish("bbc-humi", splitData[3])
            x = Template('{"temp": $temp, "humidity": $humidity}')
            st =  x.substitute(temp = splitData[1], humidity = splitData[3])
            client.publish("value", st)
    except:     
        pass

mess = ""
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

while True:
    if isMicrobitConnected:
        readSerial()

    time.sleep(1)