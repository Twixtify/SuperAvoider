import random
import pygame
from numpy import sqrt


class Enemy(pygame.sprite.Sprite):
    # ---- Static variables ----
    # Max speed
    ENEMYMAXSPEED = 100.0
    # Variable for loading enemy picture in. Require module which import Enemy to initialize this variable
    image = []
    # Dictionary over all enemies
    enemies = {}
    # Number of bird
    number = 0

    def __init__(self, start_pos=(50, 50), game_display=pygame.Surface):
        pygame.sprite.Sprite.__init__(self, self.groups)
        # Save game display as a rectangular area object
        self.area = game_display.get_rect()  # where the sprite is allowed to move
        # ---- Create variables for keeping track of sprite position ----
        self.x_pos = start_pos[0] * 1.0  # float
        self.y_pos = start_pos[1] * 1.0  # float
        self.speed_max = self.step_size()
        # Load normal image
        self.image = Enemy.image[0]
        self.mask = pygame.mask.from_surface(self.image)
        # Save image size as a rectangular area object
        self.rect = self.image.get_rect(center=(round(self.x_pos), round(self.y_pos)))
        # ---- Flag for Game Over
        self.vx = random.choice([-1, 1]) * random.random() * self.step_size()
        self.vy = random.choice([-1, 1]) * sqrt(self.step_size()*self.step_size() - self.vx*self.vx)
        self.detected = False
        # ---- Update static variables -----
        self.number = Enemy.number  # get my personal Enemy number
        Enemy.number += 1  # increase the number for next Enemy
        Enemy.enemies[self.number] = self  # store myself into the Enemy dictionary
        #  print("my number %i Enemy number %i " % (self.number, Enemy.number))

    def step_size(self):
        """
        Return automatic step size
        :return:
        """
        return 600 * max(round(self.area.width / self.area.height), round(self.area.height / self.area.width))

    def new_pos(self, pos):
        """
        Call this function to update position of enemy
        :param pos: Tuple
        :return:
        """
        self.x_pos = pos[0] * 1.0  # float
        self.y_pos = pos[1] * 1.0  # float
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)

    def new_speed(self, bounce, method="uniform"):
        """
        Calculate the new speed of Enemy sprite. Will not be 0.
        :param bounce: Integer, to know which wall sprite hit
        :param method: String
        :return:
        """
        random_direction = random.choice([-1, 1])  # +1 or -1
        if method is "uniform":
            self.vx = random_direction * random.random() * self.speed_max + random_direction
            self.vy = random_direction * random.random() * self.speed_max + random_direction
        elif method is "constant":
            if bounce == 0 or bounce == 1:
                self.vy *= -1
            if bounce == 2 or bounce == 3:
                self.vx *= -1
        elif method is "gauss":
            self.vx = random_direction * random.gauss(0, 1) * self.speed_max + random_direction
            self.vy = random_direction * random.gauss(0, 1) * self.speed_max + random_direction

    def update(self, seconds_passed):
        """
        Function called when
        :param seconds_passed: Argument must be provided when pygame.sprite.Group.update(*args) is called on enemy group
        This parameter represents the time passed since the last call to update()
        :return: None
        """
        # Move enemy to new position since last call: distance = speed * time
        self.x_pos += self.vx * seconds_passed
        self.y_pos += self.vy * seconds_passed
        # ---- Updated coordinates for sprite hitbox
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)
        # Set image of enemy
        self.image = Enemy.image[0]
        # -- check if out of screen
        if not self.area.contains(self.rect):
            self.image = Enemy.image[1]  # crash into wall
            bounce = None  # Bounce in opposite direction
            # --- compare self.rect and area.rect
            if (self.y_pos + self.rect.height / 2) > self.area.bottom:  # Bottom wall
                self.y_pos = self.area.bottom - self.rect.height / 2
                bounce = 0
            if (self.y_pos - self.rect.height / 2) < self.area.top:  # Top wall
                self.y_pos = self.area.top + self.rect.height / 2
                bounce = 1
            if (self.x_pos + self.rect.width / 2) > self.area.right:  # Right wall
                self.x_pos = self.area.right - self.rect.width / 2
                bounce = 2
            if (self.x_pos - self.rect.width / 2) < self.area.left:  # Left wall
                self.x_pos = self.area.left + self.rect.width / 2
                bounce = 3
            self.new_speed(bounce, "constant")  # calculate a new speed
        else:
            if self.detected:
                self.image = Enemy.image[2]  # blue rectangle
            else:
                self.image = Enemy.image[0]  # normal bird image

if __name__ == '__main__':
    pygame.init()
