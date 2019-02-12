import pygame
import random
import numpy as np
from numpy.linalg import norm
from enemy_detection import EnemyDetection


class Player(pygame.sprite.Sprite):
    # Static variables
    MAXSPEED = 100.0
    # Variable for loading player picture. Require module that import player.py to initialize this variable
    image = []
    # Dictionary
    players = {}
    # tag
    total_number = 0

    def __init__(self, start_pos=(50, 50), game_display=pygame.Surface, controlled_by_ai=False):
        pygame.sprite.Sprite.__init__(self, self.groups)
        # Save game display as a rectangular area object
        self.area = game_display.get_rect()  # where the sprite is allowed to move
        # Score variable for each player
        self.score = 0
        # Set flag if it's an AI controlling this player
        self.controlled_by_ai = controlled_by_ai
        # ---- Create variables for keeping track of sprite position ----
        self.x_pos = start_pos[0] * 1.0  # float
        self.y_pos = start_pos[1] * 1.0  # float
        self.step_size = self.auto_step_size()
        # Load normal image
        self.image = Player.image[0]
        self.mask = pygame.mask.from_surface(self.image)
        # ---- Create hitbox the size of the player image at it's starting location
        self.rect = self.image.get_rect(center=(round(self.x_pos), round(self.y_pos)))
