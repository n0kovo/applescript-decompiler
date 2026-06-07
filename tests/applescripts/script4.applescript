-- Reference Script 7: Declarative Directives and Inter-Script Terminology
use AppleScript version "2.5"
use scripting additions
use framework "Foundation"
use application "Safari" version "7.0" without importing

tell application "Safari" to activate

-- Object-Oriented Inheritance Setup
property parent : script "MyConstants"

-- Framework Class Instance via ASObjC
set currentHost to current application's NSHost's currentHost()