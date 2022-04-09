var UpdateLoop = setInterval(function() {AutoLog(); Post(); Update(); if (Alert.UpdateFunc != null) {Alert.UpdateFunc();}}, 10);

//Variables grabbed from python script
var PillDispenserTime = "00:00:00";
var DispenseTimes = "00:00:00";
var DispenseTimeLength = 0;

function Initialise()
{
	Canvas = document.getElementById("Display");
	Ctx = Canvas.getContext("2d");
	Display = document.getElementById("Display");
	Container = document.getElementsByClassName("CanvasContainer")[0];
	Body = document.getElementById("Body");
	
	AlertWrapper = document.getElementsByClassName("AlertWrapper")[0];
	AlertContent = document.getElementsByClassName("AlertContent")[0];
	AlertTitle = document.getElementsByClassName("AlertTitle")[0];
	AlertButtons = document.getElementsByClassName("AlertButtons")[0];

	AddRequest(new GetInitialisedState(function(Status, Response)
	{
		if (Status == DONE)
		{
			if (Response == false)
			{
				InitialiseAlert(); //Call initialisation alert
			}
		}
	}));
    
    ResetTimeStamps();
}

function Update()
{var D = new Date();
	
	//Find all timers and set time
	let Timers = document.getElementsByName("DispenserTime");
	for (var i = 0; i < Timers.length; i++)
	{
		Timers[i].innerHTML = "Pill Dispenser Time: " + PillDispenserTime;
	}
	//Find all system time displays and set
	let SystemTimes = document.getElementsByName("SystemTime");
	for (var i = 0; i < SystemTimes.length; i++)
	{
		SystemTimes[i].innerHTML = "Device Time: " + moment(D).format('HH:mm:ss'); //HH 24hr, hh 12hr
	}
	
	UpdateCanvas();
    
    for (var i = 0; i < SetTimeRequestQueue.length; i++)
    {
        if (SetTimeRequestInit == true)
        {
            SetTimeRequestQueue[0].MakeRequest();
            SetTimeRequestInit = false;
        }
        else if (SetTimeRequestQueue[0] != WAITING)
        {
            SetTimeRequestQueue.splice(0, 1);
            SetTimeRequestInit = true;
        }
    }
    
    AddRequest(new GetPillData(function(Status, Response)
    {
        PillData = Response;
        let Count = 0
        for (var i = 0; i < 21; i++)
        {
            if (PillData[i] != "0")
            {
                Count++;
            }
        }
        document.getElementById("NumPills").innerHTML = Count;
        document.getElementById("RefillNum").max = 21 - Count;
    }));
}

function AddPills()
{
    document.getElementById("RefillNum").disabled = true;
    var Num = parseInt(document.getElementById("RefillNum").value);
    Count = -1
    let Sub = PillData.split("");
    for (var i = 0; i < 21; i++)
    {
		let Index = Rotation + i;
		while(Index >= 21)
		{
			Index -= 21;
		}
		while(Index < 0)
		{
			Index += 21;
		}
        if (Sub[Index] == "0" && Count < Num)
        {
            Sub[Index] = "1";
            Count++;
        }
        else if (Sub[Index] == "0")
        {
            Sub[Index] = "0";
        }
        else
        {
            Sub[Index] = "1";
        }
    }
    PillData = Sub.join("");
    AddRequest(new SetPillData(PillData, function(Status, Response){
        document.getElementById("RefillNum").disabled = false;
    }));
}

TimeStamps = [];
var TimeStamp_Exec =
{
    Calls: [],
    execute: function()
    {
        if (this.Calls.length > 0)
        {
            AddRequest(this.Calls[0]);
            this.Calls.splice(0, 1);
        }
    }
}
function GetTimeStamps()
{
    TimeStamps = []
    AddRequest(new RequestDispenseTimeCount(function(Status, Response) {
        TimeStamp_Exec.Calls = [];
        for (var i = 0; i < parseInt(Response); i++)
        {
            TimeStamp_Exec.Calls.push(new RequestDispenseTime(i, function(Status, Response) {
                TimeStamps.push(Response);
                let InnerHTML = "";                
                let i = (TimeStamps.length - 1);
                InnerHTML += "<div class='custom_TimeStampRow'>";
                InnerHTML += "<div class='custom_TimeStampCell'>TimeStamp " + (i + 1) + ":</div>"
                let ValidationTime = moment(Response, "HH:mm");
                if (ValidationTime.isValid())
                    InnerHTML += "<div class='custom_TimeStampCell'><input id='" + "TimeStampCell_" + i +"' type='time' class='UnStyledTime' onchange='this.style.backgroundColor = " + '"#00FF00";' + "TimeStamps[" + i + "]=this.value; UpdateSetTimeStamps(" + i + ");' value='" + Response + "'/></div>"
                else
                    InnerHTML += "<div class='custom_TimeStampCell'><input id='" + "TimeStampCell_" + i +"' type='time' class='UnStyledTime' onchange='this.style.backgroundColor = " + '"#00FF00";' + " TimeStamps[" + i + "]=this.value; UpdateSetTimeStamps(" + i + ");' style='background-color: #FF0000;' value='" + Response + "'/></div>"
                InnerHTML += "<div class='custom_TimeStampCell'><button onclick='" + "TimeStamps.splice(" + i + ", 1); UpdateRemoveTimeStamps(" + i + ");'" + ">Remove</button></div>";
                InnerHTML += "</div>";
                document.getElementById("TimeStamps").innerHTML += InnerHTML;
                TimeStamp_Exec.execute();
            }));
        }
        TimeStamp_Exec.execute();
    }));
}
function ResetTimeStamps()
{
    document.getElementById("TimeStamps").innerHTML = "";
    GetTimeStamps();
}
SetTimeRequestQueue = []; 
SetTimeRequestInit = true;
function UpdateSetTimeStamps(Index, Reset = false)
{
    let ValidationTime = moment(TimeStamps[Index], "HH:mm");
    if (ValidationTime.isValid())
    {
        TimeStamps[Index]
        let Time = TimeStamps[Index].split(':');
		if (Reset == true)
		{
			let S = new SetTiming(Index, Time[0], Time[1], function() {ResetTimeStamps();});
			SetTimeRequestQueue.push(S);
		}
		else
		{
			let S = new SetTiming(Index, Time[0], Time[1], function() {document.getElementById(("TimeStampCell_" + Index)).style.backgroundColor = "#FFFFFF";});
			SetTimeRequestQueue.push(S);
		}
    }
    else
    {
        document.getElementById("TimeStampCell_" + Index).style.backgroundColor = "#FF0000";
    }
}
function UpdateRemoveTimeStamps(Index)
{
    AddRequest(new SetDispenseDel(Index, Index + 1, function() {ResetTimeStamps();}));
}