#        self.radius = max(self.rect.width, self.rect.height) * 2.0
        # ---- Flag for Game Over
        self.remove = False
        # ---- Update static variables -----
        self.number = Player.total_number  # get my personal Enemy number
        Player.total_number += 1  # increase the number for next Enemy
        Player.players[self.number] = self  # store myself into the Enemy dictionary
        #  print("my number %i Player number %i " % (self.number, Player.number))

    def new_pos(self, pos):
        """
        Call this function to update position of player
        :param pos: Tuple
        :return:
        """
        self.x_pos = pos[0] * 1.0  # float
        self.y_pos = pos[1] * 1.0  # float
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)

    def kill(self):
        if self.controlled_by_ai:
            # Flag detection object to be removed
            self.detection.remove = True
        # Show Game Over image
        self.image = Player.image[1]
        # Remove player from dictionary
        Player.players[self.number] = None  # kill Player in sprite dictionary
        # Reduce total number of players by 1
        Player.total_number -= 1
        # Call super method to remove player
        pygame.sprite.Sprite.kill(self)

    def connect_ai(self, ai_mind):
        """
        Initialize a variables for neural network
        :param ai_input_size: Integer
        :param ai_mind: Neural network object
        :return: None
        """
        # Feed forward neural network
        self.ai_mind = ai_mind
        # Enemy detection object initialized
        colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
        self.detection = EnemyDetection(colour=colour, starting_pos=(self.x_pos, self.y_pos), size=6 * self.rect.width)

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

    def move_AI(self, step_size, ai_input):
        """AI decision to move"""
        ai_decision = self.ai_decision(ai_input)
        if ai_decision is not None:
            if ai_decision == 0:
                self.y_pos += step_size  # Move down
            elif ai_decision == 1:
                self.y_pos -= step_size  # Move up
            elif ai_decision == 2:
                self.x_pos += step_size  # Move right
            elif ai_decision == 3:
                self.x_pos -= step_size  # Move left
        # ---- Updated coordinates for player hitbox
        self.rect.centerx = round(self.x_pos, 0)
        self.rect.centery = round(self.y_pos, 0)

    def detect_collision(self, enemy):
        """
        Detect if the angle between the enemy velocity vector and the vector to

        Point 1 (p1) represent the player
        Point 2 (p2) represent the enemy
        :param enemy: Enemy object
        :return: +1 (true) if a collision will occur. Otherwise return -1 (false)
        """
        # Vector from enemy to player
        p2p1_vec = np.array([self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery])
        p2_vel_vec = np.array([enemy.vx, enemy.vy])
        # Norm of vectors
        p2p1_norm = norm(p2p1_vec)
        p2_vel_norm = norm(p2_vel_vec)
        # Angle between p2p1 vector and p2 velocity vector
        theta = np.arccos(np.dot(p2_vel_vec, p2p1_vec) / (p2_vel_norm * p2p1_norm))
        # Radius of Player and Enemy (Approximates both as circles)
        r1 = np.sqrt(self.rect.width * self.rect.width + self.rect.height * self.rect.height) / 2
        r2 = np.sqrt(enemy.rect.width * enemy.rect.width + enemy.rect.height * enemy.rect.height) / 2
        # Critical angle
        theta_c = np.arctan((r1 + r2) / p2p1_norm)
        if 0 < theta <= theta_c:
            return 1, (p2p1_norm - r1 - r2) / np.sqrt(self.area.width*self.area.width + self.area.height * self.area.height)
        else:
            return -1, (p2p1_norm - r1 - r2) / np.sqrt(self.area.width*self.area.width + self.area.height * self.area.height)

    def ai_decision(self, ai_input):
        """
        Create 1D array consisting of all player and enemy positions. Scaled by game windows width and height
        The first 2 entries are always the players x and y position
        :param ai_input: Object group
        :return: 1D numpy array [rect.centerx_1, rect.centery_1, ...]
        """
        # ------------------------------------ Calculate values ---------------------------------------------
        sprite_positions = np.zeros(ai_input[1],)  # 1D array of all x and y pos
        sprite_positions[0] = self.rect.centerx / self.area.width  # Distance from left wall
        sprite_positions[1] = self.rect.centery / self.area.height  # Distance from top wall
        for i, enemy in enumerate(ai_input[0]):
            # Collision: [-1, 1]. Distance: Float.
            collision, distance = self.detect_collision(enemy)
            sprite_positions[i + 1] = enemy.x_pos / self.area.width  # Normalized enemy x pos
            sprite_positions[i + 2] = enemy.y_pos / self.area.height  # Normalized enemy y pos
            sprite_positions[i + 3] = 1 / distance  # Normalized distance between enemy and player
            sprite_positions[i + 4] = collision  # +1 (true) or -1 (false)
        sprite_positions.shape = (1, -1)
        # ---------------------------------------------------------------------------------------------------
        return self.ai_mind.get_predict(sprite_positions, classify=True)[0]

    def update(self, time_alive, ai_input=None):
        """
        Function called when
        :param time_alive: Argument must be provided when pygame.sprite.Group.update(*args) is called on this group
        This parameter represents the time passed since the last call to update()
        :param ai_input: Tuple of object and integer (ai_input, ai_input_size)
        :return: None
        """
        # -- Check if Game Over --
        if self.remove:
            self.image = Player.image[1]
            self.kill()  # Game over
        # -- Move player --
        if self.controlled_by_ai:
            self.move_AI(self.step_size, ai_input)
            # ---- Updated coordinates for detection object
            self.detection.rect.center = (self.rect.centerx, self.rect.centery)
        else:
            self.move(self.step_size)
        # Set image
        self.image = Player.image[0]
        # -- check if out of screen --
        if not self.area.contains(self.rect):
            self.image = Player.image[2]  # crash into wall (red boarder)
            # --- compare self.rect and area.rect
            if (self.x_pos + self.rect.width / 2) > self.area.right:
                self.x_pos = self.area.right - self.rect.width / 2
            if (self.x_pos - self.rect.width / 2) < self.area.left:
                self.x_pos = self.area.left + self.rect.width / 2
            if (self.y_pos + self.rect.height / 2) > self.area.bottom:
                self.y_pos = self.area.bottom - self.rect.height / 2
            if (self.y_pos - self.rect.height / 2) < self.area.top:
                self.y_pos = self.area.top + self.rect.height / 2
        # -- Update score (i.e time alive) --
        self.score += time_alive

if __name__ == '__main__':
    pygame.init()
