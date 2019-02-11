import os
import time
import pygame
import random
import numpy as np
import super_avoider_GA as GA
from enemy import Enemy
from player import Player
from enemy_detection import EnemyDetection


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
        if user_play:
            self.create_player(controlled_by_ai=False)
        # -- Create enemies --
        if enemies > 0:
            self.enemies = enemies
            self.create_enemies(self.enemies)
        # -- Initialize AIs --
        if ai_minds > 0:
            self.ai_minds = []
            for ai in range(ai_minds):
                self.ai_minds.append(self.create_player(controlled_by_ai=True))

    def load_background(self, *args):
        self.background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))  # Surface which graphic
        self.background.fill(self.background_colour)  # Background colour
        self.background.blit(self.write("Press ESC or Q to quit"), (5, 10))
        self.background.blit(self.write("Press P to (un)pause"), (self.W_WIDTH - 225, 10))
        if len(args) > 0:
            self.background.blit(self.write("Generation %i" % args[0]), (self.W_WIDTH - 225, 35))
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

    def create_enemies(self, enemies=1):
        """
        Creates pop number of enemies
        Enemies spawn in the 1st quadrant of the game display
        :param enemies: Integer
        :return: None
        """
        for enemy in range(enemies):
            # Draw positions from top left corner
            pos = (self.W_WIDTH / 4, self.W_HEIGHT / 4)
            Enemy(pos, self.background)

    def create_player(self, controlled_by_ai=False, ai_brain=False):
        """
        Spawn player on the board
        Players spawn in the 4th quadrant of the game display
        :return: Player object
        """
        pos = (self.W_WIDTH / 2 + self.W_WIDTH / 4,
               self.W_HEIGHT / 2 + self.W_HEIGHT / 4)
        if controlled_by_ai:
            # Create player object
            player = Player(start_pos=pos, game_display=self.background, controlled_by_ai=controlled_by_ai)
            # Initialize neural network
            player.init_ai(ai_input_size=2 * (1 + self.enemies), brain=ai_brain)
        else:
            player = Player(start_pos=pos, game_display=self.background, controlled_by_ai=controlled_by_ai)
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
            pos = (self.W_WIDTH / 4, self.W_HEIGHT / 4)
            enemy.new_pos(pos)
        # Reset position of players
        for player in self.player_group:
            pos = (self.W_WIDTH / 2 + self.W_WIDTH / 4,
                   self.W_HEIGHT / 2 + self.W_HEIGHT / 4)
            player.new_pos(pos)

    def restart(self, ai_brains):
        """
        Restart the game. Check which type of players should be spawned
        :return:
        """
        # Check if all players are dead, then create all player sprites
        if len(self.player_group) is 0:
            if self.user_play:
                self.create_player(controlled_by_ai=False)
            for ai in range(len(self.ai_minds)):
                self.ai_minds[ai] = self.create_player(controlled_by_ai=True, ai_brain=ai_brains[ai])
        else:
            # TODO: Assign only ai_brains that are currently not used
            # Create only missing player objects
            for player in self.player_group:
                if player.controlled_by_ai and len(self.player_group) < 2:
                    if self.user_play:
                        self.create_player(controlled_by_ai=False)
                elif len(self.player_group) < 2:  # Redo this
                    self.player_ai = self.create_player(controlled_by_ai=True, ai_brain=ai_brains)
        self.reset_pos()

    def pause(self):
        pause_text_surf = self.write("Paused", style="None", size=115)
        pause_text_rect = pause_text_surf.get_rect()
        pause_text_rect.center = ((round(self.W_WIDTH / 2)), (round(self.W_HEIGHT / 2)))
        self.screen.blit(pause_text_surf, pause_text_rect)
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game = True
                    paused = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        self.exit_game = True
                        paused = False
            # Update/draw game display
            pygame.display.flip()
            # Update only 5 times per second
            self.clock.tick(5)
        # Clear 'Paused' text from the screen
        self.screen.blit(self.background, (0, 0))

    def event_handle(self, ai_brains):
        for event in pygame.event.get():  # loop through all events that happened on the screen
            if event.type == pygame.QUIT:
                self.exit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.exit_game = True
                if event.key == pygame.K_r:
                    self.restart(ai_brains=ai_brains)
                if event.key == pygame.K_p:
                    self.pause()

    def start_game(self, generation=None, ai_brains=None):
        """
        Main method to run game
        :param generation: Integer
        :param ai_brains: List of neural network weights
        :return:
        """
        self.restart(ai_brains)
        self.load_background(generation)
        # Start a timer
        self.clock = pygame.time.Clock()
        # -------- Main Program Loop ---------
        score = []  # (player number, player score)
        self.exit_game = False
        self.players_alive = True
        while self.players_alive:
            # **''''''''''''''''''''*** Main Event Loop *****''''''''''''''''''''''****
            self.event_handle(ai_brains)
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
                    score.append((player.number, player.score))
                    print("AI %i Score: %.2f" % (player.number, player.score))
                else:
                    print("Player score:  %.2f" % player.score)
            # -------------------------------------------------------------------------------------------------------

            # ----- Clear sprites from screen -----
            # Erase sprites from last Group.draw() call.
            # The destination Surface is cleared by filling the drawn Sprite positions with the background.
            self.all_sprites_group.clear(self.screen, self.background)
            # ----- Update sprites -----
            self.player_group.update(seconds_passed, self.enemy_group)
            self.detection_group.update()
            self.enemy_group.update(seconds_passed)  # arg = seconds since last call

            # ----- Draw sprites to screen -----
            # Draws Sprites to the Surface argument.
            # This uses the Sprite.image attribute for the source surface, and Sprite.rect for the position.
            self.all_sprites_group.draw(self.screen)
            # -------------------------------------------------------------------------------------------------------

            # ----- Update screen with what we have drawn ----
            pygame.display.flip()
            # Display useful information
            pygame.display.set_caption("[FPS]: %.2f Time: %i Enemies: %i" %
                                       (self.clock.get_fps(), round(time.clock()), len(self.enemy_group)))
            # ----- Limit to 'FPS' frames per second ----
            self.clock.tick(self.FPS)
            # ----- Game over condition ------
            if Player.total_number == 0 or self.exit_game:
                self.players_alive = False
        if self.exit_game:
            return "exit"
        else:
            return score


def main():
    # -- Create AI --
    SA = SuperAvoider(user_play=False, enemies=40, ai_minds=10)
    fitness = np.zeros(len(SA.ai_minds))  # Create 1D array to hold fitness values
    individuals = []
    for player_ai in SA.ai_minds:
        individuals.append(player_ai.get_brain())
    # -------------------------------------------------------
    generation, max_gen = 0, 1000
    while generation < max_gen:
        # Perform task for each AI
        score = SA.start_game(generation=generation, ai_brains=individuals)
        if score is "exit":
            pygame.quit()
            print("Game over\nShutting down...")
            exit(0)
        else:
            for i, val in score:
                fitness[i] = val
        # Perform evolution through genetic algorithm
        individuals = GA.breed(individuals, fitness, GA.sel_tournament, GA.co_uniform, GA.mut_gauss,
                               tournaments=6, tournament_size=5)
        # Update the minds of each individual
        for num, player_ai in enumerate(SA.ai_minds):
            player_ai.set_brain(individuals[num])
        print("Generation %i Mean fitness %s" % (generation, np.mean(fitness)))
        generation += 1
    print(fitness.tolist())
    pygame.quit()
    print("Game over\nShutting down...")
    exit(0)

if __name__ == '__main__':
    main()
