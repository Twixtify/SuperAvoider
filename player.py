import pygame


class Player(pygame.sprite.Sprite):
    # Static variables
    MAXSPEED = 100.0
    # Variable for loading player picture. Require module that import player.py to initialize this variable
    image = []
    # Dictionary
    players = {}
    # tag
    total_number = 0

    def __init__(self, start_pos=(50, 50), game_display=pygame.Surface):
        pygame.sprite.Sprite.__init__(self, self.groups)
        # Save game display as a rectangular area object
        self.area = game_display.get_rect()  # where the sprite is allowed to move
        # ---- Create variables for keeping track of sprite position ----
        self.x_pos = start_pos[0] * 1.0  # float
        self.y_pos = start_pos[1] * 1.0  # float
        self.step_size = self.auto_step_size()
        # Load normal image
        self.image = Player.image[0]
        self.mask = pygame.mask.from_surface(self.image)
        # ---- Create hitbox the size of the player image at it's starting location
        self.rect = self.image.get_rect(center=(round(self.x_pos), round(self.y_pos)))
        # ---- Flag for Game Over
        self.remove = False
        # ---- Update static variables -----
        self.number = Player.total_number  # get my personal Enemy number
        Player.total_number += 1  # increase the number for next Enemy
        Player.players[self.number] = self  # store myself into the Enemy dictionary
        #  print("my number %i Player number %i " % (self.number, Player.number))

    def new_pos(self, pos):
        """
        Call this function to update position
        :param pos: Tuple
        :return:
        """
        self.x_pos = pos[0] * 1.0  # float
        self.y_pos = pos[1] * 1.0  # float
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)

    def kill(self):
        # Show Game Over image
        self.image = Player.image[4]
        # Remove player from dictionary
        Player.players[self.number] = None  # kill Player in sprite dictionary
        # Reduce total number of players by 1
        Player.total_number -= 1
        # Call super method to remove player
        pygame.sprite.Sprite.kill(self)

    def auto_step_size(self):
        """
        Return automatic step size
        :return:
        """
        return 8 * max(round(self.area.width / self.area.height), round(self.area.height / self.area.width))

    def move(self, step_size=10):
        """ Handles Keys """
        key = pygame.key.get_pressed()
        # distance moved in 1 frame, try changing it
        if key[pygame.K_DOWN] or key[pygame.K_s]:  # down key
            self.y_pos += step_size  # move down
        elif key[pygame.K_UP] or key[pygame.K_w]:  # up key
            self.y_pos -= step_size  # move up
        if key[pygame.K_RIGHT] or key[pygame.K_d]:  # right key
            self.x_pos += step_size  # move right
        elif key[pygame.K_LEFT] or key[pygame.K_a]:  # left key
            self.x_pos -= step_size  # move left
        # ---- Updated coordinates for player hitbox
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)

    def out_of_bound(self, contain=True, dangerous=False):
        # -- check if out of screen --
        if contain is True and dangerous is False:
            if not self.area.contains(self.rect):
                    self.image = Player.image[4]  # crash into wall (red boarder)
                # --- compare self.rect and area.rect
                    if (self.x_pos + self.rect.width / 2) > self.area.right:
                        self.x_pos = self.area.right - self.rect.width / 2
                    if (self.x_pos - self.rect.width / 2) < self.area.left:
                        self.x_pos = self.area.left + self.rect.width / 2
                    if (self.y_pos + self.rect.height / 2) > self.area.bottom:
                        self.y_pos = self.area.bottom - self.rect.height / 2
                    if (self.y_pos - self.rect.height / 2) < self.area.top:
                        self.y_pos = self.area.top + self.rect.height / 2
        elif contain is False and dangerous is False:
            if (self.y_pos - self.rect.height / 2) < self.area.top:  # From top to bottom
                self.y_pos = self.area.bottom - self.rect.height / 2
            if (self.x_pos + self.rect.width / 2) > self.area.right:  # From right to left
                self.x_pos = self.area.left + self.rect.width / 2
            if (self.y_pos + self.rect.height / 2) > self.area.bottom:  # From bottom to top
                self.y_pos = self.area.top + self.rect.height / 2
            if (self.x_pos - self.rect.width / 2) < self.area.left:  # From left to right
                self.x_pos = self.area.right - self.rect.width / 2
        elif not self.area.contains(self.rect):
            self.remove = True

    def update(self, time_alive, *args):
        """
        Function called when
        :param time_alive: Argument must be provided when pygame.sprite.Group.update(*args) is called on this group
        This parameter represents the time passed since the last call to update()
        :param ai_input: So all_sprites_group can be used to update sprites
        :return: None
        """
        # Reset image
        self.image = Player.image[0]
        # -- Check if Game Over --
        if self.remove:
            self.kill()  # Game over
        # -- Move player --
        self.move(self.step_size)
        # Boundary condition
        self.out_of_bound(dangerous=True)


if __name__ == '__main__':
    pygame.init()
