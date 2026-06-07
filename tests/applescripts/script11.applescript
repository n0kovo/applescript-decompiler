-- 1. LIBRARY USAGE
-- Tests: Referencing a library script (even if it doesn't exist, the syntax is valid)
try
    tell script "My Library" to log "Library invoked"
end try

-- 2. SCRIPT OBJECT DEFINITION & INHERITANCE
script ParentObject
    property ParentProp : "I am the parent"
    
    on identify()
        return "Parent"
    end identify
    
    on run
        log "Parent run handler"
    end run
end script

script ChildObject
    property parent : ParentObject
    property ChildProp : "I am the child"
    
    -- Overriding and Delegation
    on identify()
        -- Delegation via continue
        return "Child inheriting from " & continue identify()
    end identify
end script

-- 3. INITIALIZING AND USING SCRIPT OBJECTS
set myChild to ChildObject
tell myChild
    set ChildProp to "Updated Child"
    get ParentProp -- Accessing inherited property
end tell

-- 4. HANDLERS: POSITIONAL & PARAMETER SPECS
on simplePositional(x, y)
    return x + y
end simplePositional

-- Tests: Classes, default values, and parameter specifications
on advancedSpecs(val1 as integer, val2 as list : {1, 2, 3})
    return val1 + (item 1 of val2)
end advancedSpecs

-- 5. HANDLERS: LABELED PARAMETERS
-- Tests: 'given', 'with', 'without', direct parameters
on labeledHandler of directParam given rounding:roundBool, verbose:verboseMode
    if roundBool then return round directParam
    return directParam
end labeledHandler

-- 6. HANDLERS: PATTERNED POSITIONAL PARAMETERS
-- Tests: Record matching and list decomposition
on patternHandler({x, y}, {name:n, age:a})
    return n & " is " & a & " at " & x
end patternHandler

-- 7. HANDLERS: INTERLEAVED PARAMETERS
-- Tests: Objective-C style method names
on areaOfRectangleWithWidth:w height:h
    return w * h
end areaOfRectangleWithWidth:height:

-- 8. RECURSION & ERROR HANDLING
on factorial(n)
    try
        if n < 0 then error "Negative number"
        if n is 0 then return 1
        return n * factorial(n - 1)
    on error msg
        log "Error: " & msg
        return 0
    end try
end factorial

-- 9. PASSING BY REFERENCE
-- Tests: 'reference' object
set myData to {1, 2, 3}
on modifyData(dataRef)
    set end of contents of dataRef to 4
end modifyData

modifyData(a reference to myData)

-- 10. SPECIAL APPLICATION HANDLERS
-- (These will execute if the script is run as an applet/stay-open application)

on run
    -- Explicit Run handler
    log "Main script run"
    
    -- Demonstrate calling local handler from tell block
    tell application "Finder"
        my simplePositional(1, 2) of me
    end tell
end run

on open dropList
    -- Open handler for file droppings
    repeat with itemRef in dropList
        log (itemRef as text)
    end repeat
end open

on idle
    -- Idle handler logic
    beep
    return 60 -- Return frequency
end idle

on quit
    -- Quit handler
    display dialog "Quitting?"
    continue quit
end quit

-- 11. EXECUTING TESTS
set res1 to simplePositional(10, 20)
set res2 to advancedSpecs(5)
set res3 to labeledHandler of 10.5 given rounding:true, verbose:false
set res4 to patternHandler({10, 20}, {name:"Test", age:30})
set res5 to areaOfRectangleWithWidth:5 height:10
set res6 to factorial(5)

log {res1, res2, res3, res4, res5, res6, myData}