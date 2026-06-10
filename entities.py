import pygame
import math
import json

def get_movement(velocity, angle):
    rad = math.radians(angle + 90)
    x = math.cos(rad) * velocity
    y = -math.sin(rad) * velocity
    return pygame.Vector2(x, y)

def blit_rotate_around_pivot(surface, image, top_left, pivot_offset, angle):
    image_rect = image.get_rect(topleft=top_left)
    pivot_pos = pygame.Vector2(top_left) + pivot_offset
    offset_center_to_pivot = pivot_pos - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_center = pivot_pos - rotated_offset
    rotated_rect = rotated_image.get_rect(center=rotated_image_center)
    surface.blit(rotated_image, rotated_rect.topleft)

def barrel_head_pos(tank_pos: pygame.Vector2, theta_degrees, barrel_len: int):
    theta_radians = math.radians(theta_degrees + 90)
    x = tank_pos.x + math.cos(theta_radians) * barrel_len
    y = tank_pos.y - math.sin(theta_radians) * barrel_len
    return pygame.Vector2(x, y)

def get_matrix(fp):
    with open(fp, "r") as tilemap:
        matrix = json.loads(tilemap.read())
    return matrix

class Tank:
    def __init__(self, pos, assets, controls=None):
        self.pos = pygame.Vector2(pos)
        self.assets = assets
        self.max_hp = 30
        self.hp = self.max_hp
        self.is_dead = False

        self.controls = controls if controls else {
            "forward": pygame.K_w,
            "backward": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "barrel_left": pygame.K_q,
            "barrel_right": pygame.K_e,
            "shoot": pygame.K_x
        }
        
        self.tank_angle = 0
        self.barrel_angle = 0
        self.barrel_offset = pygame.Vector2(35, -40)
        self.pivot_point_inside_barrel = pygame.Vector2(35, 110)
        
        self.firing = False
        self.fire_anim_speed = 8
        self.fire_frame = 0
        self.last_fire_frame = 0
        self.shot_time = 0
        self.cd = 100
        self.bullet_velocity = 20

    def get_loaded(self, current_time):
        loaded = False
        if current_time - self.shot_time >= self.cd:
            loaded = "Loaded"
        else:
            loaded = f"Loading: {str((self.cd - (current_time - self.shot_time))/1000)}s"
        return loaded

    def handle_input(self, keys, current_time, bullets_list, other, tiles):
        if keys[self.controls["left"]]:
            self.tank_angle += 0.75
            self.barrel_angle += 0.75
            if self.collision(other, tiles):
                self.tank_angle -= 0.75
                self.barrel_angle -= 0.75
                
        if keys[self.controls["right"]]:
            self.tank_angle -= 0.75
            self.barrel_angle -= 0.75
            if self.collision(other, tiles):
                self.tank_angle += 0.75
                self.barrel_angle += 0.75
                
        if keys[self.controls["forward"]]:
            self.pos += get_movement(2.5, self.tank_angle)
            if self.collision(other, tiles):
                self.pos -= get_movement(2.5, self.tank_angle)
                
        if keys[self.controls["backward"]]:
            self.pos -= get_movement(2.5, self.tank_angle)
            if self.collision(other, tiles):
                self.pos += get_movement(2.5, self.tank_angle)
        
        if keys[self.controls["barrel_right"]]:
            self.barrel_angle -= 1
            
        if keys[self.controls["barrel_left"]]:
            self.barrel_angle += 1
            
        if keys[self.controls["shoot"]] and current_time - self.shot_time >= self.cd:
            self.shoot(current_time, bullets_list)

    def shoot(self, current_time, bullets_list):
        self.shot_time = current_time
        spawn_point = barrel_head_pos(
            self.pos + self.barrel_offset + self.pivot_point_inside_barrel, 
            self.barrel_angle, 
            115
        )
        bullets_list.append([pygame.Vector2(spawn_point), self.barrel_angle, self.bullet_velocity, self])
        
        self.firing = True
        self.fire_frame = 0
        self.last_fire_frame = current_time

    def update(self, current_time):
        if self.firing:
            if current_time - self.last_fire_frame > self.fire_anim_speed:
                self.fire_frame += 1
                self.last_fire_frame = current_time
                
                if self.fire_frame >= len(self.assets["firing"]):
                    self.firing = False
                    self.fire_frame = 0

    def draw(self, surface):
        barrel_top_left = self.pos + self.barrel_offset
        
        if self.firing:
            current_barrel_image = self.assets["firing"][self.fire_frame]
        else:
            current_barrel_image = self.assets["barrel"]
            
        blit_rotate_around_pivot(
            surface, self.assets["body"], self.pos, 
            self.pivot_point_inside_barrel + self.barrel_offset, self.tank_angle
        )
        blit_rotate_around_pivot(
            surface, current_barrel_image, barrel_top_left, 
            self.pivot_point_inside_barrel, self.barrel_angle
        )
    
    def get_body_mask_and_rect(self):
        image = self.assets["body"]
        pivot_offset = self.pivot_point_inside_barrel + self.barrel_offset
        
        image_rect = image.get_rect(topleft=self.pos)
        pivot_pos = pygame.Vector2(self.pos) + pivot_offset
        offset_center_to_pivot = pivot_pos - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-self.tank_angle)
        
        rotated_image = pygame.transform.rotate(image, self.tank_angle)
        rotated_image_center = pivot_pos - rotated_offset
        rotated_rect = rotated_image.get_rect(center=rotated_image_center)

        mask = pygame.mask.from_surface(rotated_image)
        
        return mask, rotated_rect

    def body_rect(self):
        image = self.assets["body"]
        pivot_offset = self.pivot_point_inside_barrel + self.barrel_offset
    
        image_rect = image.get_rect(topleft=self.pos)
        pivot_pos = pygame.Vector2(self.pos) + pivot_offset
        offset_center_to_pivot = pivot_pos - image_rect.center
        
        rotated_offset = offset_center_to_pivot.rotate(-self.tank_angle)
        rotated_image = pygame.transform.rotate(image, self.tank_angle)
        rotated_image_center = pivot_pos - rotated_offset
        
        return rotated_image.get_rect(center=rotated_image_center)

    def bullet_rect(self, bullets):
        rect = []
        for projectile in bullets:
            rect.append(self.assets["bullet"].get_rect(topleft=projectile[0]))
        return rect

    def collision(self, other_tanks, tiles):
        my_mask, my_rect = self.get_body_mask_and_rect()
        
        for tank in other_tanks:
            if tank is self or tank.is_dead:
                continue
                
            other_mask, other_rect = tank.get_body_mask_and_rect()

            if my_rect.colliderect(other_rect):
                offset = (other_rect.x - my_rect.x, other_rect.y - my_rect.y)
                if my_mask.overlap(other_mask, offset):
                    return True
                    
        tile_mask = pygame.mask.from_surface(self.assets["wall_tile"])
        for tile_rect in tiles:
            if my_rect.colliderect(tile_rect):
                offset = (tile_rect.x - my_rect.x, tile_rect.y - my_rect.y)
                if my_mask.overlap(tile_mask, offset):
                    return True
        return False
    
    def hit(self, bullets, all_tanks):
        if self.is_dead:
            return False

        my_mask, my_rect = self.get_body_mask_and_rect()
        
        for b in bullets[:]:
            if len(b) > 3 and b[3] is self:
                continue

            bullet_img = pygame.transform.rotate(self.assets["bullet"], b[1] + 90)
            bullet_rect = bullet_img.get_rect(center=b[0])

            if my_rect.colliderect(bullet_rect):
                bullet_mask = pygame.mask.from_surface(bullet_img)
                offset = (bullet_rect.x - my_rect.x, bullet_rect.y - my_rect.y)
                
                if my_mask.overlap(bullet_mask, offset):
                    if b in bullets:
                        bullets.remove(b)
                    
                    self.hp -= 1
                    if self.hp <= 0:
                        self.is_dead = True
                        
                    return True 
                    
        return False