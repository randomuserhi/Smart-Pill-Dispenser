#Multi threading
from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array

#Time
import time
import datetime
from dateutil.relativedelta import relativedelta

#Import GPIO inputs
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD) #Set GPIO mode the board pin numbers

#Error handling
import traceback

#This script handles all components which require being checked constantly without pause and shared variables between pill dispenser and website
#   This is because PillDispenser.py handles most of the UI elements causing it to have pauses and so this acts as the main update thread
#   Think of it as the monitor and your cpu, this is the cpu and PillDispenser.py is the monitor

#TODO:: Add something similar to Missed pills that logs time of forced movement of segment

#----------- Object Definitions ------------

#Internal Clock
class Clock:
    def __init__(Self, Hr24):
        Self.Hr24 = Hr24;
        Self.Format24 = "%H:%M:%S"
        Self.Format12 = "%l:%M:%S"
        Self.Time = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        Self.TimeDelay = time.time()

    def Update(Self):
        CurrentTime = time.time()
        DeltaTime = CurrentTime - Self.TimeDelay #Calculate DeltaTime
        Self.Time += datetime.timedelta(seconds = DeltaTime) #Add DeltaTime to current time
        Self.TimeDelay = CurrentTime
        
    def StrTime(Self):
        if (Self.Hr24):
            return Self.Time.strftime(Self.Format24)
        else:
            return Self.Time.strftime(Self.Format12)

    def CustomStrTime(Self, Format24hr, Format12hr):
        if (Self.Hr24):
            return Self.Time.strftime(Format24hr)
        else:
            return Self.Time.strftime(Format12hr)

    def CustomStrTimeSingle(Self, Format):
        return Self.Time.strftime(Format)

#Time stamps
class TimeStamp:
    def __init__(Self, Hour, Minute, Second, Valid = True):
        try:
            Self.Time = datetime.datetime(2000, 1, 1, Hour, Minute, Second, 0)
        except Exception as e:
            print "An unexpected error occured with datetime"
            traceback.print_exc()
            Self.Time = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        Self.Valid = Valid
        Self.Logged = False
        Self.LastValidDay = datetime.datetime(Time.Time.year, Time.Time.month, Time.Time.day, 0, 0, 0, 0)

    #returns itself as a datetime
    def DateTime(Self):
        return datetime.datetime(Time.Time.year, Time.Time.month, Time.Time.day, Self.Time.hour, Self.Time.minute, Self.Time.second, Time.Time.microsecond) #Get todays time

    def StrTime(Self):
        if (Time.Hr24):
            return Self.DateTime().strftime(Time.Format24)
        else:
            return Self.DateTime().strftime(Time.Format12)

    def CustomStrTime(Self, Format24hr, Format12hr):
        if (Time.Hr24):
            return Self.DateTime().strftime(Format24hr)
        else:
            return Self.DateTime().strftime(Format12hr)

    def CustomStrTimeSingle(Self, Format):
        return Self.DateTime().strftime(Format)

    #Returns true if the datetime given is within the margin of this timestamp
    def CompareDateTime(Self, DateTime, Min, Max):
        DateNow = Self.DateTime() #Get todays time
        #return boolean
        return DateNow - Min <= DateTime <= DateNow + Max

    def CompareDateTimes(Self, DateTime1, DateTime2, Min, Max):
        #return boolean
        return DateTime2 - Min <= DateTime1 <= DateTime2 + Max

    def UpdateLastValidDay(Self):
        if (Self.LastValidDay + relativedelta(days = 1) <= Time.Time):
            Self.Valid = True
        else:
            Self.Valid = False

    def UpdateValid(Self):
        if (Self.Valid == False and (Self.LastValidDay + relativedelta(days = 1) <= Time.Time)):
            Self.Valid = True
            Self.Logged = False
        elif (Self.Valid == True):
            Self.Valid = False
            Self.LastValidDay = datetime.datetime(Time.Time.year, Time.Time.month, Time.Time.day, 0, 0, 0, 0)
            Self.Logged = False
            return True
        return False

#Buzzer Object
class Buzzer:
    def __init__(Self, PinNumber):
        Self.Pin = PinNumber
        Self.Enabled = True

        #Setup GPIO for buzzer
        GPIO.setup(Self.Pin, GPIO.OUT)

    def SetOutput(Self, Out):
        if (Self.Enabled == False):
            return
        if (Out):
            GPIO.output(Self.Pin, 1) #Turn output to buzzer to HIGH
        else:
            GPIO.output(Self.Pin, 0) #Turn output to buzzer to LOW
    
