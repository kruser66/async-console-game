import time
import asyncio
import curses
from random import randint, choice
from itertools import cycle


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


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


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""
    
    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


async def animate_spaceship(canvas, frames, row=20, column=20):

    animate = cycle(frames)
    first = next(animate)
    
    max_rows, max_columns = canvas.getmaxyx()
    
    frame_row, frame_col = get_frame_size(first)
    border_row = max_rows - frame_row - 1
    border_col = max_columns - frame_col -1
    
    offset_row = 2
    offset_col = 4
    
    draw_frame(canvas, row, column, first)
    await asyncio.sleep(0)
    
    while True:
        second = next(animate)
        draw_frame(canvas, row, column, first, negative=True)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)       
        row = max(1, min(row + rows_direction * offset_row, border_row))
        column = max(1, min(column + columns_direction * offset_col, border_col))  
        
        draw_frame(canvas, row, column, second)
        first = second

        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    for _ in range(5):
        await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), 'O')
    for _ in range(5):
        await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, offset_tics=0, symbol='*'):
    while True:
        for _ in range(offset_tics):
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
    canvas.nodelay(True)
    max_rows, max_columns = canvas.getmaxyx()

    frame1 = read_frame('frames/rocket_frame_1.txt')
    frame2 = read_frame('frames/rocket_frame_2.txt')
    spaceship = [frame1, frame1, frame2, frame2]
    frame_row, frame_col = get_frame_size(frame1)
    
    srart_row = start_col = 1
    border = 2
    center_row = (max_rows - frame_row) // 2
    center_col = (max_columns- frame_col) // 2
    end_row = max_rows - border
    end_col = max_columns - border
    
    courutines = []
    for item in range(300):
        offset_tics = randint(1, 20)
        courutines.append(blink(canvas, randint(srart_row, end_row), randint(start_col, end_col), offset_tics, choice('+*.:')))
    courutines.append(animate_spaceship(canvas, spaceship, center_row, center_col))
    
    # имитация выстрела для отработки StopIteration
    courutines.append(fire(canvas, end_row, randint(start_col, end_col)))

    while True:
        for courutine in courutines.copy():
            try:
                courutine.send(None)
            except StopIteration:
                courutines.remove(courutine)
            canvas.refresh()
        
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
