#Multi threading
from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array

#Time calculations
import time

#LCD display library
import lcddriver

#Import GPIO inputs
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD) #Set GPIO mode the board pin numbers

#Error handling
import traceback

#Continuous updates
import ContinuousSysUpdates

#TODO:: Fix while loops freezing

#Continuous requests
#Gets the multiple of segments
def GetMultipleOfSegments():
    return ContinuousSysUpdates.MultipleOfSegments.value

def GetRotationNum():
    return ContinuousSysUpdates.RotationNum.value

def SetMultipleOfSegments(Multiple):
    ContinuousSysUpdates.MultipleOfSegments.value = Multiple
    return ContinuousSysUpdates.MultipleOfSegments.value

#RequestHandler - Quick request, also handles and stores all shared variables
import RequestHandler

#Button objects
class Button:
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

    def OnKeyUp(Self): #Requires Self.Update() to be called constantly at the end of each frame
        if (Self.Val == False and Self.Update()):
            return True
        return False

    def GetInput(Self):
        return not(GPIO.input(Self.Pin)) #Returns inverse of input as it is a pull up switch -> http://razzpisampler.oreilly.com/ch07.html

#Ultrasonic sensor object
class Ultrasonic:
    def __init__(Self, TrigPin, EchoPin):
        Self.TrigPin = TrigPin
        Self.EchoPin = EchoPin

        #Setup GPIO for ultrasonic sensor
        GPIO.setup(Self.TrigPin, GPIO.OUT) #Trig output pin
        GPIO.output(Self.TrigPin, 0) #Set output trig pin to low
        
        GPIO.setup(Self.EchoPin, GPIO.IN) #Echo input pin
        time.sleep(0.1) #give time to allow sensor to settle

    def GetMeasurement(Self):
        GPIO.output(Self.TrigPin, 1) #Set trig output pin to high
        time.sleep(0.00001) #wait to allow sensor to settle
        GPIO.output(Self.TrigPin, 0) #Set trig output pin back to low

        #Start timing the pulse given by echo pin
        StartTime = time.time()
        while (GPIO.input(Self.EchoPin) == 0): #Wait until echo pin has started (start of pulse)
            if (time.time() - StartTime > 0.5):
                print("Error")
                return 1000
                break
        start = time.time() #Start time
        while (GPIO.input(Self.EchoPin) == 1): #Wait until echo pin has ended (end of pulse)
            pass
        stop = time.time() #End time

        time.sleep(0.05) #Safety catch to give sensor time to rest after measurement

        #Distance = Speed / Time -> https://www.youtube.com/watch?v=xACy8l3LsXI
        return (stop - start) * 17000 #return distance in cm

