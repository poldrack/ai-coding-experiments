# Write a python function that takes as input a textfile, then create an animation that:
#[1] Displays X lines of the textfile at a time, with Y characters per line.  If the text file has more than Y characters in a line, then move to the next line.  
#[2] Scross down Z lines of the textfile every second, in a continuous way.
#[3] Animate it in a new popup window.
#[4] Record the animation for R seconds, and save it as a .avi file.
# based on Seb Bubeck's talk

import pygame
import pyganim
import cv2
import time
import os

def create_text_animation(textfile, X=5, Y=80, Z=1, R=10):
    pygame.init()

    # Set up window and font
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Text Animation")
    font = pygame.font.Font(None, 36)
    
    # Load and format the text file
    with open(textfile, 'r') as file:
        lines = file.readlines()
    formatted_lines = [line[i:i+Y] for line in lines for i in range(0, len(line), Y)]

    # Create the animation
    animation = pyganim.PygAnimation([(font.render(formatted_lines[i], True, (255, 255, 255)), 1000) for i in range(len(formatted_lines))])
    animation.play()

    # Set up OpenCV video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 1.0, (800, 600))

    # Main loop
    start_time = time.time()
    while time.time() - start_time < R:
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Draw the animation
        animation.blit(screen, (0, 0))

        # Scroll down Z lines
        animation.scroll(0, -Z * font.get_height())
        pygame.display.flip()

        # Save frame as OpenCV image
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)

    # Clean up
    out.release()
    pygame.quit()
    cv2.destroyAllWindows()

# Example usage
create_text_animation('code_complexity.py', X=5, Y=80, Z=1, R=10)
