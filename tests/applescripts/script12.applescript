-- =============================================================================
-- 04-VARIABLES-AND-PROPERTIES.MD COVERAGE TEST
-- =============================================================================

-- 1. Defining Properties
property windowCount : 0
property defaultName : "Barry"
property strangeValue : (pi * 7) ^ 2

-- 2. Global Declarations
global gAgentCount
global gStatementDate, gNextAgentNumber

-- 3. Basic Variable Assignment
set circumference to pi * 3.5
copy circumference to savedResult

-- 4. Local Declarations
local windowCount_local -- single
local agentName, agentNumber, agentHireDate -- multiple

-- 5. Using set and copy
-- Immutable (text)
set myName to "Sheila"
set yourName to myName -- yourName refers to myName, but immutable

-- Mutable (list)
set myList to {1, 2, 3}
set yourList to myList -- References the same list (set)
copy myList to copiedList -- Creates a deep copy

-- Object references
set windowRef to a reference to window 1 of application "Finder"
copy windowRef to currentWindowRef

-- 6. Set Patterns
set x to {8, 94133, {firstName:"John", lastName:"Chapman"}}
set {p, q, r} to x
set {p2, q2, {lastName:r2}} to x

-- 7. Deep Copy Demonstration
set alpha to {property1:10, property2:20}
set beta to {1, 2, "Hello"}
set gamma to {alpha, beta, "Goodbye"}
copy gamma to delta
set property1 of alpha to 42

-- 8. Scope: Handlers and Shadowing
on demoHandler()
    -- Local inside handler
    local handlerLocal
    set handlerLocal to "I am local to the handler"
    
    -- Global usage inside handler
    global gAgentCount
    set gAgentCount to 99
    
    -- Shadowing
    -- (Assuming 'defaultName' is the property defined at the top)
    local defaultName
    set defaultName to "I am shadowing the property"
    
    -- Demonstrating internal set
    set internalSet to 50
end demoHandler

-- 9. Scope: Nested Script Objects
script Paula
    property currentCount : 20
    
    script Joe
        global currentCount
        on increment()
            set currentCount to currentCount + 1
            return currentCount
        end increment
    end script
    
    tell Joe to increment()
end script

-- 10. Initialization Logic
on initializeGlobals()
    try
        set gNextAgentNumber to gNextAgentNumber + 1
    on error
        set gNextAgentNumber to 1
    end try
end initializeGlobals

-- Execute test behaviors
demoHandler()
run Paula
initializeGlobals()

-- Final check on mutable/immutable logic for the compiler to analyze
set item 1 of myList to 4
-- Result: myList is {4,2,3}, yourList is {4,2,3}, copiedList is {1,2,3}