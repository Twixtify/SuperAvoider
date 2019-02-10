import os
import time
import pygame
import random
import numpy as np
import super_avoider_GA as GA
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
    icon_path = os.path.join(image_path, "player.png")
    try:
        pygame.display.set_icon(pygame.image.load(icon_path))
    except:
        raise (UserWarning, "Could not find icon in", icon_path)

    def __init__(self, user_play=True, enemies=50, ai_minds=0, screen_size=(800, 600)):
        # ---- Define some colors ----
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        # ---- Frames per seconds ----
        self.FPS = 60
        # ---- Load Images ----
        self.init_sprite_images()

        # ---- Set the background and Surface (screen) object ----
        size = self.W_WIDTH, self.W_HEIGHT = screen_size
        self.screen = pygame.display.set_mode(size)  # Create window which graphics are rendered on
        # -------------------------------------------------------------------------------------------------------------

        # ---- objects are drawn on and then pushed to the screen to render ----
        self.background_colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
        self.load_background()
        # -------------------------------------------------------------------------------------------------------------

        # ---- Make images suitable for quick blitting, i.e drawn quickly on screen ----
        for i, _ in enumerate(Enemy.image):
            Enemy.image[i] = Enemy.image[i].convert_alpha()
        for i, _ in enumerate(Player.image):
            Player.image[i] = Player.image[i].convert_alpha()
        # -------------------------------------------------------------------------------------------------------------

        # -- Create sprite groups --
        self.make_sprite_groups()
        # -- Create player --
        self.user_play = user_play
        if self.user_play:
            self.create_player(controlled_by_ai=False)
        # -- Create enemies --
        if enemies > 0:
            self.enemies = enemies
            self.create_enemies(self.enemies)
        # -- Initialize AIs --
        if ai_minds > 0:
            self.init_ai(ai_minds)

    def init_ai(self, ai_minds):
        """
        Initialize a set of AI minds and create player object for them to control
        :param ai_minds: Integer
        :return: None
        """
        self.ai_minds = []
        self.ai_inputs = 2 * (1 + self.enemies)
        self.player_ai = self.create_player(controlled_by_ai=True)  # Load a character that is controlled by AIs
        for ai in range(ai_minds):
            self.ai_minds.append(SuperAvoiderAI(input_shape=(self.ai_inputs,),
                                                neurons_layer=[8, 5, 5],
                                                activations=["relu", "relu", "softmax"]))

    def get_ai(self, ai):
        return self.ai_minds[ai].get_flatten_weights(use_bias=False)

    def load_background(self, *args):
        self.background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))  # Surface which graphic
        self.background.fill(self.background_colour)  # Background colour
        self.background.blit(self.write("Press ESC or Q to quit"), (5, 10))
        self.background.blit(self.write("Press P to (un)pause"), (self.W_WIDTH - 225, 10))
        if len(args) > 0:
            self.background.blit(self.write("Generation %i AI: %i" % (args[0], args[1])), (self.W_WIDTH - 225, 35))
        self.background.convert()
        # Push background object on queue to be printed on screen
        self.screen.blit(self.background, (0, 0))

    def write(self, msg="sample text", style=None, size=32, colour=(0, 0, 0)):
        my_font = pygame.font.SysFont(style, size)
        my_text = my_font.render(msg, True, colour)  # Surface object
        my_text = my_text.convert_alpha()
        return my_text

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
                        self.players_alive = False
                        paused = False
            # Update/draw game display
            pygame.display.flip()
            # Update only 5 times per second
            self.clock.tick(5)
        # Clear 'Paused' text from the screen
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

    def ai_decision(self, ai, enemy_group):
        """
        Create 1D array consisting of all player and enemy positions. Scaled by game windows width and height
        The first 2 entries are always the players x and y position
        :param ai: Neural network object
        :param enemy_group: Object group
        :return: 1D numpy array [rect.centerx_1, rect.centery_1, ...]
        """
        sprite_positions = np.zeros((self.ai_inputs,))  # 1D array of all x and y pos
        sprite_positions[0] = self.player_ai.rect.centerx / self.W_WIDTH
        sprite_positions[1] = self.player_ai.rect.centery / self.W_HEIGHT
        for i, enemy in enumerate(enemy_group):
            sprite_positions[i + 1] = enemy.rect.centerx / self.W_WIDTH
            sprite_positions[i + 2] = enemy.rect.centery / self.W_HEIGHT
        sprite_positions.shape = (1, -1)
        return ai.get_predict(sprite_positions, classify=True)[0]

    def create_enemies(self, enemies=1):
        """
        Creates pop number of enemies
        Enemies spawn in the 1st quadrant of the game display
        :param enemies: Integer
        :return: None
        """
        for enemy in range(enemies):
            # Draw positions from top left corner
            pos = (random.random() * self.W_WIDTH / 2, random.random() * self.W_HEIGHT / 2)
            Enemy(pos, self.background)

    def create_player(self, controlled_by_ai=False):
        """
        Spawn player on the board
        Players spawn in the 4th quadrant of the game display
        :return: Player object
        """
        pos = (self.W_WIDTH / 2 + random.random() * self.W_WIDTH / 2,
               self.W_HEIGHT / 2 + random.random() * self.W_HEIGHT / 2)
        player = Player(start_pos=pos, game_display=self.background, controlled_by_ai=controlled_by_ai)
        if controlled_by_ai:
            colour = (random.randint(0, 244), random.randint(0, 244), random.randint(0, 244))
            EnemyDetection(colour=colour, starting_pos=pos, size=5 * player.rect.width)
        return player

    def reset_pos(self):
        """
        Reset positions of sprites
        :return:
        """
        self.all_sprites_group.clear(self.screen, self.background)
        pygame.display.flip()
        # Reset position of enemies
        for enemy in self.enemy_group:
            # Draw positions from top left corner
            pos = (random.random() * self.W_WIDTH / 2, random.random() * self.W_HEIGHT / 2)
            enemy.new_pos(pos)
        # Reset position of players
        for player in self.player_group:
            pos = (self.W_WIDTH / 2 + random.random() * self.W_WIDTH / 2,
                   self.W_HEIGHT / 2 + random.random() * self.W_HEIGHT / 2)
            player.new_pos(pos)

    def restart(self):
        """
        Restart the game. Check which type of players should be spawned
        :return: w
        """
        if len(self.player_group) is 0:
            if self.user_play:
                self.create_player(controlled_by_ai=False)
            self.player_ai = self.create_player(controlled_by_ai=True)
        else:
            for player in self.player_group:
                if player.controlled_by_ai and len(self.player_group) < 2:
                    if self.user_play:
                        self.create_player(controlled_by_ai=False)
                elif len(self.player_group) < 2:
                    self.player_ai = self.create_player(controlled_by_ai=True)
        self.reset_pos()

    def event_handle(self):
        for event in pygame.event.get():  # loop through all events that happened on the screen
            if event.type == pygame.QUIT:
                self.players_alive = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.players_alive = False
                    return True
                if event.key == pygame.K_r:
                    self.restart()
                if event.key == pygame.K_p:
                    self.pause()
        return False

    def start_game(self, generation=None, ai_number=None):
        """
        Main method to run game
        :param generation
        :param ai_number: Integer
        :return:
        """
        self.restart()
        self.load_background(generation, ai_number)
        # Start a timer
        self.clock = pygame.time.Clock()
        # -------- Main Program Loop ---------
        force_close = False
        self.players_alive = True
        while self.players_alive:
            # **''''''''''''''''''''*** Main Event Loop *****''''''''''''''''''''''****
            force_close = self.event_handle()
            # -------------------------------------------------------------------------------------------------------

            # ''''''''''''''''''''''*****  Game logic  **'''''''''''''''''''''''''''***

            # ----- collision detection -----
            for enemy in self.enemy_group:
                enemy.detected = False  # set all Enemy sprites to not detected

            # pygame.sprite.groupcollide(group1, group2, dokill1, dokill2, collided = None):
            # return dictionary of Sprites in group1 that collide with group2
            # pygame.sprite.collide_circle works only if one sprite has self.radius
            # No argument collided yield self.rects will be checked
            detected_dict = pygame.sprite.groupcollide(self.enemy_group, self.detection_group, False, False,
                                                       pygame.sprite.collide_circle)
            gameover_dict = pygame.sprite.groupcollide(self.player_group, self.enemy_group, False, False)

            # -------------------------------------------------------------------------------------------------------

            # ----- Calculate score -----
            seconds_passed = self.clock.tick(self.FPS) / 1000.0
            # ----- Flag players to be removed -----
            # Use blue border on enemies inside the hitbox of enemy_detection
            for enemy in detected_dict:
                enemy.detected = True
            # Remove player and its detector
            for player in gameover_dict:
                player.remove = True
                if player.controlled_by_ai:
                    print("AI %i Score: %.2f" % (ai_number, player.score))
                    EnemyDetection.devices[EnemyDetection.number - 1].remove = True
                else:
                    print("Player score:  %.2f" % player.score)
            # -------------------------------------------------------------------------------------------------------

            # ----- Clear sprites from screen -----
            # Erase sprites from last Group.draw() call.
            # The destination Surface is cleared by filling the drawn Sprite positions with the background.
            self.all_sprites_group.clear(self.screen, self.background)
            # ----- Update sprites -----
            self.detection_group.update((self.player_ai.rect.centerx, self.player_ai.rect.centery))
            ai_decision = self.ai_decision(self.ai_minds[ai_number], detected_dict)
            self.player_group.update(seconds_passed, ai_decision)
            self.enemy_group.update(seconds_passed)  # arg = seconds since last call

            # ----- Draw sprites to screen -----
            # Draws Sprites to the Surface argument.
            # This uses the Sprite.image attribute for the source surface, and Sprite.rect for the position.
            self.all_sprites_group.draw(self.screen)
            # -------------------------------------------------------------------------------------------------------

            # ----- Game over condition ------
            if ai_number is not None:
                if len(self.player_group) is 0:
                    self.players_alive = False
            # ----- Update screen with what we have drawn ----
            pygame.display.flip()
            # Display useful information
            pygame.display.set_caption("[FPS]: %.2f Time: %i Enemies: %i" %
                                       (self.clock.get_fps(), round(time.clock()), len(self.enemy_group)))
            # ----- Limit to 'FPS' frames per second ----
            self.clock.tick(self.FPS)
        if force_close:
            return force_close
        return self.player_ai.score


def main():
    # -- Create AI --
    SA = SuperAvoider(user_play=False, enemies=100, ai_minds=10)
    individuals = []
    for ai in SA.ai_minds:
        individuals.append(ai.get_flatten_weights(use_bias=False))
    # -------------------------------------------------------
    fitness = np.zeros(len(SA.ai_minds))  # Create 1D array to hold fitness values
    generation, max_gen = 0, 1000
    while generation < max_gen:
        for ai in range(len(SA.ai_minds)):
            score = SA.start_game(generation=generation, ai_number=ai)
            if score is True:
                pygame.quit()
                print("Game over\nShutting down...")
                exit(0)
            else:
                fitness[ai] = score
        individuals = GA.breed(individuals, fitness, GA.sel_tournament, GA.co_uniform, GA.mut_gauss,
                               tournaments=4, tournament_size=3)
        print("Generation %i Mean fitness %s" % (generation, np.mean(fitness)))
        generation += 1
    print(fitness.tolist())
    pygame.quit()
    print("Game over\nShutting down...")
    exit(0)

if __name__ == '__main__':
    main()
