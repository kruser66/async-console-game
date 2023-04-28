import os
import time
import asyncio
import curses
from random import randint, choice
from itertools import cycle
from physics import update_speed


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

COURUTINES = []


def read_frame(filename):
    with open(filename, 'r') as f:
        frame = f.read()
    return frame


def load_garbages():
    
    return [read_frame(os.path.join('frames',filename)) for filename in os.listdir('frames') if filename.startswith('trash_')]
    

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


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    garbage_height, garbage_width = get_frame_size(garbage_frame)
    
    column = max(column, garbage_width // 2)
    column = min(column, columns_number - garbage_width - 1)

    row = 1

    while row < rows_number - (garbage_width // 2 + 1):
        draw_frame(canvas, row, column, garbage_frame)
        await sleep()
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, garbages):
    max_rows, max_columns = canvas.getmaxyx()  

    while True:
        offset = randint(5, 30)
        await sleep(offset)
        garbage = choice(garbages)
        COURUTINES.append(fly_garbage(canvas, randint(1, max_columns), garbage))


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
    await sleep()
    
    row_speed = col_speed = 0   
    while True:

        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        row_speed, col_speed = update_speed(row_speed, col_speed, rows_direction, columns_direction)
        if space_pressed:
            COURUTINES.append(fire(canvas, row, column + frame_col // 2, rows_speed=-1, columns_speed=0))           

        second = next(animate)
        draw_frame(canvas, row, column, first, negative=True)

        row = max(1, min(row + row_speed * offset_row, border_row))
        column = max(1, min(column + col_speed * offset_col, border_col))  
        
        draw_frame(canvas, row, column, second)
        first = second

        await sleep()


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep()
    canvas.addstr(round(row), round(column), 'O')
    await sleep()
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, offset_tics=0, symbol='*'):
    while True:

        await sleep(offset_tics)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    max_rows, max_columns = canvas.getmaxyx()

    # загрузка фреймов ракеты
    rocket_frame_1 = read_frame('frames/rocket_frame_1.txt')
    rocket_frame_2 = read_frame('frames/rocket_frame_2.txt')
    spaceship = [rocket_frame_1, rocket_frame_1, rocket_frame_2, rocket_frame_2]
    rocket_height, rocket_width = get_frame_size(rocket_frame_1)
    
    # загрузка фрейма мусора
    garbages = load_garbages()
    
    srart_row = start_col = 1
    border = 2
    center_row = (max_rows - rocket_height) // 2
    center_col = (max_columns- rocket_width) // 2
    end_row = max_rows - border
    end_col = max_columns - border
    

    for item in range(200):
        offset_tics = randint(1, 20)
        COURUTINES.append(blink(canvas, randint(srart_row, end_row), randint(start_col, end_col), offset_tics, choice('+*.:')))
    COURUTINES.append(animate_spaceship(canvas, spaceship, center_row, center_col))
    COURUTINES.append(fill_orbit_with_garbage(canvas, garbages))

    
    # имитация выстрела для отработки StopIteration
    COURUTINES.append(fire(canvas, end_row, randint(start_col, end_col)))

    while True:
        for courutine in COURUTINES.copy():
            try:
                courutine.send(None)
            except StopIteration:
                COURUTINES.remove(courutine)
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
