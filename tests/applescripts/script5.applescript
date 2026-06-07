-- Reference Script 6: Handler Paradigms and Subroutine Passing
use AppleScript version "2.4"

-- 1. Event Responders / Application Lifecycle
on run
    log "Execution initiated"
end run

on open droppedItems
    log "Handling dropped files"
end open

on idle
    return 10 
end idle

on quit
    continue quit
end quit

-- 2. Positional and Simple Handlers
on simpleHandler()
    return "Executed"
end simpleHandler

on positionalHandler(x, y)
    return x * y
end positionalHandler

-- 3. Labeled Handlers
on labeledHandler given stringValue:str, numericValue:num
    return str & (num as text)
end labeledHandler

-- 4. Patterned Positional Handlers
on patternedHandler({x, y, z})
    return x + y + z
end patternedHandler

-- 5. Interleaved Handlers (Objective-C Bridging Style)
on calculateAreaOfWidth:w andHeight:h
    return w * h
end calculateAreaOfWidth:andHeight:

-- 6. Recursive Handler
on calculateFactorial(n)
    if n ≤ 1 then return 1
    return n * calculateFactorial(n - 1)
end calculateFactorial

-- 7. Passing by Reference Mutability
on modifyByReference(listRef)
    set item 1 of listRef to 99
end modifyByReference

-- 8. Scope Resolution Execution
set dummyList to {1, 2, 3}
modifyByReference(a reference to dummyList)

set resultPositional to positionalHandler(5, 10)
set resultLabeled to labeledHandler given stringValue:"Total: ", numericValue:50
set resultPatterned to patternedHandler({10, 20, 30})
set resultInterleaved to calculateAreaOfWidth:5 andHeight:10
set resultRecursive to calculateFactorial(5)
set resultScope to my simpleHandler()
set resultMe to simpleHandler() of me