import os
import time
import pygame
import random
import numpy as np
from enemy import Enemy
from player import Player
from enemy_detection import EnemyDetection
from super_avoider_AI import SuperAvoiderAI


class SuperAvoider:
    """
    Main class
    """
    # ---- Static variables ----
    # Center window on screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    # Initialize pygame
    pygame.init()
    # ---- Image Path and Game Icon ----
    # Path to file directory
    file_path = os.path.dirname(os.path.abspath(__file__))
    # Path to image directory
    image_path = os.path.join(file_path, "Images")
    # Set icon of window
    icon_path = os.path.join(image_path, "player.png")#"babytux.png")
    try:
        pygame.display.set_icon(pygame.image.load(icon_path))
    except:
        raise (UserWarning, "Could not find icon in", icon_path)

    def __init__(self):
        # ---- Define some colors ----
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.FPS = 60
        # ---- Load Images ----
        self.init_sprite_images()
        # ---- Set the background ----
        size = self.W_WIDTH, self.W_HEIGHT = (800, 600)
        self.screen = pygame.display.set_mode(size)  # Create window which graphics are rendered on
        self.background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))  # Surface which graphic
        # objects are drawn on and then pushed to the screen to render
        colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
        self.background.fill(colour)  # Background colour
        self.background.blit(self.write("Press ESC or Q to quit"), (5, 10))
        self.background.blit(self.write("Press P to (un)pause"), (self.W_WIDTH - 225, 10))
        self.background.convert()
        self.screen.blit(self.background, (0, 0))
        # Make images suitable for quick blitting, i.e drawn quickly on screen
        for i, _ in enumerate(Enemy.image):
            Enemy.image[i] = Enemy.image[i].convert_alpha()
        for i, _ in enumerate(Player.image):
            Player.image[i] = Player.image[i].convert_alpha()
        # ---- Start the game ----
        self.start_game()

    def write(self, msg="pygame is cool", style=None, size=32, colour=(0, 0, 0)):
        myfont = pygame.font.SysFont(style, size)
        mytext = myfont.render(msg, True, colour)  # Surface object
        mytext = mytext.convert_alpha()
        return mytext

    def init_sprite_images(self):
        """
        Method to load the enemy and player images that will be displayed on the screen
        :return:
        """
        try:
            Enemy.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "babytux.png")))
            Enemy.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "babytux_neg.png")))
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player.png")))
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player_dead.png")))
        except:
            raise (UserWarning, "Unable to find image in folder:", os.getcwd())
        Enemy.image.append(Enemy.image[0].copy())  # copy of first image
        Player.image.append(Player.image[0].copy())
        # rect(Surface, color, Rect, width=0) -> Rect
        # Draws a rectangular shape on the Surface. The given Rect is the area of the rectangle.
        # The width argument is the thickness to draw the outer edge.
        # If width is zero then the rectangle will be filled.
        pygame.draw.rect(Enemy.image[2], self.BLUE, (0, 0, 32, 36), 1)  # Draw blue border around image[2]
        pygame.draw.rect(Player.image[2], self.RED, (0, 0, 32, 32), 1)  # Draw red border around image[2]
        # print(Player.image[0].get_size())

    def spawn_enemies(self, pop=1):
        """
        Creates pop number of enemies
        Enemies spawn in the 1st quadrant of the game display
        :param pop: population
        :return:
        """
        for enemy in range(pop):
            # Draw positions from top left corner
            pos = (random.random() * self.W_WIDTH / 2, random.random() * self.W_HEIGHT / 2)
            Enemy(pos, self.background)

    def spawn_player(self):
        """
        Spawn player on the board
        Players spawn in the 4th quadrant of the game display
        :return:
        """
        colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
        pos = (self.W_WIDTH / 2 + random.random() * self.W_WIDTH / 2,
               self.W_HEIGHT / 2 + random.random() * self.W_HEIGHT / 2)
        player = Player(start_pos=pos, game_display=self.background)
        EnemyDetection(colour=colour, starting_pos=pos, size=5 * player.rect.width)
        return player

    def respown(self):
        colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
        pos = (random.random() * self.W_WIDTH, random.random() * self.W_HEIGHT)
        p1 = Player(start_pos=pos, game_display=self.background)
        EnemyDetection(colour=colour, starting_pos=pos, size=5 * p1.rect.width)

    def event_handle(self):
        for event in pygame.event.get():  # loop through all events that happened on the screen
            if event.type == pygame.QUIT:
                self.mainloop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.mainloop = False
                if event.key == pygame.K_r:
                    self.respown()
                if event.key == pygame.K_p:
                    self.pause()

    def pause(self):
        pause_text_surf = self.write("Paused", style="None", size=115)
        pause_text_rect = pause_text_surf.get_rect()
        pause_text_rect.center = ((round(self.W_WIDTH / 2)), (round(self.W_HEIGHT / 2)))
        self.screen.blit(pause_text_surf, pause_text_rect)
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        self.mainloop = False
                        paused = False
            # Update/draw game display
            pygame.display.flip()
            # Update only 5 times per second
            self.clock.tick(5)
        self.screen.blit(self.background, (0, 0))

    def make_sprite_groups(self):
        # assign default groups to each sprite class
        self.all_sprites_group = pygame.sprite.LayeredUpdates()  # All sprites in this group
        self.player_group = pygame.sprite.LayeredUpdates()
        self.enemy_group = pygame.sprite.LayeredUpdates()
        self.detection_group = pygame.sprite.LayeredUpdates()
        # ---- Assign Layer for each group (all_sprites_group default layer 0)
        self.detection_group._default_layer = 3
        self.player_group._default_layer = 2
        self.enemy_group._default_layer = 1
        # ---- Enemy group
        Enemy.groups = self.enemy_group, self.all_sprites_group
        # ---- Player group
        Player.groups = self.player_group, self.all_sprites_group
        EnemyDetection.groups = self.detection_group, self.all_sprites_group

    def AI_input(self, player, enemy_group=None):
        """
        Create 1D array consisting of all player and enemy positions. Scaled by game windows width and height
        The first 2 entries are always the players x and y position
        :param player:
        :param enemy_group:
        :return: 1D numpy array [rect.centerx_1, rect.centery_1, ...]
        """
        sprite_positions = np.zeros((self.input_size,))  # 1D array of all x and y pos
        sprite_positions[0] = player.rect.centerx / self.W_WIDTH
        sprite_positions[1] = player.rect.centery / self.W_HEIGHT
        if enemy_group is not None:
            for i, enemy in enumerate(enemy_group):
                sprite_positions[i + 1] = enemy.rect.centerx / self.W_WIDTH
                sprite_positions[i + 2] = enemy.rect.centery / self.W_HEIGHT
            sprite_positions.shape = (1, -1)
            return sprite_positions
        else:
            for i, enemy in enumerate(self.enemy_group):
                sprite_positions[i + 1] = enemy.rect.centerx / self.W_WIDTH
                sprite_positions[i + 2] = enemy.rect.centery / self.W_HEIGHT
            sprite_positions.shape = (1, -1)
            return sprite_positions

    def start_game(self):
        """
        Main method to run game
        :return:
        """
        # Start a timer
        self.clock = pygame.time.Clock()
        # -- Create sprite groups --
        self.make_sprite_groups()
        # -- Create player and enemies
        self.spawn_enemies(20)
        player = self.spawn_player()
        # -- Create AI
        self.input_size = 2 * (1 + len(self.enemy_group))
        player_ai = SuperAvoiderAI(input_shape=(self.input_size,), neurons_layer=[10, 10, 5],
                                   activations=["relu", "relu", "softmax"])
        # -------- Main Program Loop ---------
        self.mainloop = True
        while self.mainloop:
            seconds = round(time.clock())  # Update time
            # ***** Main Event Loop *****
            self.event_handle()
            # *****  Game logic  *****
            # -- Spawn enemies with mouse
