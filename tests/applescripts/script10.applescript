-- Reference Script 1: Classes, Primitives, Constants, and Coercion
use AppleScript version "2.4"
use scripting additions

-- 1. Built-in Classes and Primitives
set boolValue to true as boolean
set intValue to 42 as integer
set realValue to 3.14159 as real
set numValue to 100 as number
set textValue to "AppleScript Syntax" as text
set dateValue to current date as date
set colorValue to {65535, 0, 0} as RGB color

-- 2. Constants
set emptyData to missing value as constant
set piValue to pi
set wildcardValue to anything
set myContext to me
set itContext to it
set previousResult to result
set spaceChar to space
set tabChar to tab
set returnChar to return

-- 3. Complex Data Structures
set listData to {1, 2, 3, 4} as list
set recordData to {artist:"Miles", |album name|:"Kind of Blue", released:1959} as record
set classReference to integer as class

-- 4. File and Path Classes
set aliasData to (path to desktop folder) as alias
set posixData to "/tmp/test.txt" as POSIX file
set fileData to file "Macintosh HD:Users:Shared:test.txt" as file

-- 5. Unit Types Coercion 
-- Length
set lenCentimeters to 10 as centimeters
set lenMeters to lenCentimeters as meters
set lenMiles to 5 as miles
set lenYards to lenMiles as yards
set lenFeet to lenYards as feet
set lenInches to lenFeet as inches
set lenKilometers to lenMiles as kilometers

-- Area
set areaSqFeet to 500 as square feet
set areaSqYards to areaSqFeet as square yards
set areaSqMiles to areaSqYards as square miles
set areaSqMeters to areaSqMiles as square meters
set areaSqKilometers to areaSqMeters as square kilometers

-- Volume
set volCubicInches to 100 as cubic inches
set volCubicFeet to volCubicInches as cubic feet
set volCubicYards to volCubicFeet as cubic yards
set volCubicMeters to volCubicYards as cubic meters
set volCubicCentimeters to volCubicMeters as cubic centimeters
set volGallons to 5 as gallons
set volLiters to volGallons as liters
set volQuarts to volGallons as quarts

-- Weight / Mass
set weightOunces to 16 as ounces
set weightPounds to weightOunces as pounds
set weightGrams to 1000 as grams
set weightKilograms to weightGrams as kilograms

-- Temperature
set tempCelsius to 30 as degrees Celsius
set tempFahrenheit to tempCelsius as degrees Fahrenheit
set tempKelvin to tempCelsius as degrees Kelvin