#LED object
class LED:
    def __init__(Self, PinNumber):
        Self.Pin = PinNumber

        #Setup GPIO for LED
        GPIO.setup(Self.Pin, GPIO.OUT)

    def SetOutput(Self, Out):
        if (Out):
            GPIO.output(Self.Pin, 1) #Turn output to LED to HIGH
        else:
            GPIO.output(Self.Pin, 0) #Turn output to LED to LOW

#----------- Object Definition of variables ------------

#Components
#Buzzer
Piezo = Buzzer(16)
Piezo.Enabled = True

#LED
Light = LED(12)

#Clock
Time = Clock(True)
    
#Times when a pill needs to be dispensed
DispenseTiming = [TimeStamp(8, 0, 0), TimeStamp(12, 0, 0), TimeStamp(18, 0, 0)]

MissedTiming = [] #All of the times that pills were missed
ForcedTiming = [] #All of the times that user forced pills out

SharedInitialisationStatus = False #Has the pill dispenser started yet

#------------ Shared Variable definitions ------------

#Shared variables for Time
SharedTimeString = Array('c', "                             ")
SharedTimeStringFormatted = Array('c', "                             ")
SharedTimeStringFormat = Array('c', "                             ")
SharedDispenseTime24 = Value('i', True)

#Get length of DispenseTimingArray
SharedDispenseTimeCount = Value('i', 000)

#Shared variables for setting a value in DispenseTiming array
SharedDispenseTimingSetRequest = Value('i', False)
SharedDispenseTimingSetIndex = Value('i', 000)
SharedDispenseTimingSetHour = Value('i', 000)
SharedDispenseTimingSetMinute = Value('i', 000)
SharedDispenseTimingGetRequest = Value('i', False)
SharedDispenseTimingGetIndex = Value('i', 000)
SharedDispenseTimingGetStr = Array('c', "                             ")

#Shared variables for removing timings from DispenseTiming array
SharedDispenseTimingDelRequest = Value('i', False)
SharedDispenseTimingDelRangeIndex = Value('i', 0000)
SharedDispenseTimingDelRangeCount = Value('i', 0000)

#Shared variables for updating time from being changed via UI under PillDispenser.py
SharedDispenseUpdateTimingSetHour = Value('i', False)
SharedDispenseUpdateTimingSetMinute = Value('i', False)
SharedDispenseUpdateTimingSetSecond = Value('i', False)
SharedDispenseUpdateTimingSetDay = Value('i', False)
SharedDispenseUpdateTimingSetMonth = Value('i', False)
SharedDispenseUpdateTimingSetYear = Value('i', False)
SharedDispenseUpdateTimingSetMode = Value('i', 00)

#Shared variables for updating timestamps from being changed via UI under PillDispenser.py
SharedDispenseUpdateTimeStampSetHour = Value('i', False)
SharedDispenseUpdateTimeStampSetMinute = Value('i', False)
SharedDispenseUpdateTimeStampSetMode = Value('i', 00)
SharedDispenseUpdateTimeStampSetIndex = Value('i', 0000)

#Shared variables for setting the time via web page
SharedDispenseTimeSetRequest = Value('i', False)
SharedDeltaUpdate = Value('i', 0000)
SharedDispenseTimeSetHour = Value('i', 0000)
SharedDispenseTimeSetMinute = Value('i', 0000)
SharedDispenseTimeSetSecond = Value('i', 0000)
SharedDispenseTimeSetMillisecond = Value('i', 0000)
SharedDispenseTimeSetDay = Value('i', 0000)
SharedDispenseTimeSetMonth = Value('i', 0000)
SharedDispenseTimeSetYear = Value('i', 0000)

#Shared variable that is true when its time to drop the pills
SharedTimeToDrop = Value('i', False)
SharedDropped = Value('i', False) #Shared variable whether pill has been dropped
SharedDoDrop = Value('i', False) #Trigger motor for drop

SharedTimeNextDrop = Array('c', "                      ")
SharedTimeToNextDrop = Array('c', "                                                           ")

#Shared variables that determines whether the dispenser has been setup yet via the website
SharedDispenseInitialisationStatus = Value('i', False)

#TODO:: initialise these
SharedMissedTimingCount = Value('i', 0000)
SharedMissedTimingIndex = Value('i', 000)
SharedMissedTimingStr = Array('c', "                             ")

PillData = Array('c', "000000000000000000000000000000000000000") #What pills are inside dispenser (assumed)

