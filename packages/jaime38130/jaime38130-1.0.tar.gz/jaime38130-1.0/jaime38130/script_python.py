


from colorama import init, Fore, Back, Style

init()

def printer_color(*args, fore, back):
    if len(args) == 1:
        print(fore + str(args[0]) + Style.RESET_ALL)

    if len(args) > 1:
        if "header" in args:
            print("\n"+back + Style.BRIGHT)
            print(fore + "\t" + str(args[0]))
            print(Style.RESET_ALL + "\n")

        if "*" in args:
            print(fore + str(args[0]))
            print(Style.RESET_ALL)

        if "**" in args:
            print("\n"+fore + str(args[0]))
            print(Style.RESET_ALL)


def green(*args): printer_color(*args, fore=Fore.GREEN, back=Back.GREEN)
def white(*args): printer_color(*args, fore=Fore.WHITE, back=Back.WHITE)
def black(*args): printer_color(*args, fore=Fore.BLACK, back=Back.BLACK)
def cyan(*args): printer_color(*args, fore=Fore.CYAN, back=Back.CYAN)
def magenta(*args): printer_color(*args, fore=Fore.MAGENTA, back=Back.MAGENTA)
def red(*args): printer_color(*args, fore=Fore.RED, back=Back.RED)
def blue(*args): printer_color(*args, fore=Fore.BLUE, back=Back.BLUE)
def yellow(*args): printer_color(*args, fore=Fore.YELLOW, back=Back.YELLOW)


def jaimedcsilva(): print("Hello Jaime!")
