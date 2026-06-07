-- --------------------------------------------
-- 1. use Statements (requires AppleScript 2.3+)
-- --------------------------------------------
use AppleScript version "2.3" -- require minimum version
use scripting additions -- explicitly use scripting additions
use framework "Foundation" -- for AppleScriptObjC bridge (if available)

-- --------------------------------------------
-- 2. Properties and Global Variables
-- --------------------------------------------
property testProperty : 0
global testGlobal

-- --------------------------------------------
-- 3. Class Demonstrations (variables of each class)
-- --------------------------------------------
set aliasExample to (path to desktop) as alias
set appExample to application "Finder"
set boolExample to true
set classExample to class of boolExample -- returns class constant
set constantExample to current application
set dateExample to current date
set fileExample to (path to desktop as text) & "test.txt" as file
set intExample to 42
set listExample to {1, 2, "three", {4, 5}}
set numberExample to 3.14159
set realExample to 1.0E+5
set posixFileExample to POSIX file "/tmp/"
set recordExample to {name:"Test", value:100}
set refExample to a reference to listExample
set rgbExample to {65535, 0, 0} as RGB color
set scriptExample to load script (path to resource "test.scpt" in bundle (path to me)) -- placeholder
set textExample to "Hello, world!"
set unitExample to 5.0 as square meters

-- Log classes to verify
log class of aliasExample
log class of appExample
log class of boolExample
log class of classExample
log class of constantExample
log class of dateExample
log class of fileExample
log class of intExample
log class of listExample
log class of numberExample
log class of realExample
log class of posixFileExample
log class of recordExample
log class of refExample
log class of rgbExample
log class of scriptExample
log class of textExample
log class of unitExample

-- --------------------------------------------
-- 4. Command Demonstrations (alphabetical order)
-- --------------------------------------------
-- activate
activate application "Finder"

-- beep
beep 1

-- choose application
try
	set chosenApp to choose application with prompt "Pick an app:" without multiple selections allowed
end try

-- choose color
try
	set chosenColor to choose color default color {0, 0, 0}
end try

-- choose file
try
	set chosenFile to choose file with prompt "Select a file:" of type {"public.text"} without invisibles
end try

-- choose file name
try
	set newFileName to choose file name with prompt "Save as:" default name "untitled"
end try

-- choose folder
try
	set chosenFolder to choose folder with prompt "Select folder:" without invisibles
end try

-- choose from list
choose from list {"A", "B", "C"} with prompt "Pick one:" OK button name "OK" cancel button name "Cancel"

-- choose remote application
try
	set remoteApp to choose remote application with prompt "Choose remote app:"
end try

-- choose URL
try
	set chosenURL to choose URL showing {File servers}
end try

-- clipboard info
clipboard info
set the clipboard to "Test clipboard"
the clipboard

-- close access (used later with file read/write)
-- copy
copy listExample to listCopy

-- count
count listExample

-- current date
set now to current date

-- delay
delay 0.1

-- display alert
try
	display alert "Alert" message "This is an alert." as informational buttons {"OK"} default button "OK" giving up after 5
end try

-- display dialog
try
	display dialog "Enter something:" default answer "" buttons {"Cancel", "OK"} default button "OK" with icon note giving up after 10
end try

-- display notification (OS X 10.9+)
display notification "Test notification" with title "Title" subtitle "Subtitle" sound name "Glass"

-- do shell script
do shell script "echo 'Hello from shell'"

-- get
get item 1 of listExample

-- get eof
set testFile to (path to desktop as text) & "test_eof.txt"
close access (open for access testFile with write permission)
set eof testFile to 0
write "Hello" to testFile
get eof testFile

-- get volume settings
get volume settings

-- info for
info for (path to desktop)

-- launch
launch application "TextEdit"

-- list disks (deprecated)
list disks

-- list folder (deprecated)
list folder (path to desktop) without invisibles

