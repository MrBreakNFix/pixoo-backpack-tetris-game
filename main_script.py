from time import sleep

from client import Pixoo


def main():
    pixoo = Pixoo("11:75:58:81:e8:b6")
    pixoo.connect()

    print("Connected to Pixoo")

    while True:
        if True:
            try:
                sleep(0.01)
                pixoo.draw_pic("image.png")
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
