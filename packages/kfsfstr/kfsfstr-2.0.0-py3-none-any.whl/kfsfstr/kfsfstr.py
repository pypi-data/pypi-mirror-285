# Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import colorama
import inspect
import math
import sys


def full_class_name(obj: object) -> str:
    """
    Returns the full class name of obj, including module.

    Arguments:
    - obj: object to analyse

    Returns:
    - full_class_name: full class name of obj, including module
    """

    full_class_name: str="" # result
    module_name: str


    module_name=obj.__class__.__module__
    if module_name!=str.__class__.__module__:   # if not in module "builtins":
        full_class_name+=f"{module_name}."      # prepend module name

    full_class_name+=obj.__class__.__name__ # class name

    return full_class_name
# source: https://stackoverflow.com/questions/18176602/how-to-get-the-name-of-an-exception-that-was-caught-in-python


def notation_abs(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, width: int=0) -> str:   # type:ignore
    """
    Formats rounded number as string, no changing of magnitude for decimal prefixes (notation absolute).

    Arguments:
    - x: number to format
    - precision:
        - if round_static==False: Round to significant digits.
        - if round_static==True: Round to magnitude 10^(-precision), like built-in round().
    - trailing_zeros: Append zeros until reached precision.
    - width: After appending trailing zeros, prepend zeros until reaching width. Width includes decimal separator.

    Returns:
    - x: formatted number
    """

    x: float|str


    if round_static==False:
        x=round_sig(x, precision)                   # round to signifcant number
    else:
        x=round(x, precision)                       # round to decimal place static

    if x!=0:                                        # determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    # x magnitude floored
    else:
        magnitude=0                                 # for number 0 magnitude 0, practical for decimal prefix

    if round_static==False:
        dec_places=magnitude*-1+precision-1         # decimal places required
    else:
        dec_places=precision                        # decimal places required
    if dec_places<0:                                # at least 0 decimal places
        dec_places=0


    x=f"{x:0{width},.{dec_places}f}".replace(".", "%TEMP%").replace(",", ".").replace("%TEMP%", ",")    # int to str, comma as decimal separator

    if trailing_zeros==False and "," in x:  # if trailing zeros undesired and decimal places existing:
        x=x.rstrip("0")                     # remove trailing zeros
        if x[-1]==",":                      # if because of that last character comma:
            x=x[:-1]                        # remove comma

    return x


