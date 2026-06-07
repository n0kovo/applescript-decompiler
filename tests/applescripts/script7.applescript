-- Reference Script 4: Transactions, Timeouts, and Application Targets
use AppleScript version "2.5"

-- 1. Simple and Compound Tell Blocks
tell application "Finder" to set simpleTell to name of startup disk

tell application "System Events"
    set compoundTell to name of current user
end tell

-- 2. Timeout Modifier
with timeout of 10 seconds
    set timeoutVar to "Timeout Block Executed"
end timeout

-- 3. Database Transaction Block
tell application "Database Events"
    launch
    with transaction
        set newRecord to make new database with properties {name:"TestDB"}
    end transaction
    quit
end tell