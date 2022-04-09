function InitialiseAlert()
{
	Alert("Your Pill Dispenser has not been set up yet", "Would you like to set it up now with default or custom settings ?",
			[
			new AlertButton("Default", "CloseAlert(); DefaultSettings();"),
			new AlertButton("Custom", "CloseAlert(); CustomSettings(); "),
			new AlertButton("None", "CloseAlert(); AddRequest(new SetInitialisedState(true)); ")
			]
	);
}

//Preset Functions
function DefaultSettings() //TODO:: make this simpler by adding a function in python to do all of this
{
    Requests = []; //clear requests
	SetTimeToSystem();
	AddRequest(new SetDispenseDel(2, -1, function() {
        AddRequest(new SetTiming(0, 9, 00, function(Status, Response) //Set standard timings
        {
            if (Status == DONE)
            {
                console.log("done");
                AddRequest(new SetTiming(1, 12, 00, function(Status, Response)
                {
                    if (Status == DONE)
                    {
                        AddRequest(new SetTiming(2, 18, 0, function(Status, Response)
                        {
                            if (Status == DONE)
                            {
                                console.log("All Timings set");
                            }
                        }));
                    }
                }));
            }
        }));
    }));
	AddRequest(new SetInitialisedState(true));
	AddRequest(new SetMultipleOfSegments(1)); //Set number of segments to 1
}

