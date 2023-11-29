import pygame
import sys

from client import Pixoo
pixoo = Pixoo("11:75:58:81:e8:b6")
pixoo.connect()
pygame.init()

# Initialize the display (a small window)
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Key Input Listener")

input_string = ""  # Initialize an empty string to store the typed keys

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Exit on pressing Esc
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_RETURN:  # Perform an action on pressing Enter
                print("Action with input:", input_string)
                pixoo.draw_text(str(input_string), 12, 100, (255, 0, 0), (0, 0, 0))
                input_string = ""  # Clear the input string after the action
            else:
                if event.unicode:  # Check if the pressed key has a unicode representation
                    input_string += event.unicode
                    print("Input string:", input_string)
