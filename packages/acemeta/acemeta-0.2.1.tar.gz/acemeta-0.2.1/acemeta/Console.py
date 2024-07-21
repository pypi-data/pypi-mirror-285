from datetime import datetime

class Time():
    """
    A collection of functions that format a datetime or return the current

    #### Functions:
        date(): Returns a date in an european format
        time(): Returns a time in an european format
        clock(): Returns a time with second precision
    """
    def date(datetime: datetime = datetime.now()) -> str:
        "Returns a date in an european format"
        return (datetime).strftime("%d.%m.%Y")

    def time(datetime: datetime = datetime.now()) -> str:
        "Returns a time in an european format"
        return (datetime).strftime("%H:%M")
    
    def clock(datetime: datetime = datetime.now()) -> str:
        "Returns a time in an european format"
        return (datetime).strftime("%H:%M:%S")

class Color():
    """
    A collection of constants that change the following text color

    #### Attributes:
        red, orange, yellow, green, blue, aqua, magenta, purple, black, r
            where r stands for reset
    """
    red = "\033[31m"
    orange = "\033[38;2;255;165;0m"
    yellow = "\033[33m"
    green = "\033[32m"
    blue = "\033[34m"
    aqua = "\033[36m"
    magenta = "\033[35m"
    purple = "\033[38;2;128;0;128m"  # Purple (Hex: #800080)
    black = "\033[30m"
    r = "\033[0m"  # Reset

def log(msg: str, color: str = None) -> None:
    """
    Logs a message to the console

    #### Arguments:
        msg (str): The text that should be printed
        color (str): The color the text is to be displayed in
            red, orange, yellow, green, blue, aqua, magenta, purple, black
    """
    cr = "\033[0m"
    match color:
        case None: cc = Color.r
        case "red": cc = Color.red
        case "orange": cc = Color.orange
        case "yellow":cc = Color.yellow
        case "green": cc = Color.green
        case "blue": cc = Color.blue
        case "aqua": cc = Color.aqua
        case "magenta": cc = Color.magenta
        case "purple": cc = Color.purple
        case "black": cc = Color.black            
        case _: raise SyntaxError(f"Unsupported color: {color}")
    print(f"[{Time.clock()}] " + cc + msg + cr)

class FancyConsole():
    """
    A collection of functions to print fancy console logs

    #### Functions:
        printhead(): Prints a fancy header to the console
        print(): Prints a fancy log to the console
    """

    def printhead(msg: str, first: bool = False) -> None:
        """
        Prints a fancy header to the console

        #### Arguments:
            msg (str): The text that should be displayed in the heading
                Shouldn't be too long so that the format looks good
            first (bool): Whether the heading is the first fancyconsole element after an empty line
        """
        match first:
            case False:
                print(f"╔═╩══════════════════════════════════════════════════════════════════")
                print(f"║ {msg}")
                print(f"╚═╦══════════════════════════════════════════════════════════════════")
            case True:
                print(f"╔════════════════════════════════════════════════════════════════════")
                print(f"║ {msg}")
                print(f"╚═╦══════════════════════════════════════════════════════════════════")

    def print(msg: str, color: str = None) -> None:
        """
        Prints a fancy log to the console

        #### Arguments:
            msg (str): The text that should be printed
                Shouldn't be too long so that the format looks good
            color (str): The color the text is to be displayed in
                red, orange, yellow, green, blue, aqua, magenta, purple, black
        """
        cr = "\033[0m"
        match color:
            case None: cc = Color.r
            case "red": cc = Color.red
            case "orange": cc = Color.orange
            case "yellow":cc = Color.yellow
            case "green": cc = Color.green
            case "blue": cc = Color.blue
            case "aqua": cc = Color.aqua
            case "magenta": cc = Color.magenta
            case "purple": cc = Color.purple
            case "black": cc = Color.black            
            case _: raise SyntaxError(f"Unsupported color: {color}")

        print("  ║ " + cc + msg + cr)