def notation_tech(x: float, precision: int, round_static: bool=False, trailing_zeros: bool=True, add_decimal_prefix: bool=True, width: int=0) -> str:   # converts to notation technical as string # type:ignore
    """
    Formats rounded number as string, changes magnitude for decimal prefixes (notation technical).

    Arguments:
    - x: number to format
    - precision:
        - if round_static==False: Round to significant digits.
        - if round_static==True: Round to magnitude 10^(-precision), like built-in round().
    - trailing_zeros: Append zeros until reached precision.
    - add_decimal_prefix: Append decimal prefix for units.
    - width: After appending trailing zeros, prepend zeros until reaching width. Width includes decimal separator.

    Returns:
    - x: formatted number

    Raises:
    - ValueError: There are only decimal prefixes for magnitudes [-30; 33[. There is no decimal prefix for given magnitude.
    """

    x: float|str


    if round_static==False:
        x=round_sig(x, precision)                   # round to signifcant number
    else:
        x=round(x, precision)                       # round to decimal place static

    if x!=0:                                        # determine magnitude after rounding in case rounding changes magnitude
        magnitude=math.floor(math.log10(abs(x)))    # x magnitude floored
    else:
        magnitude=0                                 # for number 0 magnitude 0, practical for decimal prefix

    if round_static==False:
        dec_places=magnitude%3*-1+precision-1       # decimal places required
    else:
        dec_places=magnitude-magnitude%3+precision  # decimal places required
    if dec_places<0:                                # at least 0 decimal places
        dec_places=0

    x=f"{x/math.pow(10, magnitude-magnitude%3):0{width}.{dec_places}f}".replace(".", ",")   # int to str, to correct magnitude and number of decimal places, comma as decimal separator

    if trailing_zeros==False and "," in x:  # if trailing zeros undesired and decimal places existing:
        x=x.rstrip("0")                     # remove trailing zeros
        if x[-1]==",":                      # if because of that last character comma:
            x=x[:-1]                        # remove comma

    if add_decimal_prefix==True:    # if decimal prefix desired: append
        if    30<=magnitude and magnitude< 33:
            x+="Q"
        elif  27<=magnitude and magnitude< 30:
            x+="R"
        elif  24<=magnitude and magnitude< 27:
            x+="Y"
        elif  21<=magnitude and magnitude< 24:
            x+="Z"
        elif  18<=magnitude and magnitude< 21:
            x+="E"
        elif  15<=magnitude and magnitude< 18:
            x+="P"
        elif  12<=magnitude and magnitude< 15:
            x+="T"
        elif   9<=magnitude and magnitude< 12:
            x+="G"
        elif   6<=magnitude and magnitude<  9:
            x+="M"
        elif   3<=magnitude and magnitude<  6:
            x+="k"
        elif   0<=magnitude and magnitude<  3:
            x+=""
        elif  -3<=magnitude and magnitude<  0:
            x+="m"
        elif  -6<=magnitude and magnitude< -3:
            x+="µ"
        elif  -9<=magnitude and magnitude< -6:
            x+="n"
        elif -12<=magnitude and magnitude< -9:
            x+="p"
        elif -15<=magnitude and magnitude<-12:
            x+="f"
        elif -18<=magnitude and magnitude<-15:
            x+="a"
        elif -21<=magnitude and magnitude<-18:
            x+="z"
        elif -24<=magnitude and magnitude<-21:
            x+="y"
        elif -27<=magnitude and magnitude<-24:
            x+="r"
        elif -30<=magnitude and magnitude<-27:
            x+="q"
        else:
            raise ValueError(f"Error in {notation_tech.__name__}{inspect.signature(notation_tech)}: There are only decimal prefixes for magnitudes [-30; 33[ defined. There is no decimal prefix for given magnitude {magnitude}.")

    return x


colour_i: int=0 # which colour currently? memorise for continueing at next function call
def rainbowify(s: str, rainbow_colours: list=[colorama.Fore.MAGENTA, colorama.Fore.RED, colorama.Fore.YELLOW, colorama.Fore.GREEN, colorama.Fore.CYAN, colorama.Fore.BLUE]) -> str:
    """
    Dyes string to rainbow coloured string.

    Arguments:
    - s: string that should be rainbowified
    - rainbow_colours: list of colours to dye s with, usually magenta, red, yellow, green, cyan, blue

    Returns:
    - s_rainbowified: rainbowified string
    """

    global colour_i
    s_rainbowified: str=""  # result


    if sys.platform=="win32" or sys.platform=="cygwin": # if windows:
        colorama.just_fix_windows_console()             # enable colours on windows console


    for char in s:
        if char!=" ":   # if not space: dye
            s_rainbowified+=rainbow_colours[colour_i]   # dye
            colour_i=(colour_i+1)%len(rainbow_colours)  # determine colour next
        s_rainbowified+=char                            # append character in any case
    s_rainbowified+=colorama.Style.RESET_ALL            # reset colours

    return s_rainbowified


def round_sig(x: float, significants: int) -> float:
    """
    Round x to significant number. If significants is smaller 1, always returns 0.

    Arguments:
    - x: number to round
    - significants: number of significant digits to round to

    Returns:
    - x: rounded number
    """

    x=float(x)


    if x==0:    # if x is 0: magnitude determination fails, but rounded number always 0
        return x

    magnitude=math.floor(math.log10(abs(x)))    # determine magnitude floored
    x=round(x, -1*magnitude+significants-1)     # round #type:ignore

    return x