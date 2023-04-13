import time
import asyncio
import curses


class EventLoopCommand():

    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):

    def __init__(self, seconds):
        self.seconds = seconds


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    row, column = (5, 20)
    canvas.border()

    courutines = []
    for item in range(5):
        courutines.append(blink(canvas, row, column + item*2, '*'))

    while True:
        for courutine in courutines.copy():
            courutine.send(None)
        canvas.refresh()
        time.sleep(2)
        for courutine in courutines.copy():
            courutine.send(None)
        canvas.refresh()
        time.sleep(0.3)
        for courutine in courutines.copy():
            courutine.send(None)
        canvas.refresh()
        time.sleep(0.5)
        for courutine in courutines.copy():
            courutine.send(None)
        canvas.refresh()
        time.sleep(0.3)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
