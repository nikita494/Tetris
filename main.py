import random
import copy
import pygame
FPS = 60
LINE = 0
SQUARE = 1
RIGHT_Z = 2
LEFT_Z = 3
RIGHT_L = 4
LEFT_L = 5
WEDGE = 6
figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]
spawns = [(5, abs(min(min(figures_pos[i], key=lambda x: min(x[0], x[1]))))) for i in range(7)]
pygame.init()
pygame.display.set_icon(pygame.image.load("icon.png"))
pygame.display.set_caption('Tetris')
size = width, height = 400, 720
block_size = 40
border_size = 4
screen = pygame.display.set_mode(size)
is_running = True
clock = pygame.time.Clock()
grid = pygame.Surface(size)
white = 255, 255, 255
black = 0, 0, 0
animation = 0
for y in range(1, height // block_size):
    pygame.draw.line(grid, white, (0, y * block_size), (width, y * block_size))
for x in range(1, width // block_size):
    pygame.draw.line(grid, white, (x * block_size, 0), (x * block_size, height))
field = [[0 for i in range(width // block_size)] for j in range(height // block_size)]


class Tetromino:
    def __init__(self, shape, pos):
        self.positions = list()
        for i in range(4):
            x, y = figures_pos[shape][i][0] + pos[0], figures_pos[shape][i][1] + pos[1]
            self.positions.append([x, y])

    def draw(self, surface: pygame.Surface):
        for x, y in self.positions:
            surface.fill(white, (x * block_size + 1, y * block_size + 1, block_size - 2, block_size - 2))

    def update(self, x, y):
        if all(0 <= i[0] + x < len(field[0]) and 0 <= i[1] + y < len(field) for i in self.positions):
            for i in self.positions:
                i[0] += x
                i[1] += y

    def check_borders(self):
        return all(0 <= i[0] < len(field[0]) and 0 <= i[1] < len(field) for i in self.positions)


options = list(range(7))
random.shuffle(options)
n = options.pop()
tetromino = Tetromino(n, spawns[n])


def new_tetromino():
    global tetromino, options
    for x, y in tetromino.positions:
        field[y][x] = 1
    if not options:
        options = list(range(7))
        random.shuffle(options)
    n = options.pop()
    tetromino = Tetromino(n, spawns[n])


fast_fall = False
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                tetromino.update(1, 0)
            elif event.key == pygame.K_LEFT:
                tetromino.update(-1, 0)
            elif event.key == pygame.K_SPACE:
                fast_fall = not fast_fall
            elif event.key == pygame.K_UP:
                center = tetromino.positions[0]
                old_tetromino = copy.deepcopy(tetromino)
                for i in range(4):
                    x = tetromino.positions[i][1] - center[1]
                    y = tetromino.positions[i][0] - center[0]
                    tetromino.positions[i][0] = center[0] - x
                    tetromino.positions[i][1] = center[1] + y
                    if not tetromino.check_borders():
                        tetromino = old_tetromino
                        break
    screen.fill(black)
    screen.blit(grid, (0, 0))
    if fast_fall and animation % (FPS // 4) == 0:
        tetromino.update(0, 1)
    elif animation % FPS == 0:
        tetromino.update(0, 1)
    for i in range(len(field)):
        for j in range(len(field[0])):
            if field[i][j] == 1:
                screen.fill(white, (j * block_size + 1, i * block_size + 1, block_size - 2, block_size - 2))
    if any((field[y][x] == 1 for x, y in tetromino.positions)):
        tetromino.update(0, -1)
        new_tetromino()
    elif any((y == len(field) - 1 for x, y in tetromino.positions)):
        new_tetromino()
    full_lines = list()
    for i in range(len(field)):
        if all(map(lambda x: x == 1, field[i])):
            full_lines.append(i)
    while full_lines:
        print(1)
        num_line = full_lines.pop()
        full_lines = [i - 1 if i < num_line else i for i in full_lines]
        for i in range(num_line, 0, -1):
            for j in range(len(field[0])):
                field[i][j] = field[i - 1][j]

    tetromino.draw(screen)
    animation += 1
    pygame.display.flip()
    clock.tick(FPS)
