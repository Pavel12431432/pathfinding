import pygame
import math

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 100
COLS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
D, D2 = 10, math.sqrt(200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pathfinding')
font = pygame.font.SysFont('consolas', 35)
small_font = pygame.font.SysFont('consolas', 20)
clock = pygame.time.Clock()


class Tile:
	def __init__(self, pos):
		self.parent = None
		self.pos = pos
		self.barrier = False
		self.g_cost = float('inf')
		self.h_cost = float('inf')

	def f_cost(self):
		return self.g_cost + self.h_cost

	def get_neighbors(self):
		return [(self.pos[1] + y, self.pos[0] + x, x ^ y) for x in range(-1, 2) for y in range(-1, 2) if
				ROWS > self.pos[1] + y >= 0 <= self.pos[0] + x < COLS and not (x == y == 0)]


def heuristic(a, b):
	dx = abs(a[0] - b[0])
	dy = abs(a[1] - b[1])

	return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)  # octile distance
	# return D * (dx + dy) - D * min(dx, dy)	# Chebyshev distance
	# return D * math.sqrt(dx ** 2 + dy ** 2) # euclidean distance
	# return D * (dx + dy) # manhattan distance


grid = [[Tile((x, y)) for x in range(COLS)] for y in range(ROWS)]

start, target = (0, 0), (ROWS - 1, COLS - 1)

grid[start[0]][start[1]].g_cost = 0
grid[start[0]][start[1]].h_cost = heuristic(start, target)
open = [grid[start[0]][start[1]]]

closed = []


def inp():
	global start, target, open
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				return True
			elif event.key == pygame.K_a:
				pos = pygame.mouse.get_pos()
				pos = pos[1] // TILE_SIZE, pos[0] // TILE_SIZE
				start = pos
				grid[start[0]][start[1]].g_cost = 0
				grid[start[0]][start[1]].h_cost = heuristic(start, target)
				open = [grid[start[0]][start[1]]]
			elif event.key == pygame.K_d:
				pos = pygame.mouse.get_pos()
				pos = pos[1] // TILE_SIZE, pos[0] // TILE_SIZE
				target = pos
		else:
			pos = pygame.mouse.get_pos()
			pos = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
			if pygame.mouse.get_pressed()[0]:
				grid[pos[1]][pos[0]].barrier = True
			if pygame.mouse.get_pressed()[2]:
				grid[pos[1]][pos[0]].barrier = False


def draw():
	screen.fill((0, 0, 0))

	for x in range(COLS):
		for y in range(ROWS):
			if (y, x) == start:
				pygame.draw.rect(screen, (0, 200, 230), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
			elif (y, x) == target:
				pygame.draw.rect(screen, (150, 10, 200), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
			elif grid[y][x].barrier:
				pygame.draw.rect(screen, (10, 10, 10), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
			elif grid[y][x] in open:
				pygame.draw.rect(screen, (50, 200, 50), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
			elif grid[y][x] in closed:
				pygame.draw.rect(screen, (200, 50, 50), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
			else:
				pygame.draw.rect(screen, (50, 50, 50), ((x * TILE_SIZE, y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))

			if grid[y][x].f_cost() != float('inf'):
				text = font.render(str(round(grid[y][x].f_cost())), True, (255, 255, 255))
				text_rect = text.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
				screen.blit(text, text_rect)

			if grid[y][x].h_cost != float('inf'):
				text = small_font.render(str(round(grid[y][x].h_cost)), True, (255, 255, 255))
				text_rect = text.get_rect(topright=((x + 1) * TILE_SIZE - 5, y * TILE_SIZE + 5))
				screen.blit(text, text_rect)

			if grid[y][x].g_cost != float('inf'):
				text = small_font.render(str(grid[y][x].g_cost), True, (255, 255, 255))
				text_rect = text.get_rect(topleft=(x * TILE_SIZE + 5, y * TILE_SIZE + 5))
				screen.blit(text, text_rect)

	# for x in range(tile_width):
	# 	pygame.draw.line(screen, (30, 30, 30), (x * tile_size, 0), (x * tile_size, HEIGHT))
	# for y in range(tile_height):
	# 	pygame.draw.line(screen, (30, 30, 30), (0, y * tile_size), (WIDTH, y * tile_size))

	pygame.display.update()


def trace(end):
	draw()
	while end:
		pygame.draw.rect(screen, (50, 50, 200),
						 ((end.pos[0] * TILE_SIZE, end.pos[1] * TILE_SIZE), (TILE_SIZE, TILE_SIZE)))
		end = end.parent

	pygame.display.update()


def astar():
	current = min(open, key=lambda x: x.f_cost())
	open.remove(current)
	closed.append(current)
	if target[0] == current.pos[1] and target[1] == current.pos[0]:
		trace(current)
		while True:
			inp()

	for n in current.get_neighbors():
		if not grid[n[0]][n[1]] in closed and not grid[n[0]][n[1]].barrier:
			if grid[n[0]][n[1]].g_cost > current.g_cost + (10 if n[2] else 14):
				grid[n[0]][n[1]].g_cost = current.g_cost + (10 if n[2] else 14)
				grid[n[0]][n[1]].parent = current
			if not grid[n[0]][n[1]] in open:
				open.append(grid[n[0]][n[1]])
				grid[n[0]][n[1]].h_cost = heuristic(n, target)


def best_first_search():
	current = min(open, key=lambda x: x.h_cost)
	open.remove(current)
	closed.append(current)
	if target[0] == current.pos[1] and target[1] == current.pos[0]:
		trace(current)
		while True:
			inp()

	for n in current.get_neighbors():
		if not grid[n[0]][n[1]] in closed and not grid[n[0]][n[1]].barrier:
			if grid[n[0]][n[1]].g_cost > current.g_cost + (10 if n[2] else 14):
				grid[n[0]][n[1]].g_cost = current.g_cost + (10 if n[2] else 14)
		if not grid[n[0]][n[1]] in (open + closed) and not grid[n[0]][n[1]].barrier:
			open.append(grid[n[0]][n[1]])
			grid[n[0]][n[1]].parent = current
			grid[n[0]][n[1]].h_cost = heuristic(n, target)


while not inp():
	draw()

while open:
	astar()
	draw()
	inp()
	while not inp():
		draw()
	clock.tick(60)
