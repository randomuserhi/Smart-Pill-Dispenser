# Import external functions
import web
from web import form

#import Pill program
import PillDispenser

import time
    
#Define the pages (index) for the site
urls = ('/', 'index')
        
render = web.template.render('templates')
app = web.application(urls, globals())

#Error handling
import traceback

#TryParse method
def TryParse(String, DefaultVal=None):
    try:
        return int(String)
    except ValueError:
        print "TryParse failed"
        traceback.print_exc()
        return DefaultVal

#Define what happens when the index page is called
class index:

    #Set get values at initialisation of page
    def GET(self):
        return render.index()

    #Post values as in values recieved from page
    def POST(self):
        Request = web.input() #Get the request
        
        #Check what the request is for and act accordingly
        try:
            if (Request.Type == "Ping"): #Presence check
                return "404"
            elif (Request.Type == "GetPillData"): #Get pill data
                return PillDispenser.RequestHandler.GetPillData()
            elif (Request.Type == "SetPillData"): #Set pill data
                return PillDispenser.RequestHandler.SetPillData(Request.Args)
            elif (Request.Type == "Initialise"): #Initialise / start dispenser main program
                return PillDispenser.RequestHandler.SharedInitialisation()
            elif (Request.Type == "GetInitialisedState"):
                return PillDispenser.RequestHandler.GetInitialisationState();
            elif (Request.Type == "SetInitialisedState"):
                return PillDispenser.RequestHandler.SetInitialisationState(TryParse(Request.Args, False));
            elif (Request.Type == "GetMultipleOfSegments"):
                return PillDispenser.GetMultipleOfSegments()
            elif (Request.Type == "GetRotationNum"):
                return PillDispenser.GetRotationNum();
            elif (Request.Type == "SetMultipleOfSegments"):
                return PillDispenser.SetMultipleOfSegments(TryParse(Request.Args, 2))
            elif (Request.Type == "GetTimeStr"): #Requesting current time
                return PillDispenser.RequestHandler.GetTime()
            elif (Request.Type == "GetMissedTimingCount"):
                return PillDispenser.RequestHandler.GetMissedTimingCount()
            elif (Request.Type == "GetMissedTimingStr"):
                Index = TryParse(Request.Args)
                if (Index == None):
                    return "Invalid Args"
                return PillDispenser.RequestHandler.GetMissedTiming(Index)
            elif (Request.Type == "GetTimeToNextDrop"):
                return PillDispenser.RequestHandler.GetTimeToNextDrop()
            elif (Request.Type == "GetDispenseTimingCount"):
                return PillDispenser.RequestHandler.GetDispenseTimingCount()
            elif (Request.Type == "GetDispenseTimingStr"):
                Index = TryParse(Request.Args)
                if (Index == None):
                    return "Invalid Args"
                return PillDispenser.RequestHandler.GetDispenseTiming(Index)
            elif (Request.Type == "SetDispenseClock"):
                DataStream = Request.Args.split(",")
                
                if (len(DataStream) != 7):
                    return "Invalid Args"
                
                Hour = TryParse(DataStream[0])
                Minute = TryParse(DataStream[1])
                Second = TryParse(DataStream[2])
                Millisecond = TryParse(DataStream[3])
                Day = TryParse(DataStream[4])
                Month = TryParse(DataStream[5])
                Year = TryParse(DataStream[6])
                
                if (Hour == None or Minute == None or Second == None or Millisecond == None or Day == None or Month == None or Year == None):
                    return "A Parsing error occured"

                return PillDispenser.RequestHandler.SetDispenseClock(Hour, Minute, Second, Millisecond, Day, Month, Year)
            elif (Request.Type == "SetDispenseTiming"):
                DataStream = Request.Args.split(",")

                if (len(DataStream) != 3):
                    return "Invalid Args"
                
                Index = TryParse(DataStream[0])
                Hour = TryParse(DataStream[1])
                Minute = TryParse(DataStream[2])

                if (Hour == None or Minute == None or Index == None):
                    return "A Parsing error occured"
                return PillDispenser.RequestHandler.SetDispenseTiming(Index, Hour, Minute)
            elif (Request.Type == "SetDispenseDel"):
                DataStream = Request.Args.split(",")

                if (len(DataStream) != 2):
                    return "Invalid Args"
                
                Index = TryParse(DataStream[0])
                Count = TryParse(DataStream[1])

                if (Index == None or Count == None):
                    return "A Parsing error occured"
                return PillDispenser.RequestHandler.SetDispenseDel(Index, Count)
            #No request was given
            else:
                print("Home page POST error - Not returning anything")
                return "Home page error"
        
        except:
                traceback.print_exc()
                return "An unexpected error occured"
        

            
# ------------------------run the main program------------------------
if (__name__ == '__main__'):

    print("Waiting incase of SSH")
    time.sleep(10)
    print("Wait finished")

    #Run PillDispenser
    PillDispenser.DispenserStart()
    #Run Webapp
    app.run()
    #Stop PillDispenser
    PillDispenser.DispenserStop()
	
    print("The end")
