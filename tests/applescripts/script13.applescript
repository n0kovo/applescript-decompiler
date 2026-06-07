-- 1. Global Constants & Properties
property defaultClientName : "Tester"
property savedDelimiters : AppleScript's text item delimiters

-- 2. Script Objects, Handlers, and run Handlers
on greetClient(nameOfClient)
    return "Hello " & nameOfClient & "!"
end greetClient

script TestNestedScript
    property nestedValue : 42
    on run
        return nestedValue
    end run
end script

-- 3. Variable Assignment and Coercion
set myInteger to 10
set myReal to 3.14159265359
set myText to "100" as integer
set myTextList to {"A", "B", "C"} as text
set myRecord to {name:"Test", value:1}
set myRecordList to myRecord as list
set myMissing to missing value

-- 4. Text Item Delimiters
set AppleScript's text item delimiters to {", "}
set joinedText to {"bread", "milk", "butter"} as text
set AppleScript's text item delimiters to savedDelimiters

-- 5. Control Statements & Considering
considering numeric strings
    if version of AppleScript ≥ "2.0" then
        set scriptStatus to "Modern"
    else
        set scriptStatus to "Legacy"
    end if
end considering

-- 6. Object Specifiers, References, and Containers
-- Targeting System Events is safer for testing than Finder
tell application "System Events"
    set myReference to a reference to first process
    
    -- Using 'it' and 'my' keywords
    set myName to name of it
    set myScriptProp to my defaultClientName
    
    -- Absolute vs Relative
    set systemVersion to version of application "System Events"
end tell

-- 7. Commands & Direct Parameters
-- 'get', 'set', 'count', 'copy', 'run'
set myCount to count of (get every process)
copy myCount to myCountCopy

-- 8. Error Handling
try
    error "Deliberate Error" number -999
on error errMessage number errNumber
    log "Caught expected error: " & errMessage & " (" & errNumber & ")"
end try

-- 9. Files and Aliases
-- Wrapping in try because /tmp/test.txt may not exist
try
    set myFile to POSIX file "/tmp/test.txt"
    -- set myAlias to alias "Hard_Disk:Users:test.txt" 
end try

-- 10. Debugging
beep 1
-- display dialog "Decompiler test running" giving up after 1
-- say "Testing complete"

-- 11. Current Application & Constants
set currentApp to current application
set isTrue to true
set isFalse to false

-- 12. Remote Applications (Commented out syntax for decompiler parsing)
(*
set remoteMachine to "eppc://username:password@192.168.1.1"
tell application "Finder" of machine remoteMachine
    get name of first window
end tell

using terms from application "Finder"
    tell application "Finder"
        -- remote commands
    end tell
end using terms from
*)

-- 13. Implicit and Explicit Handlers
run TestNestedScript
set greeting to greetClient(defaultClientName)

return {scriptStatus, myName, myCount, greeting}