-- load script (requires a compiled script file; we'll use a dummy)
try
	set loadedScript to load script (path to resource "Dummy.scpt")
end try

-- localized string (requires bundle, but we'll call it anyway)
localized string "hello"

-- log
log "This is a log message"

-- mount volume (commented to avoid actual mount)
-- mount volume "afp://server/volume"

-- offset
offset of "world" in "Hello world"

-- open for access (already used)
-- open location
open location "http://www.apple.com"

-- path to (application)
path to application "Finder"
path to frontmost application
path to me

-- path to (folder)
path to desktop
path to documents folder
path to library folder from system domain

-- path to resource (in current bundle if applet)
try
	path to resource "Info.plist" in bundle (path to me)
end try

-- random number
random number from 1 to 100

-- read (from file opened earlier)
set fp to open for access testFile
set fileContents to read fp
close access fp

-- round
round 3.14159 rounding to nearest

-- run (application)
run application "TextEdit"

-- run script
run script "beep"

-- say
say "Hello" using "Victoria" without waiting until completion

-- scripting components
scripting components

-- set
set testVar to 10

-- set eof (already used)
-- set the clipboard to (already used)
-- set volume
set volume output volume 50

-- store script (requires a script object)
script tempScript
	display dialog "Temp"
end script
try
	store script tempScript in (path to desktop as text) & "temp.scpt" replacing yes
end try

-- summarize
summarize "This is a long text to summarize. It has multiple sentences. We want a summary." in 1

-- system attribute
system attribute "SHELL"
system attribute

-- system info
system info

-- the clipboard (already used)
-- time to GMT
time to GMT

-- write (already used)

-- --------------------------------------------
-- 5. Control Statements
-- --------------------------------------------
-- considering / ignoring (text comparison)
considering case
	"Hello" = "hello" -- false
end considering

ignoring case and diacriticals
	"café" = "cafe" -- true
end ignoring

-- considering / ignoring application responses
tell application "Finder"
	ignoring application responses
		-- do something without waiting
		empty the trash
	end ignoring
end tell

-- error statement
try
	error "Test error" number 500
on error e number n
	log "Caught error: " & e & " (" & n & ")"
end try

-- if (simple)
if true then beep

-- if (compound)
set x to 5
if x < 0 then
	log "Negative"
else if x = 0 then
	log "Zero"
else
	log "Positive"
end if

-- repeat (forever) with exit
set counter to 0
repeat
	set counter to counter + 1
	if counter > 3 then exit repeat
end repeat

-- repeat (number) times
repeat 3 times
	beep
end repeat

-- repeat until
set i to 0
repeat until i = 5
	set i to i + 1
end repeat

-- repeat while
set i to 0
repeat while i < 5
	set i to i + 1
end repeat

-- repeat with loopVariable from startValue to stopValue
repeat with n from 1 to 5
	log n
end repeat

-- repeat with loopVariable in list
repeat with itemRef in {"a", "b", "c"}
	set contents of itemRef to (contents of itemRef) & "x" -- modifies list items if mutable
end repeat

-- tell (simple)
tell application "Finder" to get name of startup disk

-- tell (compound)
tell application "Finder"
	set diskName to name of startup disk
	set folderList to every folder of home
end tell

-- try (full form)
try
	set bad to 1 / 0
on error e number n from obj partial result p to expectedType
	log {e, n, obj, p, expectedType}
end try

-- use (already used at top)
-- using terms from
using terms from application "Mail"
	-- This block uses Mail terminology for compilation only
	-- We can't actually run Mail commands here without tell, but it's allowed
	on perform mail action with messages theMessages for rule theRule
		-- dummy handler
	end perform mail action with messages
end using terms from

-- with timeout
with timeout of 10 seconds
	tell application "Finder" to get name of startup disk
end timeout

-- with transaction (Finder does not support, but we'll use dummy)
tell application "Finder"
	with transaction
		-- dummy
	end transaction
end tell

-- --------------------------------------------
-- 6. Handlers of All Types
-- --------------------------------------------
-- Simple handler (no parameters)
on simpleHandler()
	return "simple"
end simpleHandler

-- Handler with labeled parameters (and direct parameter)
on findNumbers of numberList above minLimit given rounding:roundBoolean
	set resultList to {}
	repeat with x in numberList
		set val to contents of x
		if roundBoolean then set val to round val
		if val > minLimit then set end of resultList to val
	end repeat
	return resultList
end findNumbers

-- Call labeled parameter handler
findNumbers of {5.1, 20.5, 33} above 20 with rounding

-- Handler with positional parameters
on minimumValue(x, y)
	if x < y then return x
	return y
end minimumValue

minimumValue(5, 10)

-- Handler with patterned positional parameters
on displayPoint({x, y})
	display dialog ("x = " & x & ", y = " & y)
end displayPoint

set myPoint to {3, 8}
displayPoint(myPoint)

-- Handler with interleaved parameters (Objective-C style)
on areaOfRectangleWithWidth:w height:h
	return w * h
end areaOfRectangleWithWidth:height:

its areaOfRectangleWithWidth:5 height:10

-- Handler with parameter specifications (class and default value)
on make new theClass with properties theProperties as record : {}
	return {class:theClass, properties:theProperties}
end make

make new "document" with properties {name:"test"}

-- Recursive handler
on factorial(x as integer)
	if x > 0 then return x * (factorial(x - 1))
	return 1
end factorial

factorial(5)

-- Error in handler with try
on safeDivide(a, b)
	try
		return a / b
	on error
		return missing value
	end try
end safeDivide

safeDivide(10, 0)

-- Passing by reference vs value demonstration
on modifyList(theList)
	set end of theList to "new item"
end modifyList

set myList to {1, 2, 3}
modifyList(myList)
log myList -- now {1, 2, 3, "new item"}

-- Calling handlers inside tell block
tell application "Finder"
	my simpleHandler()
end tell

-- --------------------------------------------
-- 7. Script Objects and Inheritance
-- --------------------------------------------
-- Define a parent script object
script ParentScript
	property parentName : "Parent"
	on greet()
		return "Hello from " & my parentName
	end greet
end script

-- Child script with inheritance
script ChildScript
	property parent : ParentScript
	property parentName : "Child" -- override
	on greet()
		-- delegate to parent after check
		if true then
			continue greet()
		end if
	end greet
end script

tell ChildScript to greet() -- returns "Hello from Child"

-- Demonstrate continue statement in child
script AnotherChild
	property parent : ParentScript
	on greet()
		continue greet() -- calls parent's greet
	end greet
end script

tell AnotherChild to greet() -- returns "Hello from Parent"

-- Script library usage (commented, requires separate file)
-- use script "MyLibrary"
-- tell script "MyLibrary" to someHandler()

-- --------------------------------------------
-- 8. Operators Reference (partial, already used throughout)
-- --------------------------------------------
-- Arithmetic: + - * / div mod ^
set sum to 2 + 3
set diff to 5 - 2
set prod to 4 * 5
set quot to 10 / 3
set intDiv to 10 div 3
set modVal to 10 mod 3
set power to 2 ^ 8

-- Comparison: = ≠ > ≥ < ≤
set comp1 to (5 = 5)
set comp2 to (5 ≠ 4)
set comp3 to (6 > 2)
set comp4 to (3 ≥ 3)
set comp5 to (2 < 5)
set comp6 to (4 ≤ 4)

-- Concatenation: &
set concatList to {1, 2} & {3, 4}
set concatText to "Hello " & "world"

-- Reference operator: a reference to
set listRef to a reference to myList

-- --------------------------------------------
-- 9. Special Characters and Constants
-- --------------------------------------------
set quotedText to "He said \"Hello\"."
set pathWithTab to "col1" & tab & "col2"
set multiLine to "Line1" & return & "Line2"
set linefeedExample to "A" & linefeed & "B"

-- --------------------------------------------
-- 10. Unit Type Coercions
-- --------------------------------------------
set area to 100 as square meters
set areaInFeet to area as square feet
set length to 5 as miles
set lengthInKm to length as kilometers

-- --------------------------------------------
-- 11. Date and Time Operations
-- --------------------------------------------
set now to current date
set tomorrow to now + 1 * days
set diffSeconds to tomorrow - now
set weekdayName to weekday of now
set monthName to month of now

-- --------------------------------------------
-- 12. File and Alias Operations
-- --------------------------------------------
set desktopAlias to path to desktop as alias
set desktopPath to POSIX path of desktopAlias

-- --------------------------------------------
-- 13. Advanced Reference Forms (Every, Index, Range, etc.)
-- --------------------------------------------
set sampleText to "The quick brown fox"
set firstWord to word 1 of sampleText
set wordsList to every word of sampleText
set wordsTwoToThree to words 2 thru 3 of sampleText
set middleWord to middle word of sampleText

-- --------------------------------------------
-- 14. Run Handlers (Implicit and Explicit)
-- This script itself has an implicit run handler (all top-level statements)
-- We can also define an explicit one, but a script cannot have both.
-- We'll define an explicit run handler in a nested script object for demo.
script ExplicitRunDemo
	on run
		display dialog "Explicit run handler"
	end run
end script

-- --------------------------------------------
-- 15. Stay-Open Application Handlers (idle, quit)
-- These are only relevant in applets, but we can define them.
on idle
	-- Do nothing, return default rate
	return 30
end idle

on quit
	continue quit
end quit

-- --------------------------------------------
-- 16. open Handler (for droplets)
on open theItems
	repeat with anItem in theItems
		log (anItem as text)
	end repeat
end open

-- ============================================================
-- End of coverage script
-- ============================================================