Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FinancasAutoStart.lnk")
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\Users\PEDRO\Documents\ACOMPANHAMENTO_FINANCEIRO\AUTO_START_FINANCAS.bat"
oLink.WorkingDirectory = "C:\Users\PEDRO\Documents\ACOMPANHAMENTO_FINANCEIRO"
oLink.WindowStyle = 7 ' Minimized
oLink.Save