//Trigger custom settings call
var CustomTimeStamps = [];
var CurrValue = "00:00";
var custom_Exec =
{
    TimeStamps: [],
    execute: function()
    {
        if (this.TimeStamps.length > 0)
        {
            AddRequest(this.TimeStamps[0]);
            this.TimeStamps.splice(0, 1);
        }
    }
}
function CustomSettings()
{
	//Create a alert for setting custom settings
	Alert("Custom Settings:", 
		"\
		<div style='width:100%; height: auto;'> \
		Time: <span id='custom_Time' name='DispenserTime'>00:00:00</span> (SystemTime): <span name='SystemTime'>00:00:00</span> <BR>\
		<input id='custom_SystemTimeCheck' type='checkbox' value='SetSystemTime' checked>Set to system time ?</input> <BR><BR>\
        <div style='color:red' id='custom_Error'>\
        </div><BR>\
        <div style='display:flex;justify-content: center;align-items: center;' id='custom_TimeWrapper'> \
        <input type='time' class='UnStyledTime' id='custom_TimeSet' disabled/>\
        <BR>\
        <input type='date' class='UnStyledDate' id='custom_Date' disabled/>\
        </div>\
        <BR><BR>\
        Number of Segments: <BR>\
        <select id='custom_NumSegments'> \
            <option value='1'>21</option> \
            <option value='3'>7</option> \
        </select> \
        <BR><BR><BR>\
        <div style='color:red' id='custom_ErrorTimeStamp'>\
        </div><BR>\
        <div class='custom_TimeStamp' style='height:auto;' id='custom_AddTimeStamp'> \
        a\
        </div> \
        <div class='custom_TimeStamp' id='custom_TimeStamps'> \
        a\
        </div> \
		</div> \
		",
		[
		new AlertButton("Done", "Alert.Func[0]();"),
		new AlertButton("Cancel", "CloseAlert(); InitialiseAlert();"),
		],
		function()
		{
			var TimeSpan = document.getElementById("custom_Time");
            var TimeContainer = document.getElementById("custom_TimeWrapper");
			if (document.getElementById("custom_SystemTimeCheck").checked)
			{
				TimeSpan.setAttribute("name", 'SystemTime');
                document.getElementById("custom_TimeSet").disabled = true;
                document.getElementById("custom_Date").disabled = true;
			}
			else
			{
				TimeSpan.setAttribute("name", 'DispenserTime');
                document.getElementById("custom_TimeSet").disabled = false;
                document.getElementById("custom_Date").disabled = false;
			}
			
			//TODO:: add more shit here
            
            
		},
        function() //onload function
        {
            let Table = document.getElementById("custom_TimeStamps");
            let InnerHTML = "";
            InnerHTML += "<div class='custom_TimeStampRow'>";
            InnerHTML += "<div class='custom_TimeStampCell'>New Timestamp</div>"
            InnerHTML += "<div class='custom_TimeStampCell'><input type='time' class='UnStyledTime' id='custom_TimeSetNew' value='" + CurrValue + "'/></div>"
            InnerHTML += "<div class='custom_TimeStampCell'><button onclick=" + "'let ValidationTime = moment(document.getElementById(" + '"custom_TimeSetNew"' + ").value, " + '"HH:mm"' + "); if (ValidationTime.isValid()) {CustomTimeStamps.push(document.getElementById(" + '"custom_TimeSetNew"' + ").value); CurrValue = document.getElementById(" + '"custom_TimeSetNew"' + ").value; Alert.InitFunc();}'" + ">Add</button></div>";
            InnerHTML += "</div>";
            document.getElementById("custom_AddTimeStamp").innerHTML = InnerHTML;
            InnerHTML = "";
            for (var i = 0; i < CustomTimeStamps.length; i++)
            {
                InnerHTML += "<div class='custom_TimeStampRow'>";
                InnerHTML += "<div class='custom_TimeStampCell'>TimeStamp " + (i + 1) + ":</div>"
                let ValidationTime = moment(CustomTimeStamps[i], "HH:mm");
                if (ValidationTime.isValid())
                    InnerHTML += "<div class='custom_TimeStampCell'><input style='background-color:#FFFFFF' type='time' class='UnStyledTime' onchange='CustomTimeStamps[" + i + "] = this.value; let ValidationTime = moment(this.value, " + '"HH:mm"' + "); if (ValidationTime.isValid()) {this.style.backgroundColor=" + '"#FFFFFF"' + ";}else{this.style.backgroundColor=" + '"#FF0000"' + ";}' value='" + CustomTimeStamps[i] + "'/></div>"
                else
                    InnerHTML += "<div class='custom_TimeStampCell'><input style='background-color:#FF0000' type='time' onchange='CustomTimeStamps[" + i + "] = this.value; let ValidationTime = moment(this.value, " + '"HH:mm"' + "); if (ValidationTime.isValid()) {this.style.backgroundColor=" + '"#FFFFFF"' + ";}else{this.style.backgroundColor=" + '"#FF0000"' + ";}' class='UnStyledTime'/></div>"
                InnerHTML += "<div class='custom_TimeStampCell'><button onclick='" + "CustomTimeStamps.splice(" + i + ", 1); Alert.InitFunc();'" + ">Remove</button></div>";
                InnerHTML += "</div>";
            }
            Table.innerHTML = InnerHTML;
        },
		[
			function() //Set data
			{
                Requests = []; //clear requests
                
                let Time = document.getElementById("custom_TimeSet").value.split(":");
                let Date = document.getElementById("custom_Date").value.split("-"); 
                
                let ValidationTime = moment(document.getElementById("custom_TimeSet").value, "HH:mm");
                let ValidationDate = moment(document.getElementById("custom_Date").value, "YYYY-MM-DD");
                
                if ((!document.getElementById("custom_SystemTimeCheck").checked) && (Time.length != 2 || Date.length != 3 || ValidationDate.isValid() == false || ValidationTime.isValid() == false))
                {
                    document.getElementById('custom_Error').innerHTML = "The time or date given was invalid";
                    return;
                }
                
                Valid = true;
                for (var i = 0; i < CustomTimeStamps.length; i++)
                {
                    ValidationTime = moment(CustomTimeStamps[i], "HH:mm");
                    if (ValidationTime.isValid() == false)
                    {
                        Valid = false;
                        break;
                    }
                }
                if (Valid == true)
                {
                    let TimeStamps = [];
                    for (var i = 0; i < CustomTimeStamps.length; i++)
                    {
                        let Time = CustomTimeStamps[i].split(':');
                        TimeStamps.push(new SetTiming(i, Time[0], Time[1], function() {console.log("done"); custom_Exec.execute();}));
                    }
                    custom_Exec.TimeStamps = TimeStamps;
                    AddRequest(new SetDispenseDel(2, -1, function() {custom_Exec.execute();}));
                }
                else
                {
                    document.getElementById('custom_ErrorTimeStamp').innerHTML = "Highlighted timestamps are invalid";
                    return;
                }
                
                if (document.getElementById("custom_SystemTimeCheck").checked)
				{
					SetTimeToSystem();
				}
                else
                {
                    SetClockDef(Time[0], Time[1], Date[2], Date[1], Date[0]);
                }
                
                AddRequest(new SetMultipleOfSegments(document.getElementById("custom_NumSegments").value));
                
                CloseAlert(); AddRequest(new SetInitialisedState(true));
			}  
		]
	);
}

function SetTimeToSystem()
{
	let D = new Date();
	AddRequest(new SetClock(D.getHours(), D.getMinutes(), D.getSeconds() + 1, D.getMilliseconds(), D.getDate(), D.getMonth() + 1, D.getFullYear()));
}
function SetClockDef(Hour, Minute, Day, Month, Year)
{
	let D = new Date();
	AddRequest(new SetClock(Hour, Minute, D.getSeconds() + 1, D.getMilliseconds(), Day, Month, Year));
}