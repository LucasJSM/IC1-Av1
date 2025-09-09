import cv2
import numpy as np
import math
from collections import deque, defaultdict

# --- Função para exibir centralizado e sem deformar ---
def mostrar_centralizado(win_name, img):
    x, y, win_w, win_h = cv2.getWindowImageRect(win_name)

    if win_w <= 0 or win_h <= 0:
        win_w, win_h = 1280, 720

    # Calcula fator de escala mantendo proporção
    h, w = img.shape[:2]
    scale_x = win_w / w
    scale_y = win_h / h
    scale = min(scale_x, scale_y)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Cria fundo preto do tamanho da janela atual
    canvas = np.zeros((win_h, win_w, 3), dtype=np.uint8)

    # Centraliza a imagem no canvas
    x_offset = (win_w - new_w) // 2
    y_offset = (win_h - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    cv2.imshow(win_name, canvas)


# --- Carregar imagem ---
img = cv2.imread(r"C:\Users\lucas\Documents\IC1\gta\mapa.png")
if img is None:
    print("Erro: não foi possível carregar a imagem!")
    exit()

output = img.copy()
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# --- Faixas de cores ---
lower_yellow = np.array([20, 150, 150])
upper_yellow = np.array([40, 255, 255])

lower_red1 = np.array([0, 150, 150])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 150, 150])
upper_red2 = np.array([180, 255, 255])

lower_blue = np.array([100, 150, 150])
upper_blue = np.array([130, 255, 255])

# --- Detectar CJ (amarelo) ---
mask_cj = cv2.inRange(hsv, lower_yellow, upper_yellow)
contours, _ = cv2.findContours(mask_cj, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cjs = []
for cnt in contours:
    (x, y), r = cv2.minEnclosingCircle(cnt)
    if r > 3:
        cjs.append((int(x), int(y)))
if not cjs:
    print("CJ não detectado!")
    exit()
cj = min(cjs, key=lambda p: p[0])
print("CJ detectado em:", cj)

# --- Detectar Grove Street (vermelho) ---
mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
groves = []
for cnt in contours:
    (x, y), r = cv2.minEnclosingCircle(cnt)
    if r > 3:
        groves.append((int(x), int(y)))
if not groves:
    print("Destino Grove não detectado!")
    exit()
grove = groves[0]
print("Grove Street detectado em:", grove)

# --- Detectar ruas (azul) ---
mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
ruas = []
for cnt in contours:
    (x, y), r = cv2.minEnclosingCircle(cnt)
    if r > 3:
        ruas.append((int(x), int(y)))
print("Total de ruas detectadas:", len(ruas))

# --- Montar grafo ---
grafo = defaultdict(list)
limite = 73  # distância máxima para conectar pontos
todos_pontos = ruas + [cj, grove]

for i, p1 in enumerate(todos_pontos):
    for j, p2 in enumerate(todos_pontos):
        if i != j and math.dist(p1, p2) < limite:
            grafo[p1].append(p2)

# --- BFS ---
def bfs(start, goal, grafo):
    queue = deque([(start, [start])])
    visitados = set([start])
    while queue:
        atual, caminho = queue.popleft()
        if atual == goal:
            return caminho
        for vizinho in grafo[atual]:
            if vizinho not in visitados:
                visitados.add(vizinho)
                queue.append((vizinho, caminho + [vizinho]))
    return None

caminho = bfs(cj, grove, grafo)
print("Caminho encontrado:", caminho)

# --- Desenhar base do mapa ---
frame_base = output.copy()
for p in ruas:
    cv2.circle(frame_base, p, 5, (255,0,0), -1)   # ruas azuis
cv2.circle(frame_base, grove, 8, (0,0,255), -1)   # vermelho Grove
for p1, vizinhos in grafo.items():
    for p2 in vizinhos:
        cv2.line(frame_base, p1, p2, (200,200,200), 1)  # conexões

# --- Animação do CJ percorrendo caminho ---
cv2.namedWindow("CJ animado no mapa", cv2.WINDOW_NORMAL)

if caminho:
    while True:
        for i, pos in enumerate(caminho):
            temp = frame_base.copy()

            for j in range(i):
                cv2.line(temp, caminho[j], caminho[j+1], (255,0,255), 3)

            cv2.circle(temp, pos, 10, (0,255,255), -1)

            mostrar_centralizado("CJ animado no mapa", temp)

            key = cv2.waitKey(500) & 0xFF
            if key == 27 or cv2.getWindowProperty("CJ animado no mapa", cv2.WND_PROP_VISIBLE) < 1:
                break
        else:
            continue
        break

cv2.destroyAllWindows()
