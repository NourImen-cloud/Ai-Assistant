; Inno Setup Script for Echo Mind
; Creates a standalone Windows Installer: EchoMind-Setup.exe

#define MyAppName "Echo Mind"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Echo Mind"
#define MyAppExeName "EchoMind.exe"

[Setup]
AppId={{9F82A4D1-5C73-4E8A-B231-897EFA4B812C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\EchoMind
DisableProgramGroupPage=yes
; User-level install without requiring Administrator privileges (like Chrome & Discord)
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=EchoMind-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\EchoMind\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
