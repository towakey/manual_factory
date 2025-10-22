Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\Manual Factory.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\xampp\htdocs\manual_factory\start.bat"
oLink.WorkingDirectory = "C:\xampp\htdocs\manual_factory"
oLink.Description = "Manual Factory - Portable Web Server"
oLink.Save

MsgBox "デスクトップにショートカットを作成しました", vbInformation, "完了"
