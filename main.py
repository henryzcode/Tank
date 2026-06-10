import pygame
import os
from entities import Tank, get_movement, get_matrix
import tkinter as tk
from tkinter import messagebox

os.environ['SDL_VIDEO_WINDOW_POS'] = "0, 0"
pygame.init()
msgbox = tk.Tk()
msgbox.withdraw()

error = False

screen_dimension = pygame.display.get_desktop_sizes()[0]
win = pygame.display.set_mode(screen_dimension, pygame.DOUBLEBUF | pygame.NOFRAME)

try:
    with open("1.tilemap", "r") as f:
        map_data = f.read().splitlines(True)
except FileNotFoundError as e:
    error = True
    messagebox.showerror("File not found!", f"{e}\n - This error is likely caused by missing game files or scripts, you can install the game again or contact the developer.")

if not error:
    assets = {
        "icon": pygame.image.load("assets/icon.png").convert(),
        "body": pygame.transform.scale_by(pygame.image.load("assets/body.png").convert_alpha(), (7, 7)),
        "barrel": pygame.transform.scale_by(pygame.image.load("assets/barrel.png").convert_alpha(), (5, 5)),
        "bullet": pygame.transform.scale_by(pygame.image.load("assets/bullet.png").convert_alpha(), (5, 3)),
        "firing": [
            pygame.transform.scale_by(pygame.image.load(f"assets/fire/fire{i}.png").convert_alpha(), (5, 5))
            for i in range(1, 11)
        ],
        "wall_tile": pygame.transform.scale(pygame.image.load("assets/wall.png").convert_alpha(), (30, 30))
    }

    pygame.display.set_caption("Tank", "Tank")
    pygame.display.set_icon(assets["icon"])

    clock = pygame.time.Clock()
    FPS = 120

    def valid_pos(pos):
        if pos.x < 0 or pos.y < 0 or pos.x > screen_dimension[0] or pos.y > screen_dimension[1]:
            return False
        return True

    p1_controls = {
        "forward": pygame.K_w,
        "backward": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "barrel_left": pygame.K_q,
        "barrel_right": pygame.K_e,
        "shoot": pygame.K_LSHIFT,
    }

    p2_controls = {
        "forward": pygame.K_i,
        "backward": pygame.K_k,
        "left": pygame.K_j,
        "right": pygame.K_l,
        "barrel_left": pygame.K_u,
        "barrel_right": pygame.K_o,
        "shoot": pygame.K_SEMICOLON,
    }

    tanks = [
        Tank(pos=(100, 100), assets=assets, controls=p1_controls), 
        Tank(pos=[screen_dimension[0] - 150, screen_dimension[1] - 150], assets=assets, controls=p2_controls) 
    ]

    font = pygame.font.Font("assets/pixel.ttf", 30)

    bullets = []
    run = True

    tile_rects = []
    map_matrix = get_matrix("1.tilemap")

    def render_txt(surf, font:pygame.font.Font, txt, pos, color="#000000"):
        rendered = font.render(txt, True, color)
        surf.blit(rendered, pos)

    for i in map_matrix:
        pos = (i[1][0] * 30, i[1][1] * 30)
        rect = pygame.rect.Rect(pos[0], pos[1], 30, 30)
        tile_rects.append(rect)

    txt_offset = pygame.Vector2(30, -60)

    def show_hp(surf, tanks_list, font):
        inner_o = pygame.Vector2(3, 3)
        positions = [
            pygame.Vector2(120, 20), 
            pygame.Vector2(screen_dimension[0] - 200, 20)
        ]
        
        for i, tank in enumerate(tanks_list):
            pos = positions[i]
            if not tank.is_dead:
                hp_percentage = int((tank.hp / tank.max_hp) * 100)
                render_txt(surf, font, f"Player {i+1}              {hp_percentage}%", pos - pygame.Vector2(110, 3))
            else:
                render_txt(surf, font, f"Player {i+1}              dead", pos - pygame.Vector2(110, 3))
            
            pygame.draw.rect(surf, "#2f2f2f", (pos.x, pos.y, 100, 20))
            pygame.draw.rect(surf, "#dfdfdf", (pos.x + inner_o.x, pos.y + inner_o.y, 94, 14))
            
            if not tank.is_dead and tank.hp > 0:
                hp_width = (tank.hp / tank.max_hp) * 94
                pygame.draw.rect(surf, "#ff0000", (pos.x + inner_o.x, pos.y + inner_o.y, hp_width, 14))

    while run and not error:
        clock.tick(FPS)
        current = pygame.time.get_ticks()
        
        win.fill("#ffffff")

        for i in map_matrix:
            pos = (i[1][0] * 30, i[1][1] * 30)
            win.blit(assets["wall_tile"], pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        keys = pygame.key.get_pressed()

        for b in bullets[:]:
            rotated = pygame.transform.rotate(assets["bullet"], b[1] + 90)
            bullet_rect = rotated.get_rect(center=b[0])
            for i in tile_rects:
                if bullet_rect.colliderect(i):
                    if b in bullets:
                        bullets.remove(b)
                    break

        for tank in tanks:
            if not tank.is_dead:
                tank.handle_input(keys, current, bullets, tanks, tile_rects)
                tank.update(current)
                tank.draw(win)
                tank.hit(bullets, tanks)
                render_txt(win, font, str(tank.get_loaded(current)), tank.pos + txt_offset)

        for b in bullets[:]:
            if valid_pos(b[0]):
                movement = get_movement(b[2], b[1])
                b[0] += movement
                rotated = pygame.transform.rotate(assets["bullet"], b[1] + 90)
                bullet_rect = rotated.get_rect(center=b[0])
                win.blit(rotated, bullet_rect.topleft)
            else:
                if b in bullets:
                    bullets.remove(b)

        show_hp(win, tanks, font)
                    
        pygame.display.flip()

pygame.quit()