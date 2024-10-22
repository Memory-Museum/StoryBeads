import pygame
import time

def play_audio(filename):
    """Plays audio from a given file."""
    pygame.mixer.init()  # Initialize pygame mixer if not already
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        print("Playing...")
        time.sleep(0.1)  # Wait for playback to finish
    print("End of Audio file")
         


play_audio("welcomeaudio.wav")