import os


def init():
    os.system("")


reset = u"\u001b[0m"


def color_demo():
    print()
    print(f"#################################################")
    print(f"# Not all colors are supported by all terminals #")
    print(f"#################################################")
    print()
    print(f"{Colors.FG.black} black {Colors.FG.red} red {Colors.FG.green} green {Colors.FG.yellow} yellow {Colors.FG.blue} blue {Colors.FG.purple} purple {Colors.FG.aqua} aqua {Colors.FG.grey} grey {Colors.FG.reset}")
    print(f"{Colors.FG.black_bright} black_bright {Colors.FG.red_bright} red_bright {Colors.FG.green_bright} green_bright {Colors.FG.yellow_bright} yellow_bright {Colors.FG.blue_bright} blue_bright {Colors.FG.purple_bright} purple_bright {Colors.FG.aqua_bright} aqua_bright {Colors.FG.grey_bright} grey_bright {Colors.FG.reset}")
    print()
    print(f"{Colors.BG.black} black {Colors.BG.red} red {Colors.BG.green} green {Colors.BG.yellow} yellow {Colors.BG.blue} blue {Colors.BG.purple} purple {Colors.BG.aqua} aqua {Colors.BG.grey} grey {Colors.BG.reset}")
    print(f"{Colors.BG.black_bright} black_bright {Colors.BG.red_bright} red_bright {Colors.BG.green_bright} green_bright {Colors.BG.yellow_bright} yellow_bright {Colors.BG.blue_bright} blue_bright {Colors.BG.purple_bright} purple_bright {Colors.BG.aqua_bright} aqua_bright {Colors.BG.grey_bright} grey_bright {Colors.BG.reset}")
    print()
    print("Currently only supported with 'more(code)':")
    print()
    __demo_more_fg()
    print()
    __demo_more_bg()
    print()


def __demo_more_fg():
    for i in range(0, 16):
        print(u"\u001b[38;5;" + str(i) + "m " + str(i).ljust(4), end="")
        if i == 7:
            print(u"\u001b[0m")

    print(u"\u001b[0m")
    print()

    counter = {"block": 0, "row": 0}
    for i in range(16, 232):
        counter["block"] += 1
        counter["row"] += 1
        print(u"\u001b[38;5;" + str(i) + "m " + str(i).ljust(4), end="")
        if counter["block"] == 6:
            counter["block"] = 0
            print(u"\u001b[0m    ", end="")
        if counter["row"] == 36:
            counter["row"] = 0
            print(u"\u001b[0m")

    print(u"\u001b[0m")

    for i in range(232, 256):
        print(u"\u001b[38;5;" + str(i) + "m " + str(i).ljust(4), end="")
    print(u"\u001b[0m")


def __demo_more_bg():
    for i in range(0, 16):
        print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
        if i == 7:
            print(u"\u001b[0m")

    print(u"\u001b[0m")
    print()

    counter = {"block": 0, "row": 0}
    for i in range(16, 232):
        counter["block"] += 1
        counter["row"] += 1
        print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
        if counter["block"] == 6:
            counter["block"] = 0
            print(u"\u001b[0m    ", end="")
        if counter["row"] == 36:
            counter["row"] = 0
            print(u"\u001b[0m")

    print(u"\u001b[0m")

    for i in range(232, 256):
        print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
    print(u"\u001b[0m")


class Colors:
    reset = u"\u001b[0m"

    class FG:
        reset = u"\u001b[0m"
        black = u"\u001b[30m"
        red = u"\u001b[31m"
        green = u"\u001b[32m"
        yellow = u"\u001b[33m"
        blue = u"\u001b[34m"
        purple = u"\u001b[35m"
        aqua = u"\u001b[36m"
        grey = u"\u001b[37m"
        black_bright = u"\u001b[30;1m"
        red_bright = u"\u001b[31;1m"
        green_bright = u"\u001b[32;1m"
        yellow_bright = u"\u001b[33;1m"
        blue_bright = u"\u001b[34;1m"
        purple_bright = u"\u001b[35;1m"
        aqua_bright = u"\u001b[36;1m"
        grey_bright = u"\u001b[37;1m"

        def more(code: int):
            return u"\u001b[38;5;" + str(code) + "m"

        def rgb(r: int, g: int, b: int):
            return u"\u001b[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

    class BG:
        reset = u"\u001b[0m"
        black = u"\u001b[40m"
        red = u"\u001b[41m"
        green = u"\u001b[42m"
        yellow = u"\u001b[43m"
        blue = u"\u001b[44m"
        purple = u"\u001b[45m"
        aqua = u"\u001b[46m"
        grey = u"\u001b[47m"
        black_bright = u"\u001b[40;1m"
        red_bright = u"\u001b[41;1m"
        green_bright = u"\u001b[42;1m"
        yellow_bright = u"\u001b[43;1m"
        blue_bright = u"\u001b[44;1m"
        purple_bright = u"\u001b[45;1m"
        aqua_bright = u"\u001b[46;1m"
        grey_bright = u"\u001b[47;1m"

        def more(code: int):
            return u"\u001b[48;5;" + str(code) + "m"

        def rgb(r: int, g: int, b: int):
            return u"\u001b[48;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"


def text_demo():
    print()
    print(f"#################################################")
    print(f"# Not all styles are supported by all terminals #")
    print(f"#################################################")
    print()
    print(f"Text.Font")
    print(f"{Text.Font.default} default ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt1} alt1 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt2} alt2 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt3} alt3 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt4} alt4 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt5} alt5 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt6} alt6 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt7} alt7 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt8} alt8 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print(f"{Text.Font.alt9} alt9 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Font.reset}")
    print()
    print(f"Text.Style")
    print(f"{Text.Style.bold} bold ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.dim} dim ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.italic} italic ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.underline} underline ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.blink} blink ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.blink_fast} blink_fast ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.reverse} reverse ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.hidden} hidden ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.strike} strike ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print()
    print(f"Text.Style")
    print(f"{Text.Style.framed} framed ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.encircled} encircled ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")
    print(f"{Text.Style.overlined} overlined ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 {Text.Style.reset}")


class Text:
    class Style:
        reset = u"\u001b[0m"
        bold = u"\u001b[1m"
        dim = u"\u001b[2m"
        italic = u"\u001b[3m"
        underline = u"\u001b[4m"
        blink = u"\u001b[5m"
        blink_fast = u"\u001b[6m"
        reverse = u"\u001b[7m"
        hidden = u"\u001b[8m"
        strike = u"\u001b[9m"

        framed = u"\u001b[51m"
        encircled = u"\u001b[52m"
        overlined = u"\u001b[53m"
        remove_framed = u"\u001b[54m"
        remove_overlined = u"\u001b[55m"

    class Font:
        reset = u"\u001b[10m"
        default = u"\u001b[10m"
        alt1 = u"\u001b[11m"
        alt2 = u"\u001b[12m"
        alt3 = u"\u001b[13m"
        alt4 = u"\u001b[14m"
        alt5 = u"\u001b[15m"
        alt6 = u"\u001b[16m"
        alt7 = u"\u001b[17m"
        alt8 = u"\u001b[18m"
        alt9 = u"\u001b[19m"
