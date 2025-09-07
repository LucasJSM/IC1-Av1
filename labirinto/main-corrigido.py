import pygame
import random
import time
from collections import deque

# Configurações
TILE_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = TILE_SIZE * GRID_WIDTH
HEIGHT = TILE_SIZE * GRID_HEIGHT
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
VERDE = (0, 200, 155)

# Ponto inicial e final
start = (0, 0)
end = (29, 29)

# Função para verificar se o labirinto é solucionável
def is_maze_solvable(walls):
    distances = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    queue = deque([end])
    distances[end[1]][end[0]] = 1

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                edge = tuple(sorted([(x, y), (nx, ny)]))
                if edge not in walls and distances[ny][nx] == -1:
                    distances[ny][nx] = distances[y][x] + 1
                    queue.append((nx, ny))
    
    return distances[start[1]][start[0]] != -1

# Gera labirinto
def generate_maze():
    random.seed(time.time())
    walls = set()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            for dx, dy in [(1,0),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if random.random() < 0.5:
                        edge = tuple(sorted([(x,y),(nx,ny)]))
                        if (x,y) not in [start,end] and (nx,ny) not in [start,end]:
                            walls.add(edge)
    if not is_maze_solvable(walls):
        return generate_maze()
    return walls

walls = generate_maze()

# Desenha o grid
def draw_grid(screen, distances, path, font):
    screen.fill(WHITE)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if distances[y][x] > 0:
                r = max(0, min(255, 255 - distances[y][x]*2))
                g = max(0, min(255, 255 - distances[y][x]*2))
                b = 255
                pygame.draw.rect(screen, (r,g,b), rect)
                if font:
                    text = font.render(str(distances[y][x]), True, BLACK)
                    text_rect = text.get_rect(center=(x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2))
                    screen.blit(text, text_rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Desenha paredes
    for (x1,y1),(x2,y2) in walls:
        start_pos = (x1*TILE_SIZE + (TILE_SIZE if x2>x1 or y2>y1 else 0), y1*TILE_SIZE + (TILE_SIZE if y2>y1 else 0))
        end_pos = (x2*TILE_SIZE + (0 if x2>x1 or y2>y1 else TILE_SIZE), y2*TILE_SIZE + (0 if y2>y1 else TILE_SIZE))
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)

    # Desenha caminho
    for (x,y) in path:
        center = (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
        pygame.draw.circle(screen, VERDE, center, TILE_SIZE//3)

    # Pontos inicial e final
    pygame.draw.rect(screen, GREEN, (*[i*TILE_SIZE for i in start], TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (*[i*TILE_SIZE for i in end], TILE_SIZE, TILE_SIZE))

# BFS e animação
def bfs(screen, font):
    distances = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    queue = deque([end])
    distances[end[1]][end[0]] = 1
    path = []

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        x, y = queue.popleft()
        if (x,y) == start:
            break

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                edge = tuple(sorted([(x,y),(nx,ny)]))
                if edge not in walls and distances[ny][nx]==-1:
                    distances[ny][nx] = distances[y][x]+1
                    queue.append((nx,ny))

        draw_grid(screen, distances, path, font)
        pygame.display.flip()
        pygame.time.delay(10)

    # Traça caminho
    x, y = start
    while (x,y) != end:
        path.append((x,y))
        min_dist = float('inf')
        next_pos = None
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<GRID_WIDTH and 0<=ny<GRID_HEIGHT:
                edge = tuple(sorted([(x,y),(nx,ny)]))
                if edge not in walls and distances[ny][nx]!=-1 and distances[ny][nx]<min_dist:
                    min_dist = distances[ny][nx]
                    next_pos = (nx,ny)
        if next_pos is None:
            break
        x, y = next_pos
        draw_grid(screen, distances, path, font)
        pygame.display.flip()
        pygame.time.delay(50)
    path.append(end)
    return distances, path

# Loop principal
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS - Labirinto")
    font = pygame.font.SysFont('arial', 14)

    distances, path = bfs(screen, font)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_grid(screen, distances, path, font)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