#            if pygame.mouse.get_pressed()[0]:
#                Enemy(pygame.mouse.get_pos(), self.background)
            # ---- collision detection ----
            for enemy in self.enemy_group:
                enemy.detected = False  # set all Enemy sprites to not detected

            # pygame.sprite.groupcollide(group1, group2, dokill1, dokill2, collided = None):
            # return dictionary of Sprites in group1 that collide with group2
            detected_dict = pygame.sprite.groupcollide(self.enemy_group, self.detection_group, False, False,
                                                       pygame.sprite.collide_circle)
            gameover_dict = pygame.sprite.groupcollide(self.player_group, self.enemy_group, False, False)
            # pygame.sprite.collide_circle works only if one sprite has self.radius
            # No argument collided yield self.rects will be checked
            if detected_dict:
                for enemy in detected_dict:
                    enemy.detected = True  # will get a blue border from Bird.update()
            # Remove player and its detector
            if gameover_dict:
                for player in gameover_dict:
                    print("Player %i Score: %i" % (player.number, player.score))
                    player.remove = True
                    EnemyDetection.devices[player.number].remove = True

            # ----- Update sprites -----
            # Erase sprites from last Group.draw() call.
            # The destination Surface is cleared by filling the drawn Sprite positions with the background.
            self.all_sprites_group.clear(self.screen, self.background)
            # Calls the update() method on all Sprites in the Group.
            # The base Sprite class has an update method that takes any number of arguments and does nothing.
            # The arguments passed to Group.update() will be passed to each Sprite.
            seconds_passed = self.clock.tick(self.FPS) / 1000.0
            # -- Update/Remove detectors for alive/removed players
            if self.player_group:
                for player in self.player_group:
                    self.detection_group.update((player.rect.centerx, player.rect.centery))
            # -- AI move --
            data = self.AI_input(player, detected_dict)
            ai_decision = player_ai.get_predict(data, classify=True)[0]
            self.player_group.update(seconds_passed, ai_decision)
            self.enemy_group.update(seconds_passed)  # arg = seconds since last call
            # Draws the contained Sprites to the Surface argument.
            # This uses the Sprite.image attribute for the source surface, and Sprite.rect for the position.
            self.all_sprites_group.draw(self.screen)

            # ----- Update screen with what we have drawn ----
            pygame.display.flip()
            # Display useful information
            pygame.display.set_caption("[FPS]: %.2f Time: %i Enemies: %i" % (self.clock.get_fps(), seconds, len(self.enemy_group)))
            # ----- Limit to 'FPS' frames per second ----
            self.clock.tick(self.FPS)
        pygame.quit()
        print("Game exit!\nShutting down...")
        exit(0)


if __name__ == '__main__':
    SuperAvoider()
