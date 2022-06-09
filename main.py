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
WHITE = 255, 255, 255
BLACK = 0, 0, 0
color = [(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)) for i in range(7)]
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
block_size = 40
field_size = field_width, field_height = 10, 18
size = width, height = block_size * 16, block_size * 18
border_size = 4
screen = pygame.display.set_mode(size)
is_running = True
clock = pygame.time.Clock()
grid = pygame.Surface(size)
animation = 0
for y in range(1, field_height):
    pygame.draw.line(grid, WHITE, (0, y * block_size), (field_width * block_size, y * block_size))
for x in range(1, field_width + 1):
    pygame.draw.line(grid, WHITE, (x * block_size, 0), (x * block_size, height))
field = [[0 for i in range(field_width)] for j in range(field_height)]
score = 0
font = pygame.font.Font("font.ttf", 20)
text = font.render(f"SCORE: {score}", True, WHITE)
text_rect = text.get_rect()
next_tetromino_grid = pygame.Surface((block_size * 3 + 1, block_size * 3 + 1))
for i in range(4):
    pygame.draw.line(next_tetromino_grid, WHITE, (i * block_size, 0), (i * block_size, 3 * block_size))
    pygame.draw.line(next_tetromino_grid, WHITE, (0, block_size * i), (block_size * 3, block_size * i))

grid_rect = next_tetromino_grid.get_rect()
grid_rect.centerx = block_size * 13
grid_rect.y = block_size * 2
pygame.mixer.music.load("music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


def redraw_grid():
    next_tetromino_grid.fill(BLACK)
    for i in range(5):
        pygame.draw.line(next_tetromino_grid, WHITE, (i * block_size, 0), (i * block_size, 3 * block_size))
        pygame.draw.line(next_tetromino_grid, WHITE, (0, block_size * i), (block_size * 3, block_size * i))


class Tetromino:
    def __init__(self, shape, pos):
        self.shape = shape
        self.positions = list()
        for i in range(4):
            x, y = figures_pos[shape][i][0] + pos[0], figures_pos[shape][i][1] + pos[1]
            self.positions.append([x, y])

    def draw(self, surface: pygame.Surface):
        for x, y in self.positions:
            surface.fill(color[self.shape], (x * block_size + 1, y * block_size + 1, block_size - 2, block_size - 2))

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
next_tetromino = Tetromino(options[-1], (1, 1))


def new_tetromino():
    global tetromino, options, next_tetromino
    for x, y in tetromino.positions:
        field[y][x] = 1
    n = options.pop()
    tetromino = Tetromino(n, spawns[n])


fast_fall = False
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and \
                    all(field[y][min(field_width - 1, x + 1)] != 1 for x, y in tetromino.positions):
                tetromino.update(1, 0)
            elif event.key == pygame.K_LEFT and \
                    all(field[y][max(x - 1, 0)] != 1 for x, y in tetromino.positions):
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
    screen.fill(BLACK)
    screen.blit(grid, (0, 0))
    if fast_fall and animation % (FPS // 4) == 0:
        tetromino.update(0, 1)
    elif animation % (FPS // 2) == 0:
        tetromino.update(0, 1)
    for i in range(len(field)):
        for j in range(len(field[0])):
            if field[i][j] == 1:
                screen.fill(WHITE, (j * block_size + 1, i * block_size + 1, block_size - 2, block_size - 2))
    if any((field[y][x] == 1 for x, y in tetromino.positions)):
        tetromino.update(0, -1)
        new_tetromino()
    elif any((y == len(field) - 1 for x, y in tetromino.positions)):
        new_tetromino()
    full_lines = list()
    for i in range(len(field)):
        if all(map(lambda x: x == 1, field[i])):
            full_lines.append(i)
    score += 100 * (2 ** len(full_lines) - 1)
    text = font.render(f"SCORE: {score}", True, WHITE)
    while full_lines:
        num_line = full_lines.pop()
        full_lines = [i - 1 if i < num_line else i for i in full_lines]
        for i in range(num_line, 0, -1):
            for j in range(len(field[0])):
                field[i][j] = field[i - 1][j]
    if any((field[0][i] == 1 for i in range(len(field[0])))):
        score = 0
        field = [[0 for i in range(width // block_size)] for j in range(height // block_size)]
        n = options.pop()
        tetromino = Tetromino(n, spawns[n])
    if not options:
        options = list(range(7))
        random.shuffle(options)
    tetromino.draw(screen)
    text_rect.centerx = block_size * 13
    text_rect.y = block_size * 6
    screen.blit(text, text_rect)
    redraw_grid()
    next_tetromino = Tetromino(options[-1], (1, 1))
    next_tetromino.draw(next_tetromino_grid)
    screen.blit(next_tetromino_grid, grid_rect)
    animation += 1
    pygame.display.flip()
    clock.tick(FPS)
