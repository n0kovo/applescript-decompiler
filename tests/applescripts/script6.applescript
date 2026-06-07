-- Reference Script 5: Object Specifiers and Reference Topology
use AppleScript version "2.4"

set dataList to {10, 20, 30, 40, 50, 60, 70, 80, 90, 100}

-- 1. Index and Ordinal Forms
set refIndex to item 2 of dataList
set refFirst to first item of dataList
set refLast to last item of dataList
set refSt to 1st item of dataList
set refNd to 2nd item of dataList
set refRd to 3rd item of dataList
set refTh to 4th item of dataList
set refMiddle to middle item of dataList
set refFront to front item of dataList
set refBack to back item of dataList

-- 2. Range Forms
set refRange1 to items 2 thru 5 of dataList
set refRange2 to items from 3 to 6 of dataList
set refRange3 to items 4 through 7 of dataList

-- 3. Arbitrary and Exhaustive Forms
set refSome to some item of dataList
set refEvery to every item of dataList

-- 4. Logical Filter Forms (Whose/Where)
tell application "System Events"
    set refFilter1 to every process whose name is "Finder"
    set refFilter2 to first process where background only is true
end tell

-- 5. Relative Topologies
tell application "TextEdit"
    if exists front document then
        set refBefore to character before paragraph 2 of front document
        set refAfter to character after paragraph 2 of front document
        set refFrontOf to word in front of word 5 of front document
        set refBackOf to word in back of word 5 of front document
        set refBehind to word behind word 5 of front document
        set refBeginning to beginning of front document
        set refEnd to end of front document
    end if
end tell

-- 6. Name, ID, and Property Evaluation
tell application "System Events"
    set refName to process "Dock"
    set refID to first window of process "Dock" id 1 
    set refProperty to name of process "Dock"
end tell