-- Library of math handlers for testing load script

on areaOfCircle from radius
    if class of radius is not in {real, integer} then error "Radius must be number."
    return radius * radius * pi
end areaOfCircle

on factorial(x)
    if class of x is not integer then error "Factorial requires integer."
    if x < 0 then return 0
    set result to 1
    repeat with i from 2 to x
        set result to result * i
    end repeat
    return result
end factorial