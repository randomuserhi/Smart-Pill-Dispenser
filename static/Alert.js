function Alert (Title, Content, Buttons, UpdateFunc = null, InitFunc = null, Func = [])
{
	document.getElementById("AlertBox").style.display = "flex";
	document.getElementById("AlertTitle").innerHTML = Title;
	document.getElementById("AlertContent").innerHTML = Content;
	ButtonStr = "";
	for (var i = 0; i < Buttons.length; i++)
	{
		ButtonStr += Buttons[i].InnerHTML;
	}
	document.getElementById("AlertButtons").innerHTML = ButtonStr;
	
	Alert.UpdateFunc = UpdateFunc; //function called during alert
    Alert.InitFunc = InitFunc;
    if (Alert.InitFunc != null)
    {
        Alert.InitFunc();
    }
	Alert.Func = Func; //Extra functions for other functionality
}
Alert.UpdateFunc = null;
Alert.Func = [];
Alert.InitFunc = null;

function CloseAlert()
{
	Alert.UpdateFunc = null;
    Alert.InitFunc = null;
	Alert.Func = [];
	document.getElementById("AlertBox").style.display = "none";
}

function AlertButton(Text, Function)
{
	this.InnerHTML = "<button class='AlertButton' onclick='" + Function + "'>" + Text +"</Button>";
}