#Motor controller object
class MotorController:
    def __init__(Self, STBY, PWMA, AIN1, AIN2, PWMB, BIN1, BIN2):
        Self.STBY = STBY
        Self.StandbyState = True

        #Motor A
        Self.PWMA = PWMA
        Self.AIN1 = AIN1
        Self.AIN2 = AIN2
        
        #Motor B
        Self.PWMB = PWMB
        Self.BIN1 = BIN1
        Self.BIN2 = BIN2

        GPIO.setup(Self.STBY, GPIO.OUT)

        #Setup motors (-1 means not in use)
        if (Self.PWMA != -1 and Self.AIN1 != -1 and Self.AIN2 != -1):
            GPIO.setup(Self.PWMA, GPIO.OUT)
            GPIO.setup(Self.AIN1, GPIO.OUT)
            GPIO.setup(Self.AIN2, GPIO.OUT)
        if (Self.PWMB != -1 and Self.BIN1 != -1 and Self.BIN2 != -1):
            GPIO.setup(Self.PWMB, GPIO.OUT)
            GPIO.setup(Self.BIN1, GPIO.OUT)
            GPIO.setup(Self.BIN2, GPIO.OUT)

    def Standby(Self, State):
        Self.StandbyState = State
        if (State):
            GPIO.output(Self.STBY, GPIO.LOW)
        else:
            GPIO.output(Self.STBY, GPIO.HIGH)

    def Reset(Self):
        GPIO.output(Self.STBY, GPIO.LOW)
        Self.StandbyState = True
        if (Self.PWMA != -1 and Self.AIN1 != -1 and Self.AIN2 != -1):
            GPIO.output(Self.AIN1, GPIO.LOW)
            GPIO.output(Self.AIN2, GPIO.LOW)
            GPIO.output(Self.PWMA, GPIO.LOW)
        if (Self.PWMB != -1 and Self.BIN1 != -1 and Self.BIN2 != -1):
            GPIO.output(Self.PWMB, GPIO.LOW)
            GPIO.output(Self.BIN1, GPIO.LOW)
            GPIO.output(Self.BIN2, GPIO.LOW)
        
    def MotorA(Self, In1, In2, PWM):
        if (Self.PWMA == -1 or Self.AIN1 == -1 or Self.AIN2 == -1):
            return
        GPIO.output(Self.AIN1, In1)
        GPIO.output(Self.AIN2, In2)
        GPIO.output(Self.PWMA, PWM)

    def MotorB(Self, In1, In2, PWM):
        if (Self.StandbyState or Self.PWMB == -1 or Self.BIN1 == -1 or Self.BIN2 == -1):
            return
        GPIO.output(Self.BIN1, In1)
        GPIO.output(Self.BIN2, In2)
        GPIO.output(Self.PWMB, PWM)

#MOSFET motor controller
class MOSFETController:
    def __init__(Self, Pin):
        Self.Pin = Pin
        GPIO.setup(Self.Pin, GPIO.OUT)

        Self.PrevTime = time.time()
        Self.DeltaTime = 0

    def State(Self, State):
        GPIO.output(Self.Pin, State)

    def Waddle(Self): #Slowly increment motor
        Self.State(GPIO.HIGH)
        Time = 0
        Self.Update()
        time.sleep(0.01)
        Self.State(GPIO.LOW)
        time.sleep(0.1)

    def Update(Self):
        Self.DeltaTime = (time.time() - Self.PrevTime)
        Self.PrevTime = time.time()
        return Self.DeltaTime #in seconds
        
#<<<<<<<<< GLOBAL VARIABLES >>>>>>>>>#
        
#Set Display
print("Display Set")
Display = lcddriver.lcd()
LCDRefreshRate = 1/20 #20 frames per second
LCDLastPrintCall = time.time() #Last refresh call
def RefreshRateCheck():
    global LCDLastPrintCall
    global LCDRefreshRate
    CurrentTime = time.time()
    if (CurrentTime - LCDLastPrintCall < LCDRefreshRate): #Display refresh rate hasnt been met
        return False
    LCDLastPrintCall = CurrentTime
    return True

def LCDPrint(string, line): #To make my life easier -> also includes refresh rates checks etc
    if (RefreshRateCheck()):
        while (len(string) < 16): #rewrite over written parts of lcd
            string += " "
        Display.lcd_display_string(string, line)
    
def LCDClear():
    Display.lcd_clear()

#Motor
Motor = MOSFETController(22)

#Global Buttons
print("Button Set")
B1 = Button(11, GPIO.IN, GPIO.PUD_UP)
B2 = Button(13, GPIO.IN, GPIO.PUD_UP)
B3 = Button(15, GPIO.IN, GPIO.PUD_UP)

#Global Sensors
print("DistanceFinder Set")
DistanceFinder = Ultrasonic(8, 10)

#--------- DEFAULT FUNCTIONS ---------#

#Initialisation
def InitialiseProgram():
    Display.lcd_clear() #Clear display
    SyncMotor() #Sync the motor
    
    ContinuousSysUpdates.Start() #Start SysUpdateThread
    RequestHandler.Start()

    RequestHandler.Mode.value = SETTINGS
    RequestHandler.System.value = MAIN_SETTINGS

