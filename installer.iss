[Setup]
AppName=Media Downloader
AppVersion=1.0
DefaultDirName={autopf}\Media Downloader
DefaultGroupName=Media Downloader
OutputDir=.\installer
OutputBaseFilename=MediaDownloader_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableWelcomePage=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\Media Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Media Downloader"; Filename: "{app}\Media Downloader.exe"
Name: "{autodesktop}\Media Downloader"; Filename: "{app}\Media Downloader.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
