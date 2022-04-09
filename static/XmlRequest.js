var Requests = []; //List of ongoing requests

function AddRequest()
{
	for (var i = 0; i < arguments.length; i++)
	{
		let Request = arguments[i]; //Grab request object
		
		//Check if a request of the same type is not already still ongoing within the queue
		if (Requests.some(function(R) {return (R.constructor == Request.constructor && R.Status == WAITING)}))
			continue;
			
		//If not then push this request
		Requests.push(Request);
	}
}

//Request status constants
var INTERNALSERVERERROR = 1;
var DONE = 2;
var WAITING = 0;

function Ping(ResponseFunction = null) //Checks if server is online
{
	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                Connected = true;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
        xmlhttp.send("Type=Ping&Args="); //Send request for timing  
    }
}
function GetInitialisedState(ResponseFunction = null) //Gets Initialisation state
{
	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetInitialisedState&Args="); //Send request for timing  
	}
}
function SetInitialisedState(State, ResponseFunction = null) //Gets Initialisation state
{
	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.State = State;
	
	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetInitialisedState&Args=" + (this.State ? 1 : 0)); //Send request for Initialising state  
	}
}
function InitialiseDispenser(ResponseFunction = null) //Sets the initialisation
{
	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=Initialise&Args="); //Send request for timing  
	}
}
function SetClock(Hour, Minute, Second, Millisecond, Day, Month, Year, ResponseFunction = null) //Sets the time
{
	this.Hour = Hour;
	this.Minute = Minute;
	this.Second = Second;
	this.Millisecond = Millisecond;
	this.Day = Day;
	this.Month = Month;
	this.Year = Year;
	
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;
	
	this.ResponseFunc = ResponseFunction
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetDispenseClock&Args=" + this.Hour + "," + this.Minute + "," + this.Second + "," + this.Millisecond + "," + this.Day + "," + this.Month + "," + this.Year); //Send request for time  
	}
}
function SetDispenseDel(Index, LastIndex, ResponseFunction = null) //returns the DispenseTime at index
{
	this.Index = Index;
	this.LastIndex = LastIndex;

	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetDispenseDel&Args=" + this.Index + "," + this.LastIndex); //Send request for time
	}
}
function SetTiming(Index, Hour, Minute, ResponseFunction = null) //Sets the time
{
	this.Index = Index;
	this.Hour = Hour;
	this.Minute = Minute;

	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetDispenseTiming&Args=" + this.Index + "," + this.Hour + "," + this.Minute); //Send request for timing  
	}
}
function RequestTime (ResponseFunction = null) //returns the time
{
	this.Sent = false;
	this.Status = WAITING;
	this.Response = null;
	
	this.ResponseFunc = ResponseFunction;

	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set request object to this request
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetTimeStr&Args="); //Send request for time  
	}
}
function RequestDispenseTimeCount(ResponseFunction = null) //returns the DispenseTime total
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;
	
	this.ResponseFunc = ResponseFunction;

	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = parseInt(xmlhttp.responseText);
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetDispenseTimingCount&Args="); //Send request for time
	}
}
function RequestDispenseTime(Index, ResponseFunction = null) //returns the DispenseTime at index
{
	this.Index = Index;

	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		if (Index < 0)
			return;
	
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetDispenseTimingStr&Args=" + this.Index); //Send request for time
	}
}
function GetTimeToNextDrop(ResponseFunction = null) //returns the DispenseTime at index
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetTimeToNextDrop&Args="); //Send request for time
	}
}
function RequestMissedTimeCount(ResponseFunction = null) //returns the DispenseTime total
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;
	
	this.ResponseFunc = ResponseFunction;

	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = parseInt(xmlhttp.responseText);
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetMissedTimingCount&Args="); //Send request for time
	}
}
function RequestMissedTime(Index, ResponseFunction = null) //returns the DispenseTime at index
{
	this.Index = Index;

	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		if (Index < 0)
			return;
	
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetMissedTimingStr&Args=" + this.Index); //Send request for time
	}
}
function GetMultipleOfSegments(ResponseFunction = null) //returns the DispenseTime at index
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		if (Index < 0)
			return;
	
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetMultipleOfSegments&Args="); //Send request for time
	}
}
function SetMultipleOfSegments(Multiple, ResponseFunction = null) //returns the DispenseTime at index
{
	this.Multiple = Multiple;

	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
                
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetMultipleOfSegments&Args=" + this.Multiple); //Send request for time
	}
}
function GetRotationNum(ResponseFunction = null) //returns the DispenseTime at index
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;

                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetRotationNum&Args="); //Send request for time
	}
}
function GetPillData(ResponseFunction = null) //returns the DispenseTime at index
{
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;

                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=GetPillData&Args="); //Send request for time
	}
}
function SetPillData(PillData, ResponseFunction = null) //returns the DispenseTime at index
{
    this.PillData = PillData;
	this.Sent = false;
	this.Response = null;
	this.Status = WAITING;

	this.ResponseFunc = ResponseFunction;
	
	this.MakeRequest = function()
	{
		this.Sent = true;
		var xmlhttp = new XMLHttpRequest();
		xmlhttp.Request = this; //Set Request object to this
		xmlhttp.ResponseFunc = this.ResponseFunc;
		xmlhttp.onreadystatechange=function() //Create request details
		{
			if (xmlhttp.readyState==4 && xmlhttp.status==200) //On successful request
			{
				this.Request.Response = xmlhttp.responseText;
				this.Request.Status = DONE;

                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
			}
			else if (xmlhttp.readyState==4 && xmlhttp.status==500)
			{
				this.Request.Status = INTERNALSERVERERROR;
			
                if (this.Request.ResponseFunc != null)
                {
                    this.ResponseFunc(this.Request.Status, this.Request.Response);
                }
            }
		}
        xmlhttp.onerror = function()
        {
            Connected = false;
            this.Request.Status = INTERNALSERVERERROR;
        }
		xmlhttp.open("POST","/",true); //open post request
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded"); //Set request
		xmlhttp.send("Type=SetPillData&Args=" + this.PillData); //Send request for time
	}
}