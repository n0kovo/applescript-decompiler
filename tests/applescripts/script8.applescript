-- Reference Script 3: Control Statements and Context Scopes
use AppleScript version "2.5"
use scripting additions

-- 1. If Statements (Simple and Compound)
if true then set simpleIf to "Executed"

if 5 > 10 then
    set compoundIf to false
else if 5 = 10 then
    set compoundIf to false
else
    set compoundIf to true
end if

-- 2. Repeat Loops (All Six Variations)
set loopCounter to 0

repeat
    if loopCounter > 20 then exit repeat
    set loopCounter to loopCounter + 1
end repeat

repeat 5 times
    set loopCounter to loopCounter + 1
end repeat

repeat while loopCounter > 0
    set loopCounter to loopCounter - 1
end repeat

repeat until loopCounter = 5
    set loopCounter to loopCounter + 1
end repeat

repeat with loopVar from 1 to 5
    set loopCounter to loopCounter + loopVar
end repeat

set listIter to {1, 2, 3}
repeat with listItem in listIter
    set loopCounter to loopCounter + listItem
end repeat

-- 3. Error Handling Block
try
    set errorTrigger to 1 / 0
on error errMsg number errNum
    log "Error: " & errMsg & " Code: " & errNum
end try

-- 4. Text and Response Consideration Blocks
considering text and diacriticals
    set considerTest to ("résumé" = "resume")
end considering

ignoring application responses
    tell application "Finder" to update desktop
end ignoring