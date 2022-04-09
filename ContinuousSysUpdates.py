#Multi threading
from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array

#Time calculations
import time

#Error handling
import traceback

#Import GPIO inputs
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD) #Set GPIO mode the board pin numbers

#This script handles all continuously updating variables that occure in the background of PillDispenser.py (things that have to be done quikly and accurately)

class Switch:
    def __init__(Self, PinNumber, InOut, PullUpDown):
        Self.Pin = PinNumber
        Self.In = InOut
        Self.PUD = PullUpDown

        #Last checked Button value
        Self.Val = False

        #Setup GPIO for button
        GPIO.setup(Self.Pin, Self.In, pull_up_down=Self.PUD)

    def Update(Self):
        Self.Val = Self.GetInput()
        return Self.Val

    def GetInput(Self):
        return GPIO.input(Self.Pin)

print ("Switches Set")
S1 = Switch(37, GPIO.IN, GPIO.PUD_UP)
    
def UpdateRotation():
    global S1, RotationNum, MultipleOfSegments
    while(not(S1.GetInput()) and SysUpdate()):
        continue
    time.sleep(0.05) #short delay to deny bounce
    while (S1.GetInput() and SysUpdate()):
        continue
    RotationNum.value += 1
    if (RotationNum.value >= 21 / MultipleOfSegments.value):
        RotationNum.value = 0;
    time.sleep(0.05) #short delay to deny bounce

def SysUpdate():
    if (Terminate.value):
        print("ContinuousSysUpdates.py: Cleaningup")
        GPIO.cleanup()
        Terminate.value = False
    return not(Terminate.value)
    
def Update():
    try:
        while(True):
            UpdateRotation()
            if (Terminate.value):
                print("ContinuousSysUpdates.py: Cleaningup")
                GPIO.cleanup()
                Terminate.value = False
                break
    except KeyboardInterrupt:
        print("Terminating")
        GPIO.cleanup()
    except:
        print("TRACEBACK - ContinuousSysUpdates")
        traceback.print_exc()
        
RotationNum = Value('i', 0000)
MultipleOfSegments = Value('i', 1)

Terminate = Value('i', False)

def Start():
    SysUpdateRun.start()

def Stop():
    Terminate.value = True
    PrevTime = time.time()
    Time = 0
    while (Terminate.value == True):
        print("ContinuousSysUpdates: Awaiting Termination (" + str(Time) + ")")
        Time += time.time() - PrevTime
        PrevTime = time.time()
        if (Time >= 5):
            print("ContinuousSysUpdates: Termination of GPIO Failed, terminating thread")
            break
        continue
    SysUpdateRun.terminate()

SysUpdateRun = Process(target = Update, args=())
