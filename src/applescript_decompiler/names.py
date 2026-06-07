"""AppleScript terminology tables.

Maps the four-character codes (OSTypes) embedded in compiled scripts back to
their source-level AppleScript names.
"""

# Four-character-code to source-level name. Covers classes, properties, and
# common enumerators. Unknown codes fall back to the raw-chevron form.
FOUR_CC: dict[str, str] = {
    # properties
    "pnam": "name",
    "pcls": "class",
    "ID  ": "id",
    "pALL": "properties",
    "rslt": "result",
    "ascr": "AppleScript",
    # core classes
    "reco": "record",
    "list": "list",
    "long": "integer",
    "shor": "small integer",
    "doub": "real",
    "sing": "real",
    "TEXT": "text",
    "ctxt": "text",
    "utxt": "Unicode text",
    "itxt": "international text",
    "bool": "boolean",
    "nmbr": "number",
    "type": "type class",
    "alis": "alias",
    "file": "file",
    "fsrf": "file reference",
    "psxf": "POSIX file",
    "furl": "«class furl»",
    "ldt ": "date",
    "cobj": "item",
    "cwor": "word",
    "cha ": "character",
    "cpar": "paragraph",
    "clin": "line",
    "scpt": "script",
    # constants and pseudo-classes
    "pi  ": "pi",
    "spac": "space",
    "tab ": "tab",
    "ret ": "return",
    "lnfd": "linefeed",
    "quot": "quote",
    # common properties / specifiers
    "sdsk": "startup disk",
    "curu": "current user",
    "pcnt": "contents",
    "wkdy": "weekday",
    "mnth": "month",
    "psxp": "POSIX path",
    "leng": "length",
    "days": "days",
    "pscd": "Unicode text",
    "data": "data",
    "null": "null",
    "msng": "missing value",
    "hand": "handler",
    "cRGB": "RGB color",
    "capp": "application",
    "cwin": "window",
    "cdoc": "document",
    "prcs": "process",
    "DATA": "data",
    "prdt": "product",
    # unit types
    "cmtr": "centimeters",
    "metr": "meters",
    "kmtr": "kilometers",
    "inch": "inches",
    "feet": "feet",
    "yard": "yards",
    "mile": "miles",
    "sqrm": "square meters",
    "sqkm": "square kilometers",
    "sqft": "square feet",
    "sqyd": "square yards",
    "sqmi": "square miles",
    "litr": "liters",
    "galn": "gallons",
    "qrts": "quarts",
    "cuyd": "cubic yards",
    "cyrd": "cubic yards",
    "cuft": "cubic feet",
    "cfet": "cubic feet",
    "cucm": "cubic centimeters",
    "ccmt": "cubic centimeters",
    "cmet": "cubic meters",
    "cmtr3": "cubic meters",
    "cuin": "cubic inches",
    "cuic": "cubic inches",
    "enum": "missing value",
    "****": "anything",
    "kgrm": "kilograms",
    "gram": "grams",
    "lbs ": "pounds",
    "ozs ": "ounces",
    "degc": "degrees Celsius",
    "degf": "degrees Fahrenheit",
    "degk": "degrees Kelvin",
    # text item delimiters / considering
    "case": "case",
    "diac": "diacriticals",
    "expa": "expansion",
    "hyph": "hyphens",
    "puct": "punctuation",
    "whit": "white space",
    # file / positions
    "begi": "beginning",
    "end ": "end",
    "befo": "before",
    "afte": "after",
    # command / event
    "oapp": "open application",
    "quit": "quit",
    "idle": "idle",
    "aevt": "AppleEvent",
}


# AppleEvent identifier codes to handler names. "Run Main Script" is stored as
# 'oapp' (open application) by the compiler; every other lifecycle handler has
# a similar code.
EVENT_NAMES: dict[str, str] = {
    "oapp": "run",
    "aevt": "run",
    "quit": "quit",
    "idle": "idle",
    "odoc": "open",
    "pdoc": "print",
    "rapp": "reopen",
    "alnk": "activated",
}


# AppleEvent verb (event-id) codes to their AppleScript command names. Used to
# turn `curd()` back into `current date`, etc. Commands not listed here keep
# their raw four-char verb.
COMMAND_NAMES: dict[str, str] = {
    "curd": "current date",
    "dlog": "display dialog",
    "dnot": "display notification",
    "rond": "round",
    "beep": "beep",
    "ffdr": "path to",
    "offs": "offset",
    "dela": "delay",
    "rand": "random number",
    "cmnt": "log",
    "sigt": "system info",
    "cnte": "count",
    "dosc": "do shell script",
    "actv": "activate",
    "read": "read",
    "load": "load script",
    "stor": "store script",
    "stdf": "choose file",
    "stfl": "choose folder",
    "nwfl": "choose file name",
    "ppcb": "choose application",
    "chra": "choose remote application",
    "chur": "choose URL",
    "chcl": "choose color",
    "gtfl": "choose from list",
    "qspr": "summarize",
    "lsts": "localized string",
}


# Eight-character (enumerator/pseudo-constant) codes to their source names.
# Stored as a (type, value) pair of four-char codes; only a handful have a
# bare AppleScript spelling. Unknown codes fall back to the raw «constant …»
# form, which is itself valid AppleScript.
DOUBLE_CC: dict[str, str] = {
    "misccura": "current application",
    "afdrdesk": "desktop",
    "essvesva": "File servers",
}
