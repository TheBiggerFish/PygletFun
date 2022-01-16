import time

from window import Window


def main():
    windowHeight = 900
    windowWidth = 600
    ticks = 30
    ballCount = 5
    simSpeed = 200

    win = Window(windowHeight, windowWidth, ticks, ballCount, simSpeed)

    while win.isOpen():
        win.update()
        time.sleep(1/ticks)


main()
