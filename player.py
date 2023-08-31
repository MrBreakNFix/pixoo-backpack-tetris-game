import pygame


def play_midi(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


if __name__ == "__main__":
    midi_file = "tetris.mid"  # Replace with the path to your MIDI file
    play_midi(midi_file)

    try:
        # Continue running the program until the music finishes playing
        while pygame.mixer.music.get_busy():
            pass
    except KeyboardInterrupt:
        # Allow the user to stop the music with Ctrl+C
        pygame.mixer.music.stop()