//Updates necessary css onresize
var AlertWrapper = null;
var AlertContent = null;
var AlertTitle = null;
var AlertButtons = null;
var Body = null;
function UpdateCSS()
{
}

var Ctx = null;
var Canvas;
var Container;
var Display;
function UpdateCanvas()
{
	if (Ctx == null) return;
	Ctx.clearRect(0, 0, Canvas.width, Canvas.height);
	Ctx.fillStyle = "#FFFFFF";
	Ctx.fillRect(0, 0, Canvas.width, Canvas.height);
	
	DrawDispenser();
	UpdateTime();
}
var DeltaTime = 0;
var PrevTime = 0;
function UpdateTime()
{
	var d = new Date();
	DeltaTime = (d.getTime() - PrevTime) / 1000 * 2;
	PrevTime = d.getTime();
	if (DeltaTime > 0.2)
	{
		DeltaTime = 0;
	}
}

var PillData = "";
for (var i = 0; i < 21; i++)
{
	PillData += "0";
}

var Deg2Rad = Math.PI/180;
var Rotation = 0;
var PrevRotation = Rotation;
var RotInit = false;
function DrawDispenser()
{	
	Position = {x:400, y:400};

	Ctx.beginPath();
	Ctx.arc(Position.x, Position.y, 350, 0, 2 * Math.PI);
	Ctx.lineWidth = 14;
	Ctx.strokeStyle = "#AAD2FF";
	Ctx.stroke();
	
	Ctx.beginPath();
	Ctx.arc(Position.x, Position.y, 270, 0, 2 * Math.PI);
	Ctx.lineWidth = 14;
	Ctx.strokeStyle = "#AAD2FF";
	Ctx.stroke();
	
	//Draw Segments
	let NumberOfSegements = 21;
	let Rot = 360 / NumberOfSegements;
	Ctx.save();
	Ctx.translate(Position.x, Position.y);
	if (PrevRotation == Rotation)
	{
		Ctx.rotate((-Rotation * Rot) * Deg2Rad - Math.PI/2);
		for (var i = 0; i < NumberOfSegements; i++)
		{
			Ctx.beginPath();
			Ctx.moveTo(270, 0);
			Ctx.lineTo(350, 0);
			Ctx.lineWidth = 14;
			Ctx.strokeStyle = "#AAD2FF";
			Ctx.stroke();
			
			Ctx.rotate(Rot * Deg2Rad);
		}
	}
	else
	{
		Ctx.rotate((-PrevRotation * Rot) * Deg2Rad - Math.PI/2);
		for (var i = 0; i < NumberOfSegements; i++)
		{
			Ctx.beginPath();
			Ctx.moveTo(270, 0);
			Ctx.lineTo(350, 0);
			Ctx.lineWidth = 14;
			Ctx.strokeStyle = "#AAD2FF";
			Ctx.stroke();
			
			Ctx.rotate(Rot * Deg2Rad);
		}
		PrevRotation += 2 * DeltaTime;
		if (Rotation - PrevRotation < 0.1)
		{
			PrevRotation = Rotation;
		}
	}
	
    if (RotInit == true)
    {
        Sub = "";
        for (var i = 0; i < PillData.length; i++)
        {
            if (i == Rotation)
            {
                Sub += "0";
            }
            else
            {
                Sub += PillData[i];
            }
        }
        
        if (Sub != PillData)
        {
            PillData = Sub;
            AddRequest(new SetPillData(PillData, function(Status, Response){
                document.getElementById("RefillNum").disabled = false;
            }));
        }
    }
    
	//Draw pills
	for (var i = 0; i < NumberOfSegements; i++)
	{
		if (PillData[i] != "0")
		{
			Ctx.beginPath();
			Ctx.arc(0, 0, 350, (i + 10) * Rot * Deg2Rad, (i + 11) * Rot * Deg2Rad);
			Ctx.lineWidth = 10;
			Ctx.strokeStyle = "#FF11DD";
			Ctx.stroke();
			
			Ctx.beginPath();
			Ctx.arc(0, 0, 270, (i + 10) * Rot * Deg2Rad, (i + 11) * Rot * Deg2Rad);
			Ctx.lineWidth = 10;
			Ctx.strokeStyle = "#FF11DD";
			Ctx.stroke();
		}
	}
    
	Ctx.restore();
}