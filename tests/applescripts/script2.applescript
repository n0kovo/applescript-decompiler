-- 1. Use statement (requires AppleScript 2.3+; uncomment if needed)
-- use scripting additions
-- use framework "Foundation"

-- 2. Global and local variable declarations
global globalCounter
set globalCounter to 0

-- 3. Script object with properties and handlers
script ParentScript
    property parentName : "Parent"
    
    on beep numTimes
        display notification "Parent beep " & numTimes & " times."
    end beep
    
    on parentMethod()
        return "Called from parent."
    end parentMethod
end script

-- Child script inheriting from ParentScript
script ChildScript
    property parent : ParentScript
    property childName : "Child"
    
    -- Override beep to demonstrate 'continue'
    on beep numTimes
        set dialogResult to display dialog "Child beep? Choose Yes to continue to parent." buttons {"Yes", "No"}
        if button returned of dialogResult is "Yes" then
            continue beep numTimes -- Calls parent's beep handler
        else
            display notification "Child handled beep; not continuing."
        end if
    end beep
end script

-- 4. Handlers with positional parameters
on factorial(x)
    if class of x is not integer then error "Factorial requires integer." number 1001
    if x < 0 then return 0
    set result to 1
    repeat with i from 2 to x
        set result to result * i
    end repeat
    return result
end factorial

-- 5. Handler with labeled parameters (AppleScript label 'from')
on areaOfCircle from radius
    if class of radius is not in {real, integer} then error "Radius must be number." number 1002
    return radius * radius * pi
end areaOfCircle

-- 6. Handler with multiple AS labels and a direct parameter
on moveFile theFile from sourceFolder to destinationFolder by replacing
    -- Simulate moving a file; actual implementation omitted.
    display notification "Moving " & (theFile as string) & " from " & sourceFolder & " to " & destinationFolder & " with replacing: " & replacing
    return true
end moveFile

-- 7. Handler with user-defined labels (given)
on printInfo given name:userName, age:userAge, active:isActive
    set statusString to ""
    if isActive then
        set statusString to "active"
    else
        set statusString to "inactive"
    end if
    return "Name: " & userName & ", Age: " & userAge & ", Status: " & statusString
end printInfo

-- 8. Handler with interleaved parameters
-- Defined as: on moveTo:x by:y
on moveTo:x by:y
    return "Moving to (" & x & ", " & y & ")"
end moveTo:by:

-- 9. Folder Action Handlers (just definitions; not triggered)
on adding folder items to theFolder after receiving addedItems
    display notification "Items added to " & (theFolder as string)
end adding folder items to

on closing folder window for theFolder
    display notification "Window closed for " & (theFolder as string)
end closing folder window for

on moving folder window for theFolder from originalBounds
    -- originalBounds is {left, top, right, bottom}
    display notification "Window moved/resized from " & originalBounds
end moving folder window for

on opening folder theFolder
    display notification "Folder opened: " & (theFolder as string)
end opening folder

on removing folder items from theFolder after losing lostItems
    display notification "Items removed from " & (theFolder as string)
end removing folder items from

-- 10. Handler demonstrating return with/without value
on returnDemo(flag)
    if flag then
        return "Value returned"
    else
        return -- no value
    end if
end returnDemo

