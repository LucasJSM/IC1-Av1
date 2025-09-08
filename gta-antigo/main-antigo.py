import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation
from collections import deque

# Caminho da imagem cortada enviada
map_file = "mapa.png"

# Mini mapa lógico (grid representando ruas simplificadas)
# 0 = rua, 1 = obstáculo
mapa = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1], # Objetivo está aqui (6, 17)
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

start = (17, 0)
goal = (6, 17)

# Movimentos possíveis
moves = [(-1,0), (1,0), (0,-1), (0,1)]

def is_valid(mapa, visited, x, y):
    rows, cols = len(mapa), len(mapa[0])
    return (0 <= x < rows and 0 <= y < cols 
            and mapa[x][y] != 1 
            and not visited[x][y])

def bfs(mapa, start, goal):
    queue = deque([(start, [start])])
    visited = [[False]*len(mapa[0]) for _ in range(len(mapa))]
    visited[start[0]][start[1]] = True

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if is_valid(mapa, visited, nx, ny):
                visited[nx][ny] = True
                queue.append(((nx, ny), path + [(nx, ny)]))
    return None

# Encontra o caminho
path = bfs(mapa, start, goal)

# Carregar imagem do mapa real
map_img = mpimg.imread(map_file)

# Escalas para ajustar coordenadas da grade ao mapa real
scale_x = map_img.shape[1] // len(mapa[0])  # largura / colunas
scale_y = map_img.shape[0] // len(mapa)     # altura / linhas

# Criar figura
fig, ax = plt.subplots()
ax.imshow(map_img)

def update(frame):
    ax.clear()
    ax.imshow(map_img)

    # Desenha caminho percorrido até agora
    if frame > 0:
        trajeto = path[:frame]
        xs = [y*scale_x + scale_x/2 for (_, y) in trajeto] # Adicionado offset para centralizar
        ys = [x*scale_y + scale_y/2 for (x, _) in trajeto] # Adicionado offset para centralizar
        ax.plot(xs, ys, color="blue", marker="o")

    # Posição atual do CJ
    if path and frame < len(path):
        x, y = path[frame]
        ax.plot(y*scale_x + scale_x/2, x*scale_y + scale_y/2, "ro", markersize=8, label="CJ 🚴") # Adicionado offset para centralizar

    # Destino (ponto vermelho da direita)
    gx, gy = goal
    ax.plot(gy*scale_x + scale_x/2, gx*scale_y + scale_y/2, "gs", markersize=8, label="Grove 🏠") # Adicionado offset para centralizar

    ax.legend()

# Gerar gif
# if path:
#     ani = animation.FuncAnimation(fig, update, frames=len(path), interval=800, repeat=True)
#     ani.save('gta_bfs_path.gif', writer='pillow')
# else:
#     print("Não foi possível encontrar um caminho.")

ani = animation.FuncAnimation(fig, update, frames=len(path), interval=800, repeat=True)
plt.show()