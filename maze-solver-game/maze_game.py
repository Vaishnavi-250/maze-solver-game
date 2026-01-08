import pygame
from collections import deque

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 400, 300
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Solver Game")

CELL = 100

# Maze layout
maze = [
    ['S','0','1','0'],
    ['1','0','1','0'],
    ['0','0','0','G']
]

ROWS, COLS = len(maze), len(maze[0])
MOVES = [(-1,0),(1,0),(0,-1),(0,1)]

# Find start and goal
def find(symbol):
    for i in range(ROWS):
        for j in range(COLS):
            if maze[i][j] == symbol:
                return i, j

player = find('S')
goal = find('G')

# Draw maze and path
def draw(path=[]):
    WIN.fill((255, 255, 255))

    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j*CELL, i*CELL, CELL, CELL)

            if maze[i][j] == '1':
                pygame.draw.rect(WIN, (0, 0, 0), rect)        # Wall
            elif (i, j) in path:
                pygame.draw.rect(WIN, (0, 255, 0), rect)    # Path

            pygame.draw.rect(WIN, (200, 200, 200), rect, 1)

    # Player (Blue)
    pygame.draw.rect(
        WIN, (0, 0, 255),
        (player[1]*CELL, player[0]*CELL, CELL, CELL)
    )

    # Goal (Red)
    pygame.draw.rect(
        WIN, (255, 0, 0),
        (goal[1]*CELL, goal[0]*CELL, CELL, CELL)
    )

    pygame.display.update()

# BFS algorithm
def bfs():
    queue = deque([(player, [player])])
    visited = set([player])

    while queue:
        (x, y), path = queue.popleft()

        if (x, y) == goal:
            return path

        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy

            if (0 <= nx < ROWS and 0 <= ny < COLS
                and maze[nx][ny] != '1'
                and (nx, ny) not in visited):

                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return []

# Game loop
running = True
clock = pygame.time.Clock()
path = []

while running:
    clock.tick(5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            x, y = player

            if event.key == pygame.K_w:
                nx, ny = x-1, y
            elif event.key == pygame.K_s:
                nx, ny = x+1, y
            elif event.key == pygame.K_a:
                nx, ny = x, y-1
            elif event.key == pygame.K_d:
                nx, ny = x, y+1
            elif event.key == pygame.K_SPACE:
                path = bfs()
                continue
            else:
                continue

            if (0 <= nx < ROWS and 0 <= ny < COLS
                and maze[nx][ny] != '1'):
                player = (nx, ny)

    draw(path)

pygame.quit()
