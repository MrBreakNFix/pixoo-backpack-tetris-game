import math
import os

import keyboard
from PIL import Image, ImageDraw, ImageFont
import imageio
import socket
from math import log10, ceil
from time import sleep


class Pixoo:
    CMD_SET_SYSTEM_BRIGHTNESS = 0x74
    CMD_SPP_SET_USER_GIF = 0xB1
    CMD_DRAWING_ENCODE_PIC = 0x5B

    BOX_MODE_CLOCK = 0
    BOX_MODE_TEMP = 1
    BOX_MODE_COLOR = 2
    BOX_MODE_SPECIAL = 3

    instance = None

    def __init__(self, mac_address):
        """
        Constructor
        """
        self.mac_address = mac_address
        self.btsock = None

    @staticmethod
    def get():
        if Pixoo.instance is None:
            Pixoo.instance = Pixoo(Pixoo.BDADDR)
            Pixoo.instance.connect()
        return Pixoo.instance

    def draw_dir(self, directory, delay=100):
        """
        Draw encoded pictures from a directory with a delay between frames.
        """
        # Get a list of image files in the directory
        image_files = sorted([f for f in os.listdir(directory) if f.endswith(".png")])

        for filepath in image_files:
            self.draw_pic(os.path.join(directory, filepath))
            sleep(delay / 1000)  # Convert milliseconds to seconds

    def connect(self):
        """
        Connect to SPP.
        """
        while True:
            try:
                print(f"Connecting to {self.mac_address}...")
                self.btsock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                self.btsock.connect((self.mac_address, 1))
                sleep(1)  # mandatory to wait at least 1 second
                print("Connected.")
                break  # Connection successful, exit the loop
            except OSError as e:
                print(f"Connection failed: {e}")
                print("Retrying in 1 second...")
                sleep(1)  # Wait for 5 seconds before retrying

    def __spp_frame_checksum(self, args):
        """
        Compute frame checksum
        """
        return sum(args[1:]) & 0xFFFF

    def __spp_frame_encode(self, cmd, args):
        """
        Encode frame for given command and arguments (list).
        """
        payload_size = len(args) + 3

        # create our header
        frame_header = [1, payload_size & 0xFF, (payload_size >> 8) & 0xFF, cmd]

        # concatenate our args (byte array)
        frame_buffer = frame_header + args

        # compute checksum (first byte excluded)
        cs = self.__spp_frame_checksum(frame_buffer)

        # create our suffix (including checksum)
        frame_suffix = [cs & 0xFF, (cs >> 8) & 0xFF, 2]

        # return output buffer
        return frame_buffer + frame_suffix

    def send(self, cmd, args, retry_count=math.inf):
        """
        Send data to SPP. Try to reconnect if the socket got closed.
        """
        spp_frame = self.__spp_frame_encode(cmd, args)
        self.__send_with_retry_reconnect(bytes(spp_frame), retry_count)

    def __send_with_retry_reconnect(self, bytes_to_send, retry_count=5):
        """
        Send data with a retry in case of socket errors.
        """
        while retry_count >= 0:
            try:
                if self.btsock is not None:
                    self.btsock.send(bytes_to_send)
                    return

                print(f"[!] Socket is closed. Reconnecting... ({retry_count} tries left)")
                retry_count -= 1
                self.connect()
            except (ConnectionResetError, OSError):  # OSError is for Device is Offline
                self.btsock = None  # reset the btsock
                print("[!] Connection was reset. Retrying...")

    def set_system_brightness(self, brightness):
        """
        Set system brightness.
        """
        self.send(Pixoo.CMD_SET_SYSTEM_BRIGHTNESS, [brightness & 0xFF])

    def set_box_mode(self, boxmode, visual=0, mode=0):
        """
        Set box mode.
        """
        self.send(0x45, [boxmode & 0xFF, visual & 0xFF, mode & 0xFF])

    def set_color(self, r, g, b):
        """
        Set color.
        """
        self.send(0x6F, [r & 0xFF, g & 0xFF, b & 0xFF])

    def encode_image(self, filepath):
        img = Image.open(filepath)
        return self.encode_raw_image(img)

    def encode_raw_image(self, img):
        """
        Encode a 16x16 image.
        """
        # ensure image is 16x16
        w, h = img.size
        if w == h:
            # resize if image is too big
            if w > 16:
                img = img.resize((16, 16))

            # create palette and pixel array
            pixels = []
            palette = []
            for y in range(16):
                for x in range(16):
                    pix = img.getpixel((x, y))

                    if len(pix) == 4:
                        r, g, b, a = pix
                    elif len(pix) == 3:
                        r, g, b = pix
                    if (r, g, b) not in palette:
                        palette.append((r, g, b))
                        idx = len(palette) - 1
                    else:
                        idx = palette.index((r, g, b))
                    pixels.append(idx)

            # encode pixels
            bitwidth = ceil(log10(len(palette)) / log10(2))
            nbytes = ceil((256 * bitwidth) / 8.0)
            encoded_pixels = [0] * nbytes

            encoded_pixels = []
            encoded_byte = ""
            for i in pixels:
                encoded_byte = bin(i)[2:].rjust(bitwidth, "0") + encoded_byte
                if len(encoded_byte) >= 8:
                    encoded_pixels.append(encoded_byte[-8:])
                    encoded_byte = encoded_byte[:-8]
            encoded_data = [int(c, 2) for c in encoded_pixels]
            encoded_palette = []
            for r, g, b in palette:
                encoded_palette += [r, g, b]
            return (len(palette), encoded_palette, encoded_data)
        else:
            print("[!] Image must be square.")

    def draw_gif(self, filepath, speed):
        """
        Parse Gif file and draw as animation.
        """
        # encode frames
        frames = []
        timecode = 0
        anim_gif = Image.open(filepath)
        for n in range(anim_gif.n_frames):
            anim_gif.seek(n)
            nb_colors, palette, pixel_data = self.encode_raw_image(anim_gif.convert(mode="RGB"))
            frame_size = 7 + len(pixel_data) + len(palette)
            frame_header = [
                0xAA,
                frame_size & 0xFF,
                (frame_size >> 8) & 0xFF,
                timecode & 0xFF,
                (timecode >> 8) & 0xFF,
                0,
                nb_colors,
            ]
            frame = frame_header + palette + pixel_data
            frames += frame
            timecode = speed

        # send animation
        nchunks = ceil(len(frames) / 200.0)
        total_size = len(frames)
        for i in range(nchunks):
            chunk = [total_size & 0xFF, (total_size >> 8) & 0xFF, i]
            self.send(0x49, chunk + frames[i * 200: (i + 1) * 200])

    def draw_anim(self, directory, speed=100):
        timecode = 0

        # Get a list of image files in the directory
        image_files = sorted([f for f in os.listdir(directory) if f.startswith("frame_") and f.endswith(".png")])

        # encode frames
        frames = []
        n = 0
        for filepath in image_files:
            nb_colors, palette, pixel_data = self.encode_image(os.path.join(directory, filepath))
            frame_size = 7 + len(pixel_data) + len(palette)
            frame_header = [
                0xAA,
                frame_size & 0xFF,
                (frame_size >> 8) & 0xFF,
                timecode & 0xFF,
                (timecode >> 8) & 0xFF,
                0,
                nb_colors,
            ]
            frame = frame_header + palette + pixel_data
            frames += frame
            timecode += speed

        # send animation
        nchunks = ceil(len(frames) / 200.0)
        total_size = len(frames)
        for i in range(nchunks):
            chunk = [total_size & 0xFF, (total_size >> 8) & 0xFF, i]
            self.send(0x49, chunk + frames[i * 200: (i + 1) * 200])

    def draw_pic(self, filepath):
        """
        Draw encoded picture.
        """
        nb_colors, palette, pixel_data = self.encode_image(filepath)
        frame_size = 7 + len(pixel_data) + len(palette)
        frame_header = [0xAA, frame_size & 0xFF, (frame_size >> 8) & 0xFF, 0, 0, 0, nb_colors]
        frame = frame_header + palette + pixel_data
        prefix = [0x0, 0x0A, 0x0A, 0x04]
        self.send(0x44, prefix + frame)

    def draw_text(self, text, font_size, delay, text_color, background_color):
        width, height = 16, 16  # Dimensions of the display
        font_path = "PIXELADE.TTF"
        font = ImageFont.truetype(font_path, font_size)
        # text_color = (0, 0, 255)
        # background_color = (0, 0, 0)

        # Generate frames for scrolling text
        frames = []
        for shift in range(len(text) * font_size):
            img = Image.new("RGB", (width, height), background_color)
            draw = ImageDraw.Draw(img)
            text_position = (width - shift, (height - font_size) // 2)
            draw.text(text_position, text, font=font, fill=text_color)
            frames.append(img)

        # Save GIF using imageio
        gif_path = "scrolling_text.gif"  # Change this to the desired GIF path
        with imageio.get_writer(gif_path, mode='I', duration=delay / 1000) as writer:
            for frame in frames:
                writer.append_data(frame)

        # Clean up
        for frame in frames:
            frame.close()

        self.draw_gif(gif_path, delay)  # Use the existing draw_gif method to display the generated GIF



if __name__ == '__main__':
    pixoo_baddr = "11:75:58:81:e8:b6"
    gif_folder = "gif_folder"  # Change this to your folder path

    pixoo = Pixoo(pixoo_baddr)
    pixoo.connect()
    sleep(1)

    # Get a list of image files in the directory
    image_files = sorted([f for f in os.listdir(gif_folder) if f.endswith(".gif")])

    current_gif_index = 0
    static_image_displayed = False

    while True:
        # Wait for arrow key presses to navigate through the GIFs or display a static image
        while True:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == 'right':
                    current_gif_index = (current_gif_index + 1) % len(image_files)
                    if current_gif_index == 0:
                        current_gif_index = (current_gif_index + 1) % len(image_files)
                    static_image_displayed = False
                    isasleep = False

                    break
                elif event.name == 'left':
                    current_gif_index = (current_gif_index - 1) % len(image_files)
                    if current_gif_index == 0:
                        current_gif_index = (current_gif_index - 1) % len(image_files)
                    static_image_displayed = False
                    isasleep = False

                    break
                elif event.name == 'space':
                    current_gif_index = 0
                    static_image_displayed = False
                    isasleep = False

                    break
                elif event.name == 'up':
                    static_image_displayed = True
                    isasleep = False
                    break
                elif event.name == 'down':
                    text = "This is a longer gif test to see if time is a problem"

                    font_size = 12
                    delay_per_frame = 100
                    text_color = (0, 0, 255)
                    background_color = (0, 0, 0)

                    num_frames = len(text) * font_size
                    gif_duration = num_frames * delay_per_frame / 1000.0  # Convert to seconds

                    pixoo.draw_text(text, font_size, delay_per_frame, text_color, background_color)

                    print(f"Total duration of the GIF: {gif_duration} seconds")
                    static_image_displayed = False
                    isasleep = False
                    break

        if static_image_displayed:
            static_image_displayed = False
        else:
            img_path = os.path.join(gif_folder, image_files[current_gif_index])
            if isasleep:
                sleep(1)
                isasleep = False
            pixoo.draw_gif(img_path, 100)