#Shared variables for System and Mode of Pill Dispenser
System = Value('i', 0)
Mode = Value('i', 0)

#Current pill dispenser mode constants
MAIN_RUNNING = 0
MAIN_SETTINGS = 1

RUNNING = 1
SETTINGS = 2
SETTINGS_CLOCK = 3
SETTINGS_TIMING = 4
    
def Update():
    try:
        while(True):
            UpdateSharedVariables()
            if (Terminate.value == True):
                print("RequestHandler.py: Cleaningup")
                GPIO.cleanup()
                Terminate.value = False
                break
    except KeyboardInterrupt:
        print("Terminating")
        GPIO.cleanup()
    except:
        print("TRACEBACK - RequestHandler")
        traceback.print_exc()

#Initialises shared variable for the thread
def InitialiseSharedWrappers(ParsedSystem, ParsedMode, DoDrop, Dropped, TimeToDrop, TimeStringFormat, TimeStringFormatted, DispenseTime24, DeltaUpdate, TimeString, \
                                            DispenseTimeCount, \
                                            DispenseTimingSetIndex, DispenseTimingSetHour, DispenseTimingSetMinute, \
                                            DispenseTimingGetRequest, DispenseTimingGetIndex, DispenseTimingGetStr, \
                                            DispenseTimeSetHour, DispenseTimeSetMinute, \
                                            DispenseTimeSetSecond, DispenseTimeSetMillisecond, DispenseTimeSetDay, DispenseTimeSetMonth, \
                                            DispenseTimeSetYear, DispenseTimeSetRequest, DispenseTimingSetRequest, \
                                            DispenseInitialisationStatus, \
                                            DispenseTimingDelRequest, DispenseTimingDelRangeIndex, DispenseTimingDelRangeCount, \
                                            DispenseUpdateTimingSetHour, DispenseUpdateTimingSetMinute, DispenseUpdateTimingSetSecond, DispenseUpdateTimingSetDay, DispenseUpdateTimingSetMonth, DispenseUpdateTimingSetYear, \
                                            DispenseUpdateTimingSetMode, MissedTimingCount, MissedTimingIndex, MissedTimingStr, \
                                            DispenseUpdateTimeStampSetHour, DispenseUpdateTimeStampSetMinute, DispenseUpdateTimeStampSetMode, DispenseUpdateTimeStampSetIndex, \
                                            TimeNextDrop, TimeToNextDrop, ParsedPillData):

    global System, Mode
    System = ParsedSystem
    Mode = ParsedMode

    global PillData
    PillData = ParsedPillData

    global SharedTimeNextDrop, SharedTimeToNextDrop
    SharedTimeNextDrop = TimeNextDrop
    SharedTimeToNextDrop = TimeToNextDrop

    global SharedDispenseUpdateTimeStampSetHour, SharedDispenseUpdateTimeStampSetMinute, SharedDispenseUpdateTimeStampSetMode, SharedDispenseUpdateTimeStampSetIndex
    SharedDispenseUpdateTimeStampSetHour = DispenseUpdateTimeStampSetHour
    SharedDispenseUpdateTimeStampSetMinute = DispenseUpdateTimeStampSetMinute
    SharedDispenseUpdateTimeStampSetMode = DispenseUpdateTimeStampSetMode
    SharedDispenseUpdateTimeStampSetIndex = DispenseUpdateTimeStampSetIndex

    global SharedMissedTimingCount, SharedMissedTimingIndex, SharedMissedTimingStr
    SharedMissedTimingCount = MissedTimingCount
    SharedMissedTimingIndex = MissedTimingIndex
    SharedMissedTimingStr = MissedTimingStr

    global SharedTimeToDrop, SharedDropped, SharedDoDrop
    SharedDoDrop = DoDrop
    SharedTimeToDrop = TimeToDrop
    SharedDropped = Dropped

    global SharedTimeStringFormatted, SharedTimeStringFormat
    SharedTimeStringFormatted = TimeStringFormatted
    SharedTimeStringFormat = TimeStringFormat
    SharedTimeStringFormat.value = ""

    global SharedDispenseInitialisationStatus
    SharedDispenseInitialisationStatus = DispenseInitialisationStatus
    
    global SharedDispenseTime24, SharedTimeString, SharedDispenseTimeCount, SharedDeltaUpdate
    SharedDispenseTime24 = DispenseTime24
    SharedDeltaUpdate = DeltaUpdate
    SharedTimeString = TimeString
    SharedDispenseTimeCount = DispenseTimeCount
    
    global SharedDispenseTimingSetIndex, SharedDispenseTimingSetHour, SharedDispenseTimingSetMinute, SharedDispenseTimingSetRequest
    SharedDispenseTimingSetRequest = DispenseTimingSetRequest
    SharedDispenseTimingSetIndex = DispenseTimingSetIndex
    SharedDispenseTimingSetHour = DispenseTimingSetHour
    SharedDispenseTimingSetMinute = DispenseTimingSetMinute

    global SharedDispenseTimingGetIndex, SharedDispenseTimingGet, SharedDispenseTimingGetRequest
    SharedDispenseTimingGetRequest = DispenseTimingGetRequest
    SharedDispenseTimingGetIndex = DispenseTimingGetIndex
    SharedDispenseTimingGetStr = DispenseTimingGetStr

    global SharedDispenseTimeSetRequest, SharedDispenseTimeSetHour, SharedDispenseTimeSetMinute, SharedDispenseTimeSetSecond, SharedDispenseTimeSetMillisecond, SharedDispenseTimeSetDay, SharedDispenseTimeSetMonth, SharedDispenseTimeSetYear
    SharedDispenseTimeSetRequest = DispenseTimeSetRequest
    SharedDispenseTimeSetHour = DispenseTimeSetHour
    SharedDispenseTimeSetMinute = DispenseTimeSetMinute
    SharedDispenseTimeSetSecond = DispenseTimeSetSecond
    SharedDispenseTimeSetMillisecond = DispenseTimeSetMillisecond

    global SharedDispenseTimingDelRequest, SharedDispenseTimingDelRangeIndex, SharedDispenseTimingDelRangeCount
    SharedDispenseTimingDelRequest = DispenseTimingDelRequest
    SharedDispenseTimingDelRangeIndex = DispenseTimingDelRangeIndex
    SharedDispenseTimingDelRangeCount = DispenseTimingDelRangeCount

    SharedDispenseTimeSetDay = DispenseTimeSetDay
    SharedDispenseTimeSetMonth = DispenseTimeSetMonth
    SharedDispenseTimeSetYear = DispenseTimeSetYear

    global SharedDispenseUpdateTimingSetHour, SharedDispenseUpdateTimingSetMinute, SharedDispenseUpdateTimingSetSecond, SharedDispenseUpdateTimingSetDay, SharedDispenseUpdateTimingSetMonth, SharedDispenseUpdateTimingSetYear
    SharedDispenseUpdateTimingSetHour = DispenseUpdateTimingSetHour
    SharedDispenseUpdateTimingSetMinute = DispenseUpdateTimingSetMinute
    SharedDispenseUpdateTimingSetSecond = DispenseUpdateTimingSetSecond
    SharedDispenseUpdateTimingSetDay = DispenseUpdateTimingSetDay
    SharedDispenseUpdateTimingSetMonth = DispenseUpdateTimingSetMonth
    SharedDispenseUpdateTimingSetYear = DispenseUpdateTimingSetYear

    Update()

