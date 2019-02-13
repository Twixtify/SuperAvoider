import os
import time
import pygame
import random
import numpy as np
import super_avoider_GA as ga
from enemy import Enemy
from player import Player
from player_ai import PlayerAI
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
    icon_path = os.path.join(image_path, "player_R.png")
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
        self.load_background()
        # -------------------------------------------------------------------------------------------------------------

        # ---- Make images suitable for quick blitting, i.e drawn quickly on screen ----
        for i, _ in enumerate(Enemy.image):
            Enemy.image[i] = Enemy.image[i].convert_alpha()
        for i, _ in enumerate(Player.image):
            Player.image[i] = Player.image[i].convert_alpha()
        for i, _ in enumerate(PlayerAI.image):
            PlayerAI.image[i] = PlayerAI.image[i].convert_alpha()
        # -------------------------------------------------------------------------------------------------------------

        # -- Create sprite groups --
        self.make_sprite_groups()
        # -- Create player --
        self.user_play = user_play
        if self.user_play:
            self.create_player(pos=(self.W_WIDTH / 2, self.W_HEIGHT / 2), controlled_by_ai=False)
        # -- Create enemies --
        self.enemies = enemies
        self.create_enemies(self.enemies)
        # -- Initialize AIs --
        self.GA = ga.SuperAvoiderGA()
        # - AI options -
        # input size = player (x,y) + enemy (x,y) + collision enemy + enemy (vx,vy)
        input_shape = (2 + 5 * self.enemies,)
        neurons_layer = [10, 10, 5]
        activations = ["relu", "relu", "softmax"]
        # - Create population of neural networks -
        self.GA.init_pop(size=ai_minds, ai_options=[input_shape, neurons_layer, activations])
        # - Create AI players and connect them to an AI -
        for i in range(len(self.GA.pop)):
            player = self.create_player(pos=(self.W_WIDTH / 2, self.W_HEIGHT / 2), controlled_by_ai=True)
            player.connect_ai(self.GA.get_ai(i))
        self.reset_pos(players=True, players_ai=True, enemies=True)

    def load_background(self, *args):
        self.background_colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
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
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player_R.png")))
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player_L.png")))
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player_sad.png")))
            Player.image.append(pygame.image.load(os.path.join(SuperAvoider.image_path, "player_dead.png")))
        except:
            raise (UserWarning, "Unable to find image in folder:", os.getcwd())
        Enemy.image.append(Enemy.image[0].copy())  # copy of first image
        Player.image.append(Player.image[2].copy())
        # rect(Surface, color, Rect, width=0) -> Rect
        # Draws a rectangular shape on the Surface. The given Rect is the area of the rectangle.
        # The width argument is the thickness to draw the outer edge.
        # If width is zero then the rectangle will be filled.
        pygame.draw.rect(Enemy.image[2], self.BLUE, (0, 0, 32, 36), 1)  # Draw blue border around image[2]
        pygame.draw.rect(Player.image[4], self.RED, (0, 0, 32, 32), 1)  # Draw red border around image[2]
        for image in Player.image:
            PlayerAI.image.append(image)

    def make_sprite_groups(self):
        # assign default groups to each sprite class
        self.all_sprites_group = pygame.sprite.LayeredUpdates()  # All sprites in this group
        self.player_group = pygame.sprite.LayeredUpdates()
        self.ai_group = pygame.sprite.LayeredUpdates()
        self.enemy_group = pygame.sprite.LayeredUpdates()
        self.detection_group = pygame.sprite.LayeredUpdates()
        # ---- Assign Layer for each group (all_sprites_group default layer 0)
        self.detection_group._default_layer = 3
        self.player_group._default_layer = 2
        self.ai_group._default_layer = 2
        self.enemy_group._default_layer = 1
        # ---- Enemy group
        Enemy.groups = self.enemy_group, self.all_sprites_group
        # ---- Player group
        Player.groups = self.player_group, self.all_sprites_group
        PlayerAI.groups = self.ai_group, self.all_sprites_group
        EnemyDetection.groups = self.detection_group, self.all_sprites_group

    def create_enemies(self, enemies=1):
        """
        Creates pop number of enemies
        Enemies spawn in the 1st quadrant of the game display
        :param enemies: Integer
        :return: None
        """
        for enemy in range(enemies):
            r = random.random()
            if r < 0.25:
                pos = (self.W_WIDTH / 4, self.W_HEIGHT / 4)  # Top left corner
            elif r < 0.5:
                pos = (3 * self.W_WIDTH / 4, self.W_HEIGHT / 4)  # Top right corner
            elif r < 0.75:
                pos = (self.W_WIDTH / 4, 3 * self.W_HEIGHT / 4)  # Bottom left corner
            else:
                pos = (3 * self.W_WIDTH / 4, 3 * self.W_HEIGHT / 4)  # Bottom right corner
            # Draw positions from top left corner
            Enemy(start_pos=pos, game_display=self.background)

    def create_player(self, pos, controlled_by_ai):
        """
        Spawn player on the board
        Players spawn in the 4th quadrant of the game display
        :return: Player object (Used to connect PlayerAI with a neural network)
        """
        # Create player object
        if controlled_by_ai:
            player_ai = PlayerAI(start_pos=pos, game_display=self.background)
            return player_ai
        player = Player(start_pos=pos, game_display=self.background)
        return player

    def reset_pos(self, players=False, players_ai=False, enemies=False):
        """
        Reset positions of sprites
        :return: None
        """
        # Clear screen from sprites
        self.all_sprites_group.clear(self.screen, self.background)
        # Update screen (i.e clear it)
        pygame.display.flip()
        # Reset position of players
        if players:
            for player in self.player_group:
                pos = (self.W_WIDTH / 2, self.W_HEIGHT / 2)
                player.new_pos(pos)
        # Reset position of AIs
        if players_ai:
            for player_ai in self.player_group:
                pos = (self.W_WIDTH / 2, self.W_HEIGHT / 2)
                player_ai.new_pos(pos)
        # Reset position of enemies
        if enemies:
            for enemy in self.enemy_group:
                r = random.random()
                if r < 0.25:
                    pos = (self.W_WIDTH / 4, self.W_HEIGHT / 4)  # Top left corner
                elif r < 0.5:
                    pos = (3 * self.W_WIDTH / 4, self.W_HEIGHT / 4)  # Top right corner
                elif r < 0.75:
                    pos = (self.W_WIDTH / 4, 3 * self.W_HEIGHT / 4)  # Bottom left corner
                else:
                    pos = (3 * self.W_WIDTH / 4, 3 * self.W_HEIGHT / 4)  # Bottom right corner
                enemy.new_pos(pos)

    def restart(self):
        """
        Restart the game. Check which type of players should be spawned
        :return:
        """
        # Check if all players are dead, then create all player sprites
        if self.user_play:
            if len(self.player_group) is 0:
                self.create_player(pos=(self.W_WIDTH / 2, self.W_HEIGHT / 2), controlled_by_ai=False)
        if len(self.ai_group) is 0:
            for i in range(len(self.GA.pop)):
                player_ai = self.create_player(pos=(self.W_WIDTH / 2, self.W_HEIGHT / 2), controlled_by_ai=True)
                player_ai.connect_ai(self.GA.get_ai(i))
        #else:
        #    # TODO: Assign only ai_brains that are currently not used
        #    # Create only missing player objects
        #    for player in self.player_group:
        #        if player.controlled_by_ai and len(self.player_group) < 2:
        #            if self.user_play:
        #                self.create_player(controlled_by_ai=False)
        #        elif len(self.player_group) < 2:  # Redo this
        #            self.create_player(controlled_by_ai=True)

        # Sample new positions of all sprites every restart
        self.reset_pos(enemies=True)

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

    def event_handle(self):
        for event in pygame.event.get():  # loop through all events that happened on the screen
            if event.type == pygame.QUIT:
                self.exit_game = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.exit_game = True
                if event.key == pygame.K_r:
                    self.restart()
                if event.key == pygame.K_p:
                    self.pause()

    def start_game(self, generation=None):
        """
        Main method to run game
        :param generation: Integer
        :return:
        """
        self.restart()
        self.load_background(generation)
        # Start a timer
        self.clock = pygame.time.Clock()
        # -------- Main Program Loop ---------
        score = []  # (AI number, AI score)
        cycles = 3  # How many cycles of game logic should be had before drawing to screen
        self.exit_game = False
        self.players_alive = True
        while self.players_alive:
            # **''''''''''''''''''''*** Main Event Loop *****''''''''''''''''''''''****
            self.event_handle()
            # -------------------------------------------------------------------------------------------------------
            for frame in range(cycles):
                if cycles > self.FPS:  # Just for safety
                    self.event_handle()
                # ''''''''''''''''''''''*****  Game logic  **'''''''''''''''''''''''''''***
                # ----- collision detection -----
                # Reset all Enemy sprites to not detected
                for enemy in self.enemy_group:
                    enemy.detected = False

                # pygame.sprite.groupcollide(group1, group2, dokill1, dokill2, collided = None):
                # return dictionary of Sprites in group1 that collide with group2
                # pygame.sprite.collide_circle works only if one sprite has self.radius
                # No argument collided yield self.rects will be checked
                detected_dict = pygame.sprite.groupcollide(self.enemy_group, self.detection_group, False, False,
                                                           pygame.sprite.collide_circle)
                # Return all players that collided with an enemy
                player_gameover_dict = pygame.sprite.groupcollide(self.player_group, self.enemy_group, False, False)
                # Return all player AIs that collided with an enemy
                ai_gameover_dict = pygame.sprite.groupcollide(self.ai_group, self.enemy_group, False, False)
                # -------------------------------------------------------------------------------------

                # ----- Calculate score -----
                seconds_passed = self.clock.tick(self.FPS) / 1000.0
                # ----- Flag players to be removed -----
                # Use blue border on enemies inside the hitbox of enemy_detection
                for enemy in detected_dict:
                    enemy.detected = True
                # Flag player to be removed
                for player in player_gameover_dict:
                    player.remove = True
                    print("Player score:  %.2f" % player.score)
                # Flag AI to be removed
                for player_ai in ai_gameover_dict:
                    player_ai.remove = True
                    score.append((player_ai.number, player_ai.score))
