[Setup]
AppId={{88fc68fb-965d-4dce-a0a8-b1eeb65fb47a}}
AppName=Whisper Cheap
AppVersion=1.0.1
AppPublisher=Whisper Cheap
DefaultDirName={autopf}\Whisper Cheap
DefaultGroupName=Whisper Cheap
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=WhisperCheapSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\src\resources\icons\app.ico
UninstallDisplayIcon={app}\WhisperCheap.exe

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; Flags: unchecked

[Files]
Source: "..\dist\WhisperCheap\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Whisper Cheap"; Filename: "{app}\WhisperCheap.exe"
Name: "{autodesktop}\Whisper Cheap"; Filename: "{app}\WhisperCheap.exe"; Tasks: desktopicon

[Registry]
; Clean up any existing autostart entry (removes dev python.exe entries)
; User can re-enable autostart from app settings after installation
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "WhisperCheap"; Flags: deletevalue uninsdeletevalue

[Run]
Filename: "{app}\WhisperCheap.exe"; Description: "Launch Whisper Cheap"; Flags: nowait postinstall skipifsilent
