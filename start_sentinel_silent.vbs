Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
strPython = "C:\Users\andhi\AppData\Local\Programs\Python\Python313\python.exe"

If Not fso.FileExists(strPython) Then
    strPython = "python.exe"
End If

WshShell.CurrentDirectory = strScriptDir
WshShell.Run Chr(34) & strPython & Chr(34) & " main.py --server", 0, False
