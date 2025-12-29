Dim WshShell
Set WshShell = WScript.CreateObject("WScript.Shell")
WshShell.Run "D:\ThisComputer\Documents\Arduino\sisyphusValorantTracker\scrapMatchData.py", 0, False
WshShell.Run "D:\Softwares\ngrok\ngrok.exe http 5000", 0, False
Set WshShell = Nothing