#Termination
def TerminateProgram():
    print("PillDispenser.py: Cleaningup")
    GPIO.cleanup() #Reset GPIO pins on termination
    ContinuousSysUpdates.Stop() #Terminate SysUpdate thread
    RequestHandler.Stop() #Terminate RequestHandler

#Halt the program until a request or timeout is reached
class Await:
    def __init__(Self, Val, Condition, Operator, MeanwhileFunc = None):
        Self.Timeout = 0
        Self.PrevTime = time.time()
        Self.Operator = Operator
        Self.Val = Val
        Self.Condition = Condition
        Self.Operator = Operator
        Self.MeanwhileFunc = MeanwhileFunc #Function that runs in the background whilst waiting

    def Wait(Self):
        Self.PrevTime = time.time()
        if (Self.Operator == 0):
            while(Self.Val.value == Self.Condition and Self.Timeout < 5):
                Self.Timeout += time.time() - Self.PrevTime
                Self.PrevTime = time.time()
                if (Self.MeanwhileFunc != None):
                    Self.MeanwhileFunc()
        else:
            while(Self.Val.value != Self.Condition and Self.Timeout < 5):
                Self.Timeout += time.time() - Self.PrevTime
                Self.PrevTime = time.time()
                if (Self.MeanwhileFunc != None):
                    Self.MeanwhileFunc()

#--------- DISPENSER MODES AND CONSTANTS ---------#

#Current pill dispenser mode
MAIN_RUNNING = 0
MAIN_SETTINGS = 1

RUNNING = 1
SETTINGS = 2
SETTINGS_CLOCK = 3
SETTINGS_TIMING = 4

#<<<<<<<<< INTERNAL FUNCTIONS >>>>>>>>>#

#--------- SETTINGS FUNCTIONS ---------#

def Settings(): #Settings Mode manager -> Selects what function to run
    if (RequestHandler.System.value != MAIN_SETTINGS): #validation of mode
        return
    if (RequestHandler.Mode.value == SETTINGS):
        _Settings()
    elif (RequestHandler.Mode.value == SETTINGS_CLOCK):
        SettingsClock()
    elif (RequestHandler.Mode.value == SETTINGS_TIMING):
        SettingsTiming()

def _Settings(): #Settings menu
    LCDClear()

    #Settings menu program global variables
    Option = 0 #Option -> which setting function you want to go to
    OptionMap = [
        -1, #Cancel call
        SETTINGS_CLOCK,
        SETTINGS_TIMING
    ]
   
    #Settings menu loop -> Runs settings specific functions
    while (True):
        LCDPrint("Setup Dispenser", 1)
        
        if (RequestHandler.Mode.value != SETTINGS): #Validation of mode
            break
        
        #Display current selected option
        if (OptionMap[Option] == SETTINGS_CLOCK):
            LCDPrint("Clock", 2)
        elif (OptionMap[Option] == SETTINGS_TIMING):
            LCDPrint("Configure Timing", 2)
        else:
            LCDPrint("Done ?", 2)

        #Button checks
        if (B1.OnKeyUp()):
            Option -= 1
        elif (B2.OnKeyUp()):
            Option += 1
        elif (B3.OnKeyUp()):
            if (OptionMap[Option] == -1): #Cancel call
                RequestHandler.System.value = MAIN_RUNNING #Set system mode
                RequestHandler.Mode.value = RUNNING #Set mode
                break #Break out of settings menu
            else:
                RequestHandler.Mode.value = OptionMap[Option] #Set mode
                break #Break out of settings menu
            
        if (Option >= len(OptionMap)):
            Option = 0
        elif (Option < 0):
            Option = len(OptionMap) - 1

        SysUpdates()

