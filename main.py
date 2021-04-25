import pygame
import os

pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 800
ICON_IMG = pygame.image.load(os.path.join("imgs", "icon.png"))
COLOURS = {0: (255, 255, 255), 1: (0, 0, 0)}

pygame.display.set_caption("Conway's Game of Life")
pygame.display.set_icon(ICON_IMG)
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


class Grid:

    def __init__(self, width, height):
        self.grid = [0] * (width * height)
        self.width = width
        self.height = height
        self.active_cells = []
        self.active = False

    def simulate(self):
        if not self.active:
            return
        to_die = []
        to_live = []
        for cell in self.active_cells:
            n = self.get_neighbours(cell) 
            s = sum([ self.grid[i] for i in n ])
            if s < 2 or s > 3:
                to_die.append(cell)
            for dead_cell in [ x for x in n if self.grid[x] == 0 ]:
                if sum([ self.grid[i] for i in self.get_neighbours(dead_cell) ]) == 3:
                    to_live.append(dead_cell)
        for cell in to_die:
            self.set_cell(cell, 0)
        for cell in to_live:
            self.set_cell(cell, 1)

    def toggle_active(self):
        self.active = not self.active

    def get_index(self, pos, zoom, x_offset, y_offset):
        return int(((x_offset / zoom) + (pos[0] / zoom)) // 1) + (self.width * (int(((y_offset / zoom) + (pos[1] / zoom)))))

    def set_cell(self, index, value):
        self.grid[index] = value
        if value == 1 and index not in self.active_cells:
            self.active_cells.append(index)
        elif value == 0 and index in self.active_cells:
            self.active_cells.remove(index)

    def get_neighbours(self, index):
        pos = (index % self.width, index // self.width)
        neighbours = [ x + (y * self.width) for x in range(pos[0] - 1, pos[0] + 2) for y in range(pos[1] - 1, pos[1] + 2) if (x, y) != pos and x >= 0 and y >= 0 and x < self.width and y < self.height]
        return neighbours

    def display_grid(self, win, x_offset, y_offset, resolution):
        for x in range(int(x_offset // zoom), min(int(x_offset // zoom) + int(WIN_WIDTH // zoom) + 2, self.width)):
            for y in range(int(y_offset // zoom), min(int(y_offset // zoom) + int(WIN_HEIGHT // zoom) + 2, self.height)):
                clamp = [0, 0]
                if (x * resolution) + (resolution / 25) - x_offset < 0:
                    clamp[0] = 1
                if (y * resolution) + (resolution / 25) - y_offset < 0:
                    clamp[1] = 1
                pygame.draw.rect(win, COLOURS[self.grid[x + (y * self.width)]],
                                 ((x * resolution) + (resolution / 25) - x_offset,
                                  (y * resolution) + (resolution / 25) - y_offset,
                                  resolution - (resolution / 25) - clamp[0], 
                                  resolution - (resolution / 25) - clamp[1]))


running = True
grid = Grid(1000, 300)

x_offset, y_offset = 0, 0
moving_screen = False
drawing = -1
clock = pygame.time.Clock()

min_size = 25
max_size = min(WIN_WIDTH, WIN_HEIGHT) / 100
zoom = max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size)

frame = 0
sim_speed = 10

while running:

    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEMOTION and moving_screen:    # MOVING SCREEN WITH MIDDLE MOUSE BUTTON
            movement = pygame.mouse.get_rel()
            if zoom * (grid.width - (WIN_WIDTH / zoom)) > x_offset - movement[0] > 0:
                x_offset -= movement[0]
            elif x_offset - movement[0] > zoom * (grid.width - (WIN_WIDTH / zoom)):
                x_offset = zoom * (grid.width - (WIN_WIDTH / zoom))
            elif 0 > x_offset - movement[0]:
                x_offset = 0
            if zoom * (grid.height - (WIN_HEIGHT / zoom)) > y_offset - movement[1] > 0:
                y_offset -= movement[1]
            elif y_offset - movement[1] > zoom * (grid.height - (WIN_WIDTH / zoom)):
                y_offset = zoom * (grid.height - (WIN_WIDTH / zoom))
            elif 0 > y_offset - movement[1]:
                y_offset = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:  # ZOOM FUNCTION WITH MOUSE WHEEL
            if event.button == 4:   # ZOOM IN
                if zoom + int(zoom / (max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size))) < (min(WIN_WIDTH, WIN_HEIGHT) / min_size):
                    zoom += int(zoom / (max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size)))
                else:
                    zoom = min(WIN_WIDTH, WIN_HEIGHT) / min_size
            elif event.button == 5:     # ZOOM OUT
                if zoom - int(zoom / (max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size))) > max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size):
                    zoom -= int(zoom / (max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size)))
                    x_offset = min(zoom * (grid.width - (WIN_WIDTH / zoom)), x_offset)
                    y_offset = min(zoom * (grid.width - (WIN_WIDTH / zoom)), y_offset)
                else:
                    zoom = max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size)
                    x_offset = zoom * (grid.width - (WIN_WIDTH / zoom))
                    y_offset = zoom * (grid.width - (WIN_WIDTH / zoom))
            elif event.button == 2:
                moving_screen = True
                pygame.mouse.get_rel()
            elif event.button == 1:
                drawing = 1
            elif event.button == 3:
                drawing = 0
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                moving_screen = False
            elif event.button == 1 or event.button == 3:
                drawing = -1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                grid.toggle_active()
            elif event.key == pygame.K_r:
                x_offset, y_offset = 0, 0
                zoom = max(min(WIN_WIDTH, WIN_HEIGHT) / grid.width, max_size)
                grid = None
                grid = Grid(1000, 300)
        
    if drawing >= 0:
        grid.set_cell(grid.get_index(pygame.mouse.get_pos(), zoom, x_offset, y_offset), drawing)

    frame += 1

    screen.fill((100, 100, 100))
    
    if frame % sim_speed == 0:
        frame = 0
        grid.simulate()

    grid.display_grid(screen, x_offset, y_offset, zoom)
    pygame.display.update()