-- 11. Main script execution
try
    -- Using 'tell' to target a script object (ChildScript)
    tell ChildScript
        beep 3 -- Invokes overridden handler, may call parent via 'continue'
        log parentMethod() -- Accesses parent's handler
    end tell
    
    -- Call positional handler
    set fact5 to factorial(5) --> 120
    log "Factorial of 5: " & fact5
    
    -- Call labeled handler (AS label)
    set circleArea to areaOfCircle from 10.5
    log "Area of circle radius 10.5: " & circleArea
    
    -- Call handler with multiple AS labels and direct param
    moveFile "test.txt" from "Documents" to "Archive" by true
    
    -- Call handler with 'given' user labels
    set info to printInfo given name:"John", age:30, active:true
    log info
    
    -- Call interleaved handler
    set coordStr to moveTo:100 by:200
    log coordStr
    
    -- Demonstrate 'return' behavior
    log returnDemo(true) --> "Value returned"
    log returnDemo(false) --> (no value; log may show nothing)
    
    -- 12. Control statements
    
    -- if-then-else
    set x to 10
    if x > 5 then
        log "x is greater than 5"
    else if x = 5 then
        log "x equals 5"
    else
        log "x is less than 5"
    end if
    
    -- repeat forms
    set sum to 0
    repeat with i from 1 to 5
        set sum to sum + i
    end repeat
    log "Sum 1..5: " & sum
    
    set counter to 0
    repeat while counter < 3
        set counter to counter + 1
        log "While loop iteration " & counter
    end repeat
    
    set counter to 5
    repeat until counter = 0
        set counter to counter - 1
        log "Until loop, counter: " & counter
    end repeat
    
    repeat 3 times
        log "Repeating 3 times"
    end repeat
    
    -- exit repeat
    set i to 0
    repeat
        set i to i + 1
        if i = 2 then exit repeat
        log "Inside infinite repeat, i=" & i
    end repeat
    
    -- 13. tell statements (application and script object)
    tell application "Finder"
        set homePath to (path to home folder) as text
        log "Home folder: " & homePath
    end tell
    
    tell me to log "Tell me works"
    
    -- 14. considering / ignoring
    set str1 to "AppleScript"
    set str2 to "applescript"
    considering case
        if str1 = str2 then
            log "Case-sensitive: equal"
        else
            log "Case-sensitive: not equal"
        end if
    end considering
    
    ignoring case
        if str1 = str2 then
            log "Case-insensitive: equal"
        end if
    end ignoring
    
    -- 15. with timeout and with transaction
    with timeout of 10 seconds
        log "Performing operation with timeout"
    end timeout
    
    tell application "Finder"
        with transaction
            -- Simulate a transaction; in practice you'd make changes here
            log "Inside Finder transaction"
        end transaction
    end tell
    
    -- 16. Error handling (try blocks)
    try
        -- Deliberate error: division by zero
        set badResult to 5 / 0
    on error errMsg number errNum
        log "Caught error " & errNum & ": " & errMsg
    end try
    
    -- Catching specific error number (example from Appendix C)
    try
        open for access file "NonexistentFolder:File.txt" with write permission
    on error number -43 -- File not found
        log "File not found error caught."
    end try
    
    -- Using 'error' statement to raise custom error
    try
        error "Custom error message" number 12345
    on error msg number n
        log "Custom error " & n & ": " & msg
    end try
    
    -- 17. Using raw Apple event (chevron syntax)
    -- This calls 'display dialog' via event code.
    «event sysodlog» "Hello from raw event" given «class btns»:{"OK"}
    
    -- 18. Reference forms on a list
    set sampleList to {10, 20, 30, 40, 50}
    set firstItem to first item of sampleList
    set lastItem to last item of sampleList
    set someItem to some item of sampleList
    set itemsGreaterThan20 to every item of sampleList whose it > 20
    log "First: " & firstItem & ", Last: " & lastItem & ", Some: " & someItem
    log "Items >20: " & itemsGreaterThan20
    
    -- 19. Load script library (requires NumberLib.scpt in same directory)
    try
        set libPath to (path to me as text) & "::NumberLib.scpt"
        set numberLib to load script file libPath
        tell numberLib
            log "Factorial via library: " & factorial(6)
            log "Circle area via library: " & areaOfCircle from 7
        end tell
    on error
        log "Library not found; load script test skipped."
    end try
    
    -- 20. Copy command vs set
    set listA to {1, 2, 3}
    copy listA to listB
    set end of listB to 4
    log "listA: " & listA & ", listB: " & listB -- Both modified? copy does deep copy of list? Actually copy makes a new list.
    
    -- 21. Use of 'it', 'me', 'my', 'its'
    set myVar to "global scope"
    script TestMe
        property scriptVar : "script scope"
        on test()
            log "scriptVar: " & scriptVar
            log "myVar: " & my myVar
        end test
    end script
    tell TestMe to test()
    
    -- 22. Date and time operations
    set currentDate to current date
    set tomorrow to currentDate + 1 * days
    log "Tomorrow: " & tomorrow
    
    -- 23. Using 'whose' filter on Finder items (if Finder is running)
    tell application "Finder"
        set docs to every item of desktop whose name ends with ".txt"
        log "Text files on desktop: " & (count of docs)
    end tell
    
    -- 24. Demonstration of 'continue' in a handler with parent chain
    -- We'll define a handler in a nested script and use continue
    script Level1
        on testContinue()
            return "Level1 result"
        end testContinue
    end script
    
    script Level2
        property parent : Level1
        on testContinue()
            continue testContinue() -- Calls Level1's handler
            return "Level2 additional"
        end testContinue
    end script
    
    tell Level2
        log testContinue() -- Should log "Level1 result" then "Level2 additional" after continue
        -- Actually continue returns control after parent executes; the return after continue will execute.
        -- So output will be "Level1 result" followed by "Level2 additional".
    end tell
    
    -- 25. Accessing properties and using 'prop' abbreviation
    script PropDemo
        property theCount : 10
        on increment()
            set theCount to theCount + 1
            return theCount
        end increment
    end script
    tell PropDemo
        log "Initial count: " & its theCount
        increment()
        log "After increment: " & its theCount
    end tell
    
    log "All tests completed."
    
on error errMsg number errNum
    display dialog "Unhandled error: " & errMsg & " (" & errNum & ")"
end try