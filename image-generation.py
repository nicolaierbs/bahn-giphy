import imageio
from pygifsicle import optimize
from PIL import Image, ImageDraw, ImageFont
import os.path
import requests
import copy


class ImageTransition:
    def __init__(self, file_name, start_pos, end_pos, num_frames, start_frame):
        self.file_name = file_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.time = num_frames
        self.start_time = start_frame

    def get_images(self):
        start_x, start_y = self.start_pos
        end_x, end_y = self.end_pos
        step_x, step_y = (end_x - start_x) / self.time, (end_y - start_y) / self.time
        images = []
        for i in range(self.time):
            images.append(ImageState(self.file_name, (int(start_x + i * step_x), int(start_y + i * step_y))))
        return images


class ImageState:
    def __init__(self, file_name, position):
        self.file_name = file_name
        self.pos = position

    def set_pos(self, position):
        self.pos = position

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_pos(self):
        return self.pos

    def get_file_name(self):
        return self.file_name


class FrameState:
    def __init__(self, bg, fg):
        self.background = bg
        self.foreground_objs = fg

    def get_bg(self):
        return self.background

    def get_fg(self):
        return self.foreground_objs

    def add_fg_obj(self, fg_obj):
        self.foreground_objs.append(fg_obj)

    def generate(self):
        background = Image.open(self.background.get_file_name())
        image = background
        for fg_obj in self.foreground_objs:
            foreground_obj = Image.open(fg_obj.get_file_name())
            image.paste(foreground_obj, fg_obj.get_pos(), mask=foreground_obj)
        return image


class GIFGenerator:
    def __init__(self):
        self.type = None
        self.frames = []

    def add_frame(self, bg=None, fg=None, reuse_last=True):
        if reuse_last:
            bg = self.get_frame().get_bg()
            fg = self.get_frame().get_fg()
        frame = FrameState(copy.deepcopy(bg), copy.deepcopy(fg))
        self.frames.append(frame)

    def get_frame(self, pos=-1):
        return self.frames[pos]

    def add_foreground_object(self, transition):
        images = transition.get_images()
        for i, image in enumerate(images):
            frame = self.get_frame(transition.start_time + i)
            frame.add_fg_obj(image)

    def generate_gif(self, fps = 50, file_name="output/test.gif"):
        frames = []
        for frame in self.frames:
            frames.append(frame.generate())
        imageio.mimsave(file_name, frames)
        optimize(file_name)


def check_font(path):
    if not os.path.isfile(path):
        url = 'https://github.com/ipython/xkcd-font/raw/master/xkcd-script/font/xkcd-script.ttf'
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)


font_path = 'xkcd-script.ttf'
check_font(font_path)

gif = GIFGenerator()

background = ImageState('images/landscape-winter.jpg', None)
background = ImageState('images/landscape-sommer.jpg', None)
foreground = ImageState('images/train_ice2.png', (-300,180))

gif.add_frame(background, [], reuse_last=False)
for i in range(40):
    gif.add_frame(reuse_last=True)
gif.add_foreground_object(ImageTransition('images/train_ice2.png', (-500,180), (500,180), 10, 0))
gif.add_foreground_object(ImageTransition('images/log.png', (200,180), (200,180), 10, 10))
gif.generate_gif()
