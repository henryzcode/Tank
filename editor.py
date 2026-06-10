import pygame
import json

pygame.init()

screen_dim = pygame.display.get_desktop_sizes()[0]
win = pygame.display.set_mode(screen_dim, pygame.DOUBLEBUF)
pygame.display.set_caption("Editor", "Editor")
cursor_img = pygame.image.load("assets/cursor.png").convert_alpha()
mid_point = (cursor_img.get_width() // 2, cursor_img.get_height() // 2)

tilemap_dir = "1.tilemap"

import os

matrix = []

if os.path.exists(tilemap_dir):
    with open(tilemap_dir, "r") as tilemap:
        try:
            matrix = json.load(tilemap)
        except json.JSONDecodeError:
            matrix = []
else:
    matrix = []

cursor = pygame.cursors.Cursor((0, 0), cursor_img)
pygame.mouse.set_cursor(cursor)

font = pygame.font.Font("assets/pixel.ttf", 40)
clock = pygame.time.Clock()

tile_size = 30
tiles = {
    0 : pygame.transform.scale(pygame.image.load("assets/wall.png"), (tile_size, tile_size))
}
def render_txt(font: pygame.font.Font, surf: pygame.surface.Surface, txt, color, x, y):
    texture = font.render(txt, True, color)
    surf.blit(texture, (x, y))

def get_grid_pos(mpos, g_size, offset):
    x = (mpos[0] - offset[0]) // g_size
    y = (mpos[1] - offset[1]) // g_size
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    return (x, y), (x*g_size + offset[0], y*g_size + offset[1])

running = True
mpos = []
grid_pos = []
current_tile = 0

SAVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SAVE_EVENT, 1500)

while running:
    mouse = pygame.mouse.get_pressed()
    mpos = pygame.mouse.get_pos()
    grid_pos, draw_pos = get_grid_pos(mpos, tile_size, (0,120))
    win.fill("#000000")
    tiles[current_tile].set_alpha(80)
    win.blit(tiles[current_tile], (25, 50))
    tiles[current_tile].set_alpha(90)
    win.blit(tiles[current_tile], draw_pos)
    pygame.draw.line(win, "#363636", (220, 10), (220, 110), 10)
    pygame.draw.line(win, "#363636", (0, 120), (screen_dim[0], 118), 5)
    render_txt(font, win, "Current tile: ", "#00ff00", 5, 5)
    render_txt(font, win, "Mouse pos: " + str(mpos), "#00ff00", 240, 10)
    render_txt(font, win, "Grid coordinate: " + str(grid_pos), "#00ff00", 240, 65)

    for i in matrix:
        tiles[i[0]].set_alpha(255)
        _draw_pos = (i[1][0]*30, i[1][1]* 30 + 120)
        win.blit(tiles[i[0]], _draw_pos)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if mouse[0]:
            matrix.append([current_tile, grid_pos])
        if mouse[2]:
            for i in matrix[:]:
                if grid_pos == tuple(i[1]):
                    matrix.remove(i)
        if event.type == SAVE_EVENT:
            with open(tilemap_dir, "w") as tilemap:
                json.dump(matrix, tilemap)
                tilemap.close()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()