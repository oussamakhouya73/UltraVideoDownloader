; Inno Setup script. Build: iscc /DAppVersion=1.2.0 installer\UltraVideoDownloader.iss
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif
#define AppName "UltraVideoDownloader"
#define AppExe "UltraVideoDownloader.exe"

[Setup]
AppId={{7B4E2C1A-9D3F-4A66-8E15-2F0C5B7A9D41}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppName}
; Per-user install: no administrator rights needed
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#AppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
OutputDir=..\installer-out
OutputBaseFilename=UltraVideoDownloader-Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\UltraVideoDownloader\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
; Also runs after a silent (auto-update) install, so the app reopens by itself.
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall
