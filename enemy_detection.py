import pygame


class EnemyDetection(pygame.sprite.Sprite):
    devices = {}
    total_number = 0

    def __init__(self, colour, starting_pos, size):
        """
        Constructor
        :param colour: tuple of RGB values
        :param starting_pos: Where to draw image and create hitbox
        :param size: [width, height] of area to draw circle on
        """
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.colour_circle = colour  # Colour of detector
        init_x_pos, init_y_pos = round(starting_pos[0]), round(starting_pos[1])
        self.radius = round(size)  # for collide check
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius))  # created surface object (default color BLACK)
        self.image.set_colorkey((0, 0, 0))  # Any pixels matching the colorkey will not be drawn(i.e BLACK in this case)
        image_width, image_height = self.image.get_size()  # (width, height) of surface object
        x_center, y_center = round(image_width / 2), round(image_height / 2)  # Center position of surface object
        pygame.draw.circle(self.image, self.colour_circle, (x_center, y_center), self.radius, 2)  # red circle
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect(center=(init_x_pos, init_y_pos))
        self.remove = False
        self.number = EnemyDetection.total_number  # get my personal Enemy number
        EnemyDetection.total_number += 1  # increase the number for next Enemy
        EnemyDetection.devices[self.number] = self  # store myself into the Enemy dictionary

    def kill(self):
        # Remove object from dictionary
        EnemyDetection.devices[self.number] = None  # kill object in sprite dictionary
        # Reduce total number of active devices by 1
        EnemyDetection.total_number -= 1
        # Call super method to remove object
        pygame.sprite.Sprite.kill(self)

    def update(self):
        # -- Check if Game Over --
        if self.remove:
            self.kill()  # Game over