def UpdateTime():
    UpdateTime_Get()
    UpdateTime_Set()

def UpdateTime_Set():
    
    #Update Formatted time string request
    if (SharedTimeStringFormat.value != ""):
        SharedTimeStringFormatted.value = Time.CustomStrTimeSingle(SharedTimeStringFormat.value)
        SharedTimeStringFormat.value = ""

    #Update Timings from UI
    if (SharedDispenseUpdateTimingSetHour.value == True):
        Time.Time += relativedelta(hours = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(hours = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetHour.value = False
        
    if (SharedDispenseUpdateTimingSetMinute.value == True):
        Time.Time += relativedelta(minutes = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(minutes = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetMinute.value = False
        
    if (SharedDispenseUpdateTimingSetSecond.value == True):
        Time.Time += relativedelta(seconds = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(seconds = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetSecond.value = False

    if (SharedDispenseUpdateTimingSetDay.value == True):
        Time.Time += relativedelta(days = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(days = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetDay.value = False

    if (SharedDispenseUpdateTimingSetMonth.value == True):
        Time.Time += relativedelta(months = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(months = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetMonth.value = False

    if (SharedDispenseUpdateTimingSetYear.value == True):
        Time.Time += relativedelta(years = SharedDispenseUpdateTimingSetMode.value)
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += relativedelta(years = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[i].UpdateLastValidDay()
        SharedDispenseUpdateTimingSetYear.value = False

    #Request for setting of time via website
    if (SharedDispenseTimeSetRequest.value == True): 
        Hour = SharedDispenseTimeSetHour.value
        Minute = SharedDispenseTimeSetMinute.value
        Second = SharedDispenseTimeSetSecond.value
        Millisecond = SharedDispenseTimeSetMillisecond.value
    
        Day = SharedDispenseTimeSetDay.value
        Month = SharedDispenseTimeSetMonth.value
        Year = SharedDispenseTimeSetYear.value

        try:
            NewTime = datetime.datetime(Year, Month, Day, Hour, Minute, Second, Millisecond)

            DeltaTime = NewTime - Time.Time

            for i in range(0, len(DispenseTiming)):
                DispenseTiming[i].LastValidDay += DeltaTime

            Time.Time = NewTime
        except Exception as e:
            print "An unexpected error occured with datetime"
            traceback.print_exc()
            
        SharedDispenseTimeSetRequest.value = False

def UpdateTime_Get():
    
    #Update Time object
    global Time
    Time.Update()
    Time.Hr24 = SharedDispenseTime24.value

    #Update shared values
    SharedTimeString.value = Time.StrTime()

    #Updating Timestamps on change of time
    if (SharedDeltaUpdate.value != 0):
        for i in range(0, len(DispenseTiming)):
            DispenseTiming[i].LastValidDay += SharedDeltaUpdate.value
        SharedDeltaUpdate.value = 0

def UpdateDispenseTiming():
    UpdateDispenseTiming_Get()
    UpdateDispenseTiming_Set()

def UpdateDispenseTiming_Get():
    SharedDispenseTimeCount.value = len(DispenseTiming)

    #Request to get DispenseTiming value 
    if (SharedDispenseTimingGetRequest.value == True):
        if (len(DispenseTiming) == 0):
            SharedDispenseTimingGetStr.value = "No Timings!"
        elif (SharedDispenseTimingGetIndex.value < len(DispenseTiming) and SharedDispenseTimingGetIndex.value >= 0):
            SharedDispenseTimingGetStr.value = DispenseTiming[SharedDispenseTimingGetIndex.value].StrTime()
        else:
            SharedDispenseTimingGetStr.value = "null"
        SharedDispenseTimingGetRequest.value = False

    #Get next pill time
    Closest = None
    for i in range(0, len(DispenseTiming)):
        Val = DispenseTiming[i].DateTime()
        if (Val < Time.Time):
            continue
        if (Closest == None or Val < Closest.DateTime()):
            Closest = DispenseTiming[i]
    if (Closest == None):
        for i in range(0, len(DispenseTiming)):
            Val = DispenseTiming[i].DateTime() + relativedelta(days = 1)
            if (Closest == None or Val < Closest.DateTime()):
                Closest = DispenseTiming[i]
    if (Closest != None):
        SharedTimeNextDrop.value = Closest.StrTime()
        Diff = Closest.DateTime() - Time.Time
        stringDiff = {"days": Diff.days}
        stringDiff["hours"], rem = divmod(Diff.seconds, 3600)
        stringDiff["minutes"], stringDiff["seconds"] = divmod(rem, 60)
        SharedTimeToNextDrop.value = "{hours}, hours and {minutes} minutes to go".format(**stringDiff)
    elif (len(DispenseTiming) == 0):
        SharedTimeNextDrop.value = "No Timings!"
        SharedTimeToNextDrop.value = "No Timings!"
    else:
        SharedTimeNextDrop.value = "null"
        SharedTimeToNextDrop.value = 0

def UpdateDispenseTiming_Set():
    #Update dispense timing from ui
    if (SharedDispenseUpdateTimeStampSetHour.value == True):
        if (SharedDispenseUpdateTimeStampSetIndex.value >= 0 and SharedDispenseUpdateTimeStampSetIndex.value < len(DispenseTiming)):
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].Time += relativedelta(hours = SharedDispenseUpdateTimeStampSetMode.value)
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].LastValidDay += relativedelta(hours = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].UpdateLastValidDay()
        SharedDispenseUpdateTimeStampSetHour.value = False
        
    if (SharedDispenseUpdateTimeStampSetMinute.value == True):
        if (SharedDispenseUpdateTimeStampSetIndex.value >= 0 and SharedDispenseUpdateTimeStampSetIndex.value < len(DispenseTiming)):
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].Time += relativedelta(minutes = SharedDispenseUpdateTimeStampSetMode.value)
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].LastValidDay += relativedelta(minutes = SharedDispenseUpdateTimingSetMode.value)
            DispenseTiming[SharedDispenseUpdateTimeStampSetIndex.value].UpdateLastValidDay()
        SharedDispenseUpdateTimeStampSetMinute.value = False
    
    #Request to delete a range of timestamps (although count is named count it is actually last index to delete (non-inclusive))
    if (SharedDispenseTimingDelRequest.value == True):
        if (SharedDispenseTimingDelRangeCount.value == -1): #Sets to last index (delete all items basically)
            SharedDispenseTimingDelRangeCount.value = len(DispenseTiming)
        if (SharedDispenseTimingDelRangeIndex.value >= 0 and SharedDispenseTimingDelRangeIndex.value < len(DispenseTiming) and SharedDispenseTimingDelRangeCount.value > 0 and SharedDispenseTimingDelRangeCount.value <= len(DispenseTiming)):
            del DispenseTiming[SharedDispenseTimingDelRangeIndex.value:SharedDispenseTimingDelRangeCount.value]
        SharedDispenseTimingDelRequest.value = False

    #Request for setting timings
    if (SharedDispenseTimingSetRequest.value == True): 
        if (SharedDispenseTimingSetIndex.value < 0 or SharedDispenseTimingSetIndex.value > len(DispenseTiming)):
            SharedDispenseTimingSetRequest.value = False #Invalid index end request
        elif (SharedDispenseTimingSetIndex.value == len(DispenseTiming)):
            DispenseTiming.append(TimeStamp(SharedDispenseTimingSetHour.value, SharedDispenseTimingSetMinute.value, 0))
        else:
            if (SharedDispenseTimingSetHour.value >= 0 and SharedDispenseTimingSetMinute.value >= 0):
                DispenseTiming[SharedDispenseTimingSetIndex.value] = TimeStamp(SharedDispenseTimingSetHour.value, SharedDispenseTimingSetMinute.value, 0)
            else:
                del DispenseTiming[SharedDispenseTimingSetIndex.value]
            SharedDispenseTimingSetRequest.value = False #End of request

def UpdateSystem():
    #Updates system calls
    global SharedInitialisationStatus
    if (SharedDispenseInitialisationStatus.value == True and SharedInitialisationStatus == False): #Initialise
        System.value = MAIN_RUNNING
        Mode.value = RUNNING
        SharedInitialisationStatus = True

def UpdatePillDrop():
    #Time range for when to dispense pills
    # TODO:: CHANGE CALCULATION OF MAX TIME TO BE A CURVE AS IF TIME BETWEEN PILLS IS LESS THAN 5 MINUTES PROBLEMS WILL OCCURE
    # PROBS:: ARBITARY NUMBER - (1 / (x^2))
    MinTime = 0
    MaxTime = 30

    global DispenseTiming

    #Check if Drop request has been triggered
    if (SharedDropped.value):
        SharedDoDrop.value = False #Reset whether to preform drop
        #Loop through and check if timings are valid
        for i in range(0, len(DispenseTiming)):
            if (DispenseTiming[i].CompareDateTime(Time.Time, relativedelta(minutes = MinTime), relativedelta(minutes = MaxTime)) and DispenseTiming[i].UpdateValid()):
                SharedDoDrop.value = True #Drop pill
                break
        SharedDropped.value = False #Reset Drop reques after check

    #Check timings for alerting user
    SharedTimeToDrop.value = False
    for i in range(0, len(DispenseTiming)):
        if (DispenseTiming[i].CompareDateTime(Time.Time, relativedelta(minutes = MinTime), relativedelta(minutes = MaxTime)) and DispenseTiming[i].Valid):
            #alert user to take their medication
            SharedTimeToDrop.value = True
        elif (DispenseTiming[i].CompareDateTime(Time.Time, relativedelta(minutes = MinTime), relativedelta(minutes = MaxTime + 10)) and DispenseTiming[i].Valid and DispenseTiming[i].Logged == False):
            #Medication Missed - log the time of miss
            global MissedTiming, LoggedMissedTiming
            print("Missed Pill") #TODO:: remove later
            MissedTiming.append(Time.StrTime())
            DispenseTiming[i].Logged = True

    #Trigger components to alert user
    if (SharedTimeToDrop.value and System.value == MAIN_RUNNING):
        Piezo.SetOutput(GPIO.HIGH)
        Light.SetOutput(GPIO.HIGH)
    else:
        Piezo.SetOutput(GPIO.LOW)
        Light.SetOutput(GPIO.LOW)

def UpdateMissedTiming():
    SharedMissedTimingCount.value = len(MissedTiming)
    #For this using -1 as request reference
    if (SharedMissedTimingIndex.value != -1):
        if (SharedMissedTimingIndex.value < len(MissedTiming) and SharedMissedTimingIndex.value >= 0):
            SharedMissedTimingStr = MissedTiming[SharedMissedTimingIndex.value]
        else:
            SharedMissedTimingStr = "null"
        SharedMissedTimingIndex.value = -1

#Update all shared variables
def UpdateSharedVariables():
    UpdateTime()
    UpdateDispenseTiming()
    UpdateSystem()
    UpdatePillDrop()
    UpdateMissedTiming()

def SetPillData(Val):
    global PillData
    PillData.value = Val
    print(PillData.value)
    return PillData.value

def GetPillData():
    global PillData
    return PillData.value

#Initialises the pill dispenser
def SharedInitialisation():
    global SharedDispenseInitialisationStatus
    SharedDispenseInitialisationStatus.value = True

#Sets Initialisation state of the pill dispenser
def SetInitialisationState(State):
    global SharedDispenseInitialisationStatus
    SharedDispenseInitialisationStatus.value = State
    return SharedDispenseInitialisationStatus.value

#Gets the state of initialisation
def GetInitialisationState():
    global SharedDispenseInitialisationStatus
    return SharedDispenseInitialisationStatus.value

#returns the time from the shared variable
def GetTime():
    global SharedTimeString
    return SharedTimeString.value

#returns the total number of Missed times
def GetMissedTimingCount():
    global SharedMissedTimingCount
    return SharedMissedTimingCount.value

#returns time till next pill take
def GetTimeToNextDrop():
    global SharedTimeToNextDrop
    return SharedTimeToNextDrop.value

#returns the missed time from the given index
def GetDispenseTiming(Index):
    global SharedMissedTimingStr, SharedMissedTimingIndex

    if (Index < 0): #Check if grabbing a valid index
        return "null"
    
    #Toggle request
    SharedMissedTimingIndex.value = Index

    #Pause until request is finished
    Attempts = 0 #Count to break out of pause when waiting for too long
    PrevTime = time.time() #Used to calc change in time
    while (SharedMissedTimingIndex.value != -1):
        Attempts += time.time() - PrevTime #Add delta time
        PrevTime = time.time()
        if (Attempts > 5): #After 5 seconds break
            return "Error-500"
            break
        continue

    #return value after request is finished    
    return SharedMissedTimingStr.value
    
#returns the total number of dispense times
def GetDispenseTimingCount():
    global SharedDispenseTimeCount
    return SharedDispenseTimeCount.value

#returns the dispense time from the given index
def GetDispenseTiming(Index):
    global SharedDispenseTimingGetStr, SharedDispenseTimingGetRequest

    if (Index < 0): #Check if grabbing a valid index
        return "null"
    
    #Toggle request
    SharedDispenseTimingGetRequest.value = True

    #Pause until request is finished
    Attempts = 0 #Count to break out of pause when waiting for too long
    PrevTime = time.time() #Used to calc change in time
    while (SharedDispenseTimingGetRequest.value == True):
        Attempts += time.time() - PrevTime #Add delta time
        PrevTime = time.time()
        if (Attempts > 5): #After 5 seconds break
            return "Error-500"
            break
        continue

    #return value after request is finished    
    return SharedDispenseTimingGetStr.value

def GetDispenseTimingRequestStatus():
    global SharedDispenseTimingGetRequest
    return SharedDispenseTimingGetRequest.value

def SetDispenseClock(Hour, Minute, Second, Millisecond, Day, Month, Year):
    global SharedDispenseTimeSetRequest
    SharedDispenseTimeSetRequest.value = True

    global SharedDispenseTimeSetHour, SharedDispenseTimeSetMinute, SharedDispenseTimeSetSecond, SharedDispenseTimeSetMillisecond
    global SharedDispenseTimeSetDay, SharedDispenseTimeSetMonth, SharedDispenseTimeSetYear

    SharedDispenseTimeSetHour.value = Hour
    SharedDispenseTimeSetMinute.value = Minute
    SharedDispenseTimeSetSecond.value = Second
    SharedDispenseTimeSetMillisecond.value = Millisecond
    
    SharedDispenseTimeSetDay.value = Day
    SharedDispenseTimeSetMonth.value = Month
    SharedDispenseTimeSetYear.value = Year

    #while(SharedDispenseTimeSetRequest.value == True):
    #    continue
    
    return "Success"

def GetDispenseClockSetRequestStatus():
    global SharedDispenseTimeSetRequest
    return SharedDispenseTimeSetRequest.value

def SetDispenseTiming(Index, Hour, Minute):
    global SharedDispenseTimingSetRequest, SharedDispenseTimingSetIndex, SharedDispenseTimingSetHour, SharedDispenseTimingSetMinute

    #Set timings
    SharedDispenseTimingSetIndex.value = Index
    SharedDispenseTimingSetHour.value = Hour
    SharedDispenseTimingSetMinute.value = Minute

    #Send a request
    SharedDispenseTimingSetRequest.value = True

    #while(SharedDispenseTimingSetRequest.value == True):
    #    continue
    
    return "Success"

def GetDispenseTimingRequestSetStatus():
    global SharedDispenseTimingSetRequest
    return SharedDispenseTimingSetRequest.value

def GetDispenseTiming(Index):
    global SharedDispenseTimingGetRequest, SharedDispenseTimingGetIndex, SharedDispenseTimingGetStr

    #Set timings
    SharedDispenseTimingGetIndex.value = Index

    #Send a request
    SharedDispenseTimingGetRequest.value = True

    while(SharedDispenseTimingGetRequest.value == True):
        continue
    
    return SharedDispenseTimingGetStr.value

def GetDispenseTimingRequestGetStatus():
    global SharedDispenseTimingGetRequest
    return SharedDispenseTimingGetRequest.value

def SetDispenseDel(Index, Count):
    global SharedDispenseTimingDelRequest, SharedDispenseTimingDelRangeIndex, SharedDispenseTimingDelRangeCount
    
    #Set ranges
    SharedDispenseTimingDelRangeIndex.value = Index
    SharedDispenseTimingDelRangeCount.value = Count

    #Send a request
    SharedDispenseTimingDelRequest.value = True

    #while(SharedDispenseTimingSetRequest.value == True):
    #    continue
    
    return "Success"

def GetDispenseTimingRequestStatusDel(Index, Count):
    global SharedDispenseTimingDelRequest
    return SharedDispenseTimingDelRequest.value

Terminate = Value('i', False)
    
def Start():
    RequestRun.start()

def Stop():
    Terminate.value = True
    PrevTime = time.time()
    Time = 0
    while (Terminate.value == True):
        print("RequestHandler: Awaiting Termination (" + str(Time) + ")")
        Time += time.time() - PrevTime
        PrevTime = time.time()
        if (Time >= 5):
            print("RequestHandler: Termination of GPIO Failed, terminating thread")
            break
        continue
    RequestRun.terminate()

RequestRun = Process(target = InitialiseSharedWrappers, args=(System, Mode, SharedDoDrop,  SharedDropped, SharedTimeToDrop, SharedTimeStringFormat, SharedTimeStringFormatted, SharedDispenseTime24, SharedDeltaUpdate, SharedTimeString, \
                                            SharedDispenseTimeCount, \
                                            SharedDispenseTimingSetIndex, SharedDispenseTimingSetHour, SharedDispenseTimingSetMinute, \
                                            SharedDispenseTimingGetRequest, SharedDispenseTimingGetIndex, SharedDispenseTimingGetStr, \
                                            SharedDispenseTimeSetHour, SharedDispenseTimeSetMinute, \
                                            SharedDispenseTimeSetSecond, SharedDispenseTimeSetMillisecond, SharedDispenseTimeSetDay, SharedDispenseTimeSetMonth, \
                                            SharedDispenseTimeSetYear, SharedDispenseTimeSetRequest, SharedDispenseTimingSetRequest, \
                                            SharedDispenseInitialisationStatus, \
                                            SharedDispenseTimingDelRequest, SharedDispenseTimingDelRangeIndex, SharedDispenseTimingDelRangeCount, \
                                            SharedDispenseUpdateTimingSetHour, SharedDispenseUpdateTimingSetMinute, SharedDispenseUpdateTimingSetSecond, SharedDispenseUpdateTimingSetDay, SharedDispenseUpdateTimingSetMonth, SharedDispenseUpdateTimingSetYear, \
                                            SharedDispenseUpdateTimingSetMode, SharedMissedTimingCount, SharedMissedTimingIndex, SharedMissedTimingStr, \
                                            SharedDispenseUpdateTimeStampSetHour, SharedDispenseUpdateTimeStampSetMinute, SharedDispenseUpdateTimeStampSetMode, SharedDispenseUpdateTimeStampSetIndex, SharedTimeNextDrop, \
                                            SharedTimeToNextDrop, PillData))
