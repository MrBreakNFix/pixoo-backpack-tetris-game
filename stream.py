import time
import pyautogui


def ss(interval, output_filename, target_size=(16, 16)):
    while True:
        screenshot = pyautogui.screenshot()

        width, height = screenshot.size

        min_dimension = min(width, height)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = (width + min_dimension) // 2
        bottom = (height + min_dimension) // 2

        screenshot = screenshot.crop((left, top, right, bottom))

        screenshot = screenshot.resize(target_size)

        screenshot.save(output_filename)
        time.sleep(interval)


if __name__ == "__main__":
    interval = 0.01
    output_filename = "image.png"

    ss(interval, output_filename)