def SettingsTiming(): #Settings timing menu
    LCDClear()

    #SettingsTiming global variables
    Option = 0

    EditMode = False

    #flashing animation
    FlashTimer = time.time()
    Flash = False #Flashing in or flashing out

    while(True):
        if (RequestHandler.Mode.value != SETTINGS_TIMING): #Mode validation
            break
        
        #Flashing animation
        CurrentTime = time.time()
        Delay = 1
        if (Flash):
            Delay = 0.2
        if (CurrentTime - FlashTimer > Delay):
            FlashTimer = CurrentTime
            Flash = not(Flash)

        if (Option == -1):
            LCDPrint("Done ?", 1)
            LCDPrint("", 2)
        elif (Option == RequestHandler.SharedDispenseTimeCount.value):
            LCDPrint("New Timing ?", 1)
            LCDPrint("", 2)
        else:
            #Display options
            LCDPrint("Dispense Time " + str(Option + 1), 1)
            RequestHandler.GetDispenseTiming(Option)
            W = Await(RequestHandler.SharedDispenseTimingGetRequest, True, 0)
            W.Wait()
            LCDPrint(RequestHandler.SharedDispenseTimingGetStr.value, 2)

        #Button checks
        if (not(EditMode)):
            if (B1.OnKeyUp()):
                Option -= 1
            elif (B2.OnKeyUp()):
                Option += 1
            elif (B3.OnKeyUp()):
                if (Option == -1): #Cancel call
                    RequestHandler.System.value = MAIN_SETTINGS #Set system mode
                    RequestHandler.Mode.value = SETTINGS #Set mode
                    break #Break out of settings menu
                elif (Option == RequestHandler.SharedDispenseTimeCount.value):
                    Index = RequestHandler.SharedDispenseTimeCount.value
                    RequestHandler.SetDispenseTiming(RequestHandler.SharedDispenseTimeCount.value, 0, 0)
                    while(True):
                        #Flashing animation
                        CurrentTime = time.time()
                        Delay = 1
                        if (Flash):
                            Delay = 0.2
                        if (CurrentTime - FlashTimer > Delay):
                            FlashTimer = CurrentTime
                            Flash = not(Flash)
                        
                        LCDPrint("Change Hour", 1)

                        RequestHandler.GetDispenseTiming(Index)
                        W = Await(RequestHandler.SharedDispenseTimingGetRequest, True, 0)
                        W.Wait()
                        String = RequestHandler.SharedDispenseTimingGetStr.value
                        if (Flash):
                            LCDPrint("  " + String[2:8], 2)
                        else:
                            LCDPrint(String, 2)

                        if (B1.OnKeyUp()):
                            RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                            RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = -1
                            RequestHandler.SharedDispenseUpdateTimeStampSetHour.value = True
                        elif (B2.OnKeyUp()):
                            RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                            RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = 1
                            RequestHandler.SharedDispenseUpdateTimeStampSetHour.value = True
                        elif (B3.OnKeyUp()): #cancel call
                            break #Break out of settings menu

                        SysUpdates()
                    while(True):
                        #Flashing animation
                        CurrentTime = time.time()
                        Delay = 1
                        if (Flash):
                            Delay = 0.2
                        if (CurrentTime - FlashTimer > Delay):
                            FlashTimer = CurrentTime
                            Flash = not(Flash)
                        
                        LCDPrint("Change Minute", 1)

                        RequestHandler.GetDispenseTiming(Index)
                        W = Await(RequestHandler.SharedDispenseTimingGetRequest, True, 0)
                        W.Wait()
                        String = RequestHandler.SharedDispenseTimingGetStr.value
                        if (Flash):
                            LCDPrint(String[0:3] + "  " + String[5:8], 2)
                        else:
                            LCDPrint(String, 2)

                        if (B1.OnKeyUp()):
                            RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                            RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = -1
                            RequestHandler.SharedDispenseUpdateTimeStampSetMinute.value = True
                        elif (B2.OnKeyUp()):
                            RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                            RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = 1
                            RequestHandler.SharedDispenseUpdateTimeStampSetMinute.value = True
                        elif (B3.OnKeyUp()): #cancel call
                            break #Break out of settings menu

                        SysUpdates()
                    
                else:
                    SettingsTiming_Edit(Option)

        if (Option < -1):
            Option = RequestHandler.SharedDispenseTimeCount.value - 1
        elif (Option > RequestHandler.SharedDispenseTimeCount.value):
            Option = -1

        SysUpdates()

