import paho.mqtt.client as mqtt
import tm1637
from RPi import GPIO
import time
from threading import Thread

clkDisplay = 23
dioDisplay = 24
brightnessDisplay = 1
Display = tm1637.TM1637(clkDisplay,dioDisplay,brightnessDisplay)
Display.Clear()

signalBuzzer  = 18
vccBuzzer = 27
gndBuzzer = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(signalBuzzer, GPIO.OUT)
GPIO.setup(vccBuzzer, GPIO.OUT)
GPIO.setup(gndBuzzer, GPIO.OUT)
GPIO.output(vccBuzzer,True)
GPIO.output(gndBuzzer,False)
buzzerFrequency = 0

sensorDataOutOfRange = 165
ledOFF = 127

def setBuzzerReady():
    GPIO.output(signalBuzzer,True)
    time.sleep(0.25)
    GPIO.output(signalBuzzer,False)

def sensorDateIsOutOfRangeOrOFF(msg):
    global buzzerFrequency
    if msg < 0:
        Display.Clear()
        buzzerFrequency = -1
    elif msg > sensorDataOutOfRange:
        digits = [127,0,127,127]
        Display.Show(digits)
        Display.ShowDoublepoint(1,1)
        buzzerFrequency = 0.6

def sensorDateChooseRange(msg):
    global buzzerFrequency
    if msg >= 2 and msg <= 10:
        digits = [127,0,0,127]
        buzzerFrequency = 0
    elif msg > 10 and msg <= 20:
        digits = [127,0,1,127]
        buzzerFrequency = 0.025
    elif msg > 20 and msg <= 30:
        digits = [127,0,2,127]
        buzzerFrequency = 0.05
    elif msg > 30 and msg <= 40:
        digits = [127,0,3,127]
        buzzerFrequency = 0.1
    elif msg > 40 and msg <= 50:
        digits = [127,0,4,127]
        buzzerFrequency = 0.1
    elif msg > 50 and msg <= 60:
        digits = [127,0,5,127]
        buzzerFrequency = 0.15
    elif msg > 60 and msg <= 70:
        digits = [127,0,6,127]
        buzzerFrequency = 0.15
    elif msg > 70 and msg <= 80:
        digits = [127,0,7,127]
        buzzerFrequency = 0.2
    elif msg > 80 and msg <= 90:
        digits = [127,0,8,127]
        buzzerFrequency = 0.2
    elif msg > 90 and msg <= 100:
        digits = [127,0,9,127]
        buzzerFrequency = 0.25
    elif msg > 100 and msg <= 110:
        digits = [127,1,0,127]
        buzzerFrequency = 0.3
    elif msg > 110 and msg <= 120:
        digits = [127,1,2,127]
        buzzerFrequency = 0.3
    elif msg > 120 and msg <= 130:
        digits = [127,1,3,127]
        buzzerFrequency = 0.35
    elif msg > 130 and msg <= 140:
        digits = [127,1,4,127]
        buzzerFrequency = 0.35
    elif msg > 140 and msg <= 150:
        digits = [127,1,5,127]
        buzzerFrequency = 0.4
    elif msg > 150 and msg <= 160:
        digits = [127,1,6,127]
        buzzerFrequency = 0.4
    return digits

def buzzer():
    buzzerCondition = True;
    while True:
        if buzzerFrequency > 0:
            GPIO.output(vccBuzzer,buzzerCondition)
            time.sleep(buzzerFrequency)
            buzzerCondition = not buzzerCondition
        elif buzzerFrequency < 0:
            GPIO.output(vccBuzzer,False)
        else:
            GPIO.output(vccBuzzer,True)

def on_message(client, obj, msg):
    msa = str(msg.payload)
    msa1 = msa.replace("b","")
    msa2 = msa1.replace("'","")
    msa3 = float(msa2)
    msa4 = int(msa3)

    if msa4 < 0 or msa4 > sensorDataOutOfRange:
        sensorDateIsOutOfRangeOrOFF(msa4)
    else:
        Display.Show(sensorDateChooseRange(msa4))
        Display.ShowDoublepoint(1,1)




mqttc = mqtt.Client()
mqttc.on_message = on_message

mqttc.username_pw_set("RasberyPI", "pi")
mqttc.connect("m21.cloudmqtt.com", 12528)

mqttc.subscribe("Distance", 0)

buzzerThread = Thread(target = buzzer, args=())
buzzerThread.start()

# Continue the network loop, exit when an error occurs
rc = 0
while rc == 0:
    rc = mqttc.loop()