#                    print("AI %i Score: %.2f" % (player_ai.number, player_ai.score))
                self.all_sprites_group.update(seconds_passed, (self.enemy_group, self.GA.ai_input_size()))
            # -------------------------------------------------------------------------------------------------------

            # ***''''''''''''''*** Draw logic ***'''''''''''''''''''***

            # ----- Clear sprites from screen -----
            # Erase sprites from last Group.draw() call.
            # The destination Surface is cleared by filling the drawn Sprite positions with the background.
            self.all_sprites_group.clear(self.screen, self.background)
            # ----- Update sprites -----

            # ----- Draw sprites to screen -----
            # Draws Sprites to the Surface argument.
            # This uses the Sprite.image attribute for the source surface, and Sprite.rect for the position.
            self.all_sprites_group.draw(self.screen)
            # -------------------------------------------------------------------------------------------------------

            # ----- Update screen with what we have drawn ----
            pygame.display.flip()
            # Display useful information
            pygame.display.set_caption("[FPS]: %.2f Time: %i Players: %i" %
                                       (self.clock.get_fps(), round(time.clock()),
                                        len(self.player_group) + len(self.ai_group)))
            # ----- Limit to 'FPS' frames per second ----
            self.clock.tick(self.FPS)
            # ----- Game over condition ------
            if Player.total_number + PlayerAI.total_number == 0 or self.exit_game:
                self.players_alive = False
        if self.exit_game:
            return "exit"
        else:
            return score


def main():
    np.random.seed()
    # -- Create AI --
    SA = SuperAvoider(user_play=False, enemies=8, ai_minds=60)
    fitness = np.zeros(len(SA.GA.get_pop()))  # Create 1D array to hold fitness values
    individuals = []
    for i in range(len(fitness)):
        individuals.append(SA.GA.get_ind(i, use_bias=True))
    # -------------------------------------------------------
    generation, max_gen = 0, 10000
    while generation < max_gen:
        # Perform task for each AI
        score = SA.start_game(generation=generation)
        if score is "exit":
            pygame.quit()
            print("Game over\nShutting down...")
            exit(0)
        else:
            for i, val in score:
                fitness[i] = val
        # Perform evolution through genetic algorithm
        ga.breed(individuals, fitness, ga.sel_tournament, ga.co_uniform, ga.mut_gauss,
                 tournaments=12, tournament_size=4, replace_worst=6)
        # Update the minds of each individual
        SA.GA.set_pop(individuals)
        print("Generation %i Mean fitness %s" % (generation, np.mean(fitness)))
        generation += 1
    print(fitness.tolist())
    pygame.quit()
    print("Game over\nShutting down...")
    exit(0)

if __name__ == '__main__':
    main()