def SettingsTiming_Edit(Index): #Settings timing menu
    LCDClear()

    #SettingsTiming_Edit global variables
    Option = 0

    #flashing animation
    FlashTimer = time.time()
    Flash = False #Flashing in or flashing out

    EditMode = False

    while(True):
        if (RequestHandler.Mode.value != SETTINGS_TIMING): #Mode validation
            break

        if (Option == 0):
            LCDPrint("Change ?", 2)
        elif (Option == 1):
            LCDPrint("Delete ?", 2)
        elif (Option == 2):
            LCDPrint("Cancel ?", 2)

        #Button checks
        if (not(EditMode)):
            if (B1.OnKeyUp()):
                Option -= 1
            elif (B2.OnKeyUp()):
                Option += 1
            elif (B3.OnKeyUp()):
                if (Option == 0): #Cancel call
                    EditMode = True
                elif (Option == 1):
                    RequestHandler.SetDispenseDel(Index, Index + 1)
                    break
                elif (Option == 2):
                    break
        else:
            while(True):
                #Flashing animation
                CurrentTime = time.time()
                Delay = 1
                if (Flash):
                    Delay = 0.2
                if (CurrentTime - FlashTimer > Delay):
                    FlashTimer = CurrentTime
                    Flash = not(Flash)
                
                LCDPrint("Change Hour", 1)

                RequestHandler.GetDispenseTiming(Index)
                W = Await(RequestHandler.SharedDispenseTimingGetRequest, True, 0)
                W.Wait()
                String = RequestHandler.SharedDispenseTimingGetStr.value
                if (Flash):
                    LCDPrint("  " + String[2:8], 2)
                else:
                    LCDPrint(String, 2)

                if (B1.OnKeyUp()):
                    RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                    RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = -1
                    RequestHandler.SharedDispenseUpdateTimeStampSetHour.value = True
                elif (B2.OnKeyUp()):
                    RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                    RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = 1
                    RequestHandler.SharedDispenseUpdateTimeStampSetHour.value = True
                elif (B3.OnKeyUp()): #cancel call
                    break #Break out of settings menu

                SysUpdates()
            while(True):
                #Flashing animation
                CurrentTime = time.time()
                Delay = 1
                if (Flash):
                    Delay = 0.2
                if (CurrentTime - FlashTimer > Delay):
                    FlashTimer = CurrentTime
                    Flash = not(Flash)
                
                LCDPrint("Change Minute", 1)

                RequestHandler.GetDispenseTiming(Index)
                W = Await(RequestHandler.SharedDispenseTimingGetRequest, True, 0)
                W.Wait()
                String = RequestHandler.SharedDispenseTimingGetStr.value
                if (Flash):
                    LCDPrint(String[0:3] + "  " + String[5:8], 2)
                else:
                    LCDPrint(String, 2)

                if (B1.OnKeyUp()):
                    RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                    RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = -1
                    RequestHandler.SharedDispenseUpdateTimeStampSetMinute.value = True
                elif (B2.OnKeyUp()):
                    RequestHandler.SharedDispenseUpdateTimeStampSetIndex.value = Index
                    RequestHandler.SharedDispenseUpdateTimeStampSetMode.value = 1
                    RequestHandler.SharedDispenseUpdateTimeStampSetMinute.value = True
                elif (B3.OnKeyUp()): #cancel call
                    break #Break out of settings menu

                SysUpdates()
            break

        if (Option < 0):
            Option = 2
        elif (Option > 2):
            Option = 0

        SysUpdates()
    
def SettingsClock(): #Settings clock menu
    LCDClear()

    #SettingsClock global variables
    Option = 0
    OptionMap = [
        0, #Format 24hr or 12hr
        1, #change hour
        2, #change minute
        3, #change day
        4, #change month
        5, #change year
        -1 #Cancel call
    ]

    EditMode = False

    #flashing animation
    FlashTimer = time.time()
    Flash = False #Flashing in or flashing out

    #SettingsClock menu loop
    while(True):
        if (RequestHandler.Mode.value != SETTINGS_CLOCK): #Check mode validation
            break
        
        #Flashing animation
        CurrentTime = time.time()
        Delay = 1
        if (Flash):
            Delay = 0.2
        if (CurrentTime - FlashTimer > Delay):
            FlashTimer = CurrentTime
            Flash = not(Flash)
        
        #Display options on Display
        if (OptionMap[Option] == 0):
            LCDPrint("Format?", 1)
            if (Flash and EditMode == True):
                LCDPrint("", 2)
            else:
                if (RequestHandler.SharedDispenseTime24.value):
                    LCDPrint("24 hour", 2)
                else:
                    LCDPrint("12 hour", 2)
                
        elif (OptionMap[Option] == 1):
            LCDPrint("Change Hour?", 1)
            if (Flash and EditMode == True):
                if (RequestHandler.SharedDispenseTime24.value):
                    RequestHandler.SharedTimeStringFormat.value = "  :%M:%S"
                    W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                    W.Wait()
                    LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
                else:
                    RequestHandler.SharedTimeStringFormat.value = "  :%M:%S"
                    W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                    W.Wait()
                    LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            else:
                LCDPrint(RequestHandler.SharedTimeString.value, 2)
            
        elif (OptionMap[Option] == 2):
            LCDPrint("Change Minute?", 1)
            if (Flash and EditMode == True):
                if (RequestHandler.SharedDispenseTime24.value):
                    RequestHandler.SharedTimeStringFormat.value = "%H:  :%S"
                    W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                    W.Wait()
                    LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
                else:
                    RequestHandler.SharedTimeStringFormat.value = "%l:  :%S"
                    W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                    W.Wait()
                    LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            else:
                LCDPrint(RequestHandler.SharedTimeString.value, 2)
            
        elif (OptionMap[Option] == 3):
            LCDPrint("Change Day?", 1)
            if (Flash and EditMode == True):
                RequestHandler.SharedTimeStringFormat.value = "  /%m/%Y"
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            else:
                RequestHandler.SharedTimeStringFormat.value = "%d/%m/%Y"
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            
        elif (OptionMap[Option] == 4):
            LCDPrint("Change Month?", 1)
            if (Flash and EditMode == True):
                RequestHandler.SharedTimeStringFormat.value = "%d/  /%Y"
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            else:
                RequestHandler.SharedTimeStringFormat.value = "%d/%m/%Y"
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            
        elif (OptionMap[Option] == 5):
            LCDPrint("Change Year?", 1)
            if (Flash and EditMode == True):
                RequestHandler.SharedTimeStringFormat.value = "%d/%m/  "
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            else:
                RequestHandler.SharedTimeStringFormat.value = "%d/%m/%Y"
                W = Await(RequestHandler.SharedTimeStringFormat, "", 1)
                W.Wait()
                LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 2)
            
        else:
            LCDPrint("Done ?", 1)
            LCDPrint("", 2)
            
        #Button checks
        if (not(EditMode)):
            if (B1.OnKeyUp()):
                Option -= 1
            elif (B2.OnKeyUp()):
                Option += 1
            elif (B3.OnKeyUp()):
                if (OptionMap[Option] == -1): #Cancel call
                    RequestHandler.System.value = MAIN_SETTINGS #Set system mode
                    RequestHandler.Mode.value = SETTINGS #Set mode
                    break #Break out of settings menu
                else:
                    EditMode = True
        else: #Update time and dispensetimings
            if (B1.OnKeyUp()):
                RequestHandler.SharedDispenseUpdateTimingSetMode.value = -1
                if (OptionMap[Option] == 0):
                    RequestHandler.SharedDispenseTime24.value = not(RequestHandler.SharedDispenseTime24.value)
                elif (OptionMap[Option] == 1):
                    RequestHandler.SharedDispenseUpdateTimingSetHour.value = True
                elif (OptionMap[Option] == 2):
                    RequestHandler.SharedDispenseUpdateTimingSetMinute.value = True
                elif (OptionMap[Option] == 3):
                    RequestHandler.SharedDispenseUpdateTimingSetDay.value = True
                elif (OptionMap[Option] == 4):
                    RequestHandler.SharedDispenseUpdateTimingSetMonth.value = True
                elif (OptionMap[Option] == 5):
                    RequestHandler.SharedDispenseUpdateTimingSetYear.value = True
            elif (B2.OnKeyUp()):
                RequestHandler.SharedDispenseUpdateTimingSetMode.value = 1
                if (OptionMap[Option] == 0):
                    RequestHandler.SharedDispenseTime24.value = not(RequestHandler.SharedDispenseTime24.value)
                elif (OptionMap[Option] == 1):
                    RequestHandler.SharedDispenseUpdateTimingSetHour.value = True
                elif (OptionMap[Option] == 2):
                    RequestHandler.SharedDispenseUpdateTimingSetMinute.value = True
                elif (OptionMap[Option] == 3):
                    RequestHandler.SharedDispenseUpdateTimingSetDay.value = True
                elif (OptionMap[Option] == 4):
                    RequestHandler.SharedDispenseUpdateTimingSetMonth.value = True
                elif (OptionMap[Option] == 5):
                    RequestHandler.SharedDispenseUpdateTimingSetYear.value = True
            elif (B3.OnKeyUp()):
                EditMode = False

        if (Option >= len(OptionMap)):
            Option = 0
        elif (Option < 0):
            Option = len(OptionMap) - 1

        SysUpdates()

    #If something breaks go back to settings
    RequestHandler.System.value = MAIN_SETTINGS #Set system mode
    RequestHandler.Mode.value = SETTINGS #Set mode
    

