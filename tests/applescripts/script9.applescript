-- Reference Script 2: Operators, Expressions, and Mathematical Computations
use AppleScript version "2.4"

-- 1. Mathematical Operators
set mathAdd to 10 + 5
set mathSub to 10 - 5
set mathMul to 10 * 5
set mathDiv to 10 / 5
set mathDivFractional to 10 ÷ 2
set mathDivInt to 10 div 3
set mathMod to 10 mod 3
set mathExp to 10 ^ 2

-- 2. Boolean Logic Operators
set logicAnd to (true and false)
set logicOr to (true or false)
set logicNot to not logicAnd

-- 3. Comparison Operators
set compEq to (5 = 5)
set compNeq to (5 ≠ 6)
set compGt to (5 > 4)
set compLt to (4 < 5)
set compGte to (5 ≥ 5)
set compLte to (4 ≤ 5)

-- 4. String and List Specific Operators
set strConcat to "Hello" & " World"
set checkStarts to strConcat starts with "Hello"
set checkEnds to strConcat ends with "World"
set checkContains to strConcat contains "o"
set checkContained to "o" is contained by strConcat

-- 5. Reference Operators
set dataList to {10, 20, 30}
set listRef to a reference to dataList