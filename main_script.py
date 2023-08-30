import multiprocessing
from time import sleep

import TetrisGame
from client import Pixoo
from tetris_module import Tetris

def run_tetris_game():
    TetrisGame.run_tetris_game()

def main():
    tetris = Tetris()

    pixoo = Pixoo("11:75:58:81:e8:b6")
    pixoo.connect()

    print("Connected to Pixoo")

    # Create a separate process for running TetrisGame
    tetris_game_process = multiprocessing.Process(target=run_tetris_game)
    tetris_game_process.start()

    while True:
        if tetris.notScoring:
            try:
                sleep(0.01)
                pixoo.draw_pic("tetris.png")
            except Exception as e:
                print(f"An error occurred: {e}")
            sleep(0.01)
        else:
            try:
                print("YES")
                pixoo.draw_text(str("score"), 12, 100, (255, 255, 255), (0, 0, 0))
            except Exception as e:
                print(f"An error occurred: {e}")
            sleep(0.01)

if __name__ == '__main__':
    main()