#--------- RUNNING FUNCTIONS ---------#

#Update time
def UpdateButtons(): #Update buttons
    B1.Update()
    B2.Update()
    B3.Update()

def Running(): #Run mode manager
    if (RequestHandler.System.value != MAIN_RUNNING): #System mode validation
        return
    if (RequestHandler.Mode.value == RUNNING):
        Run() #Run pill dispenser

def Run():
    #flashing animation for run loop
    FlashTimer = time.time()
    Flash = False #Flashing in or flashing out

    #Run menu loop
    while(True):
        if (RequestHandler.Mode.value != RUNNING): #Mode validation
            break
        
        #Flashing animation
        CurrentTime = time.time()
        Delay = 1
        if (Flash):
            Delay = 0.2
        if (CurrentTime - FlashTimer > Delay):
            FlashTimer = CurrentTime
            Flash = not(Flash)
            
        #Display time
        RequestHandler.SharedTimeStringFormat.value = "%d/%m/%Y"
        W = Await(RequestHandler.SharedTimeStringFormat, "", 1, Dispenser)
        W.Wait()
        LCDPrint(RequestHandler.SharedTimeStringFormatted.value, 1)
        LCDPrint(RequestHandler.SharedTimeString.value, 2)

        Dispenser() #Dispenser functions

        if (B3.OnKeyUp()): #Enter settings on button press
            RequestHandler.Mode.value = SETTINGS
            RequestHandler.System.value = MAIN_SETTINGS
            break

        SysUpdates()

#Update the Pill Dispenser -> parameters are shared values from outside of process
def Update():
    try:

        #Enter a function depending on system
        if (RequestHandler.System.value == MAIN_RUNNING):
            Running() #Run run function
        elif (RequestHandler.System.value == MAIN_SETTINGS):
            Settings() #Run Settings function

        SysUpdates()
        
    except KeyboardInterrupt:
        print("Terminating")
        TerminateProgram()
    except:
        print("TRACEBACK - PillDispenser")
        traceback.print_exc()
        
#Updates that have to occure at the end of each frame, but not during Halts
def SysUpdates():
    UpdateButtons() #Update button input checks
    
    CheckTampering() #Check that the dispenser isnt being tampered with
    
    #Check for termination
    if (Terminate.value):
        TerminateProgram()
        Terminate.value = False

def CheckTampering():
    if (ContinuousSysUpdates.S1.GetInput()):
        LCDPrint("Please do not", 1)
        LCDPrint("rotate", 2)
    while (ContinuousSysUpdates.S1.GetInput()):
        Motor.Waddle()

#TODO:: Port all these get set functions to another thread

#--------- PILL DISPENSER FUNCTIONS STARTER ---------#

def Dispenser(): #Actual operation of dispenser
    #Check ultrasonic sensor
    Measurement = DistanceFinder.GetMeasurement()
    
    if (Measurement < 10): #less than 10cm
        #Check Timing and trigger drop
        RequestHandler.SharedDropped.value = True #Trigger drop pill

        #Wait for response from RequestHandler
        W = Await(RequestHandler.SharedDropped, True, 0)
        W.Wait()
        
        #If do drop command is not active then time is not correct
        if (RequestHandler.SharedDoDrop.value == False):
            LCDPrint("It is not time", 1)
            LCDPrint("yet!", 2)
            time.sleep(2)
            return
        
        DropPill()

def DropPill():
    LCDPrint("Dropping Pill...", 1)

    for i in range (0, ContinuousSysUpdates.MultipleOfSegments.value):
        #Rotate motor one switch notch
        while (ContinuousSysUpdates.S1.GetInput()):
            Motor.Waddle()
        while (not(ContinuousSysUpdates.S1.GetInput())):
            Motor.Waddle()
        while (ContinuousSysUpdates.S1.GetInput()):
            Motor.Waddle()
    
    Motor.State(GPIO.LOW)
    return

def SyncMotor(): #Syncs motor with switch
    print("Syncing Motor...")
    print("Searching for Pin")
    LCDPrint("Syncing Motor...", 1)
    while (not(ContinuousSysUpdates.S1.GetInput())):
        Motor.Waddle()
    print("Pin found")
    print("Searching for Gap")
    while (ContinuousSysUpdates.S1.GetInput()):
        Motor.Waddle()
    print("Gap found")
    print("Sync finished...")
    ContinuousSysUpdates.RotationNum.value = 0

#--------- PROGRAM STARTER ---------#

Terminate = Value('i', False)

def Loop():
    try:
        while(True):
            Update()
    except KeyboardInterrupt:
        TerminateProgram()

#Start and stop the program
def DispenserStart():
    print("Initialising")
    LCDPrint("Initialising", 1)
    InitialiseProgram()
    print("Starting loop")
    DispenserRun.start()

def DispenserStop():
    print("Terminating Process")
    PrevTime = time.time()
    Time = 0
    while (Terminate.value == True):
        print("PillDispenser: Awaiting Termination (" + str(Time) + ")")
        Time += time.time() - PrevTime
        PrevTime = time.time()
        if (Time >= 5):
            print("PillDispenser: Termination of GPIO Failed, terminating thread")
            break
        continue
    print("Terminated")
    DispenserRun.terminate()


#Create process for start program
DispenserRun = Process(target=Loop, args=())


