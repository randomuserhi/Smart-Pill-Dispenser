//var AutoLoop = setInterval(function() {AutoLog(); Post();}, 200); //Automatic requests

var Connected = true;

function AutoLog() //Generates automatic requests
{
	AddRequest(new RequestTime(function(Status, Response) 
	{
		if (Status == DONE) 
		{
			PillDispenserTime = Response;
		}
	}));
	AddRequest(new GetRotationNum(function(Status, Response)
	{
		if (Status == DONE)
		{
			Rotation = parseInt(Response);
            RotInit = true;
		}
	}));
    AddRequest(new GetTimeToNextDrop(function(Status, Response)
    {
        let Count = 0
        for (var i = 0; i < 21; i++)
        {
            if (PillData[i] != "0")
            {
                Count++;
            }
        }
        if (Count == 0)
        {
            document.getElementById("TimeToNext").innerHTML = "PillDispenser needs to be refilled!";
        }
        else if (Count < 3)
        {
            document.getElementById("TimeToNext").innerHTML = "PillDispneser needs to be refilled soon!<BR>" + Response + " till next dose!";
        }
        else
        {
            document.getElementById("TimeToNext").innerHTML = Response + "!";
        }
    }));
}

var ping = null;
var ConnectionInit = false;
function Post() //Handles all the requests
{
    if (!Connected)
    {
        Requests = []; //Clear requests
        ConnectionInit = false;
        if (ping == null)
        {
            ping = new Ping();
            ping.MakeRequest();
        }
        else if (ping.Status != WAITING)
        {
            ping = new Ping();
            ping.MakeRequest();
        }
        Alert("Connection to Pill Dispenser has been lost", "Please check your internet connection", [])
        return;
    }
    if (Connected == true && ConnectionInit == false)
    {
        ConnectionInit = true;
        CloseAlert();
        Initialise();
    }

	for (var i = 0; i < Requests.length; i++) //Loop through all requests
	{
		let R = Requests[i];
		
		if (R.Sent) //Check if request wasnt already sent
			continue;
			
		R.MakeRequest();
	}
	
	Requests = Requests.filter(function(R) {return R.Status == WAITING}); //Filter out all requests which are complete (not waiting)
}