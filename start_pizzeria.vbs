Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\abdul\Cursor projects\pizzeria-management-system"
WshShell.Run "pythonw app.py", 0, False
Set WshShell = Nothing


