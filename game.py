import time
import asyncio
import curses
from random import randint, choice
from itertools import cycle


def read_frame(filename):
    with open(filename, 'r') as f:
        frame = f.read()
    return frame


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, frames, row=20, column=20):

    animate = cycle(frames)

    first = next(animate)
    draw_frame(canvas, row, column, first)
    for _ in range(10):
        await asyncio.sleep(0)
    
    while True:
        second = next(animate)

        draw_frame(canvas, row, column, first, negative=True)
        draw_frame(canvas, row, column, second)
        first = second
        canvas.refresh()

        for _ in range(10):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    for _ in range(randint(1, 20)):
        await asyncio.sleep(0)

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(randint(1, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    rows, columns = canvas.getmaxyx()

    spaceship = [
        read_frame('frames/rocket_frame_1.txt'),
        read_frame('frames/rocket_frame_2.txt')
    ]

    courutines = []
    for item in range(300):
        courutines.append(blink(canvas, randint(1, rows-2), randint(1, columns-2), choice('+*.:')))
    courutines.append(animate_spaceship(canvas, spaceship))
    courutines.append(fire(canvas, rows-2, columns/2))
    courutines.append(fire(canvas, rows-2, columns-10))

    while True:
        stop = []
        for index, courutine in enumerate(courutines.copy()):
            if courutine in stop:
                continue
            try:
                courutine.send(None)
            except StopIteration:
                stop.append(courutine)
                courutines.pop(index)
            canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
