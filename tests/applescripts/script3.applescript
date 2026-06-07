-- Reference Script 8: System Native Commands, I/O, and OSAX
use AppleScript version "2.5"
use scripting additions

-- 1. Environment and System Attributes
set sysAttr to system attribute "sys1"
set sysInfo to system info
set sysSettings to get volume settings
set curDate to current date
set gmtTime to time to GMT
set randNum to random number from 1 to 10
set roundedNum to round 5.6
set mountedDisks to list disks
set desktopFolder to path to (desktop folder)
set scriptApp to path to application "Finder"
set rsrcPath to path to resource "Scripts"

-- 2. File I/O Operations
set targetFile to (path to desktop as text) & "AS_Decompiler_Test.txt"
set eofData to 0

try
    set fileRef to open for access file targetFile with write permission
    set eof fileRef to 0
    write "Exhaustive Decompilation Test Data" to fileRef
    set eofData to get eof fileRef
    close access fileRef
on error
    try
        close access file targetFile
    end try
end try

try
    set fileRef to open for access file targetFile
    set readData to read fileRef
    close access fileRef
end try

-- 3. Clipboard and AppleScript Management
set the clipboard to "Coverage Matrix"
set clipData to the clipboard
set clipInfo to clipboard info

set tempScript to "display dialog \"Hello\""
store script tempScript in file ((path to desktop as text) & "temp.scpt")
set loadedScript to load script file ((path to desktop as text) & "temp.scpt")
run script loadedScript
set osaComponents to scripting components

-- 4. User Interaction and Dialogs
beep 1
delay 1
say "Decompilation matrix active"

display notification "Matrix Loaded" with title "System Check"
display dialog "Proceed?" buttons {"No", "Yes"} default button 2
display alert "System Alert" message "Testing coverage."

set chosenFile to choose file with prompt "Select a file:"
set chosenFolder to choose folder with prompt "Select a folder:"
set chosenName to choose file name with prompt "Save as:"
set chosenColor to choose color default color {65535, 65535, 65535}
set chosenList to choose from list {"A", "B", "C"} with prompt "Select:"
set chosenApp to choose application with prompt "Pick App:"
set chosenURL to choose URL showing File servers
set chosenRemote to choose remote application title "Select Remote App"

-- 5. Command Operations and Legacy Strings
set folderList to list folder (path to desktop folder)
mount volume "smb://guest@localhost/Public"
open location "https://www.apple.com"
do shell script "echo 'System Validated'"
set volume output volume 50

-- 6. Deprecated and Legacy Functions
set ascChar to ASCII character 65
set ascNum to ASCII number "A"
set locString to localized string "Cancel"
set strOffset to offset of "A" in "MAC"
set strSummary to summarize "This is a long string of text meant for summarizing."
set varCopy to copy "Data" to copyDest
set varCount to count of "Characters"

-- 7. Process Commands
tell application "Finder"
    launch
    activate
    get name of front window
    set collapsed of front window to true
end tell