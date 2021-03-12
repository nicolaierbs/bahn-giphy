import imageio
from pygifsicle import optimize
from PIL import Image, ImageDraw, ImageFont
import os.path
import requests
import copy

###
#
#  Image and Movement
#
###


class Bounce:
    def __init__(self, pos_one, pos_two, time, freq):
        self.pos_one = pos_one
        self.pos_two = pos_two
        self.time = time
        self.freq = freq

    def get_positions(self):
        positions = []
        time_one_way = int(self.time / (2*self.freq))
        for j in range(self.freq):
            up = Translation(self.pos_one, self.pos_two, time_one_way)
            down = Translation(self.pos_two, self.pos_one, time_one_way)
            positions += up.get_positions()
            positions += down.get_positions()
        return positions


class Translation:
    def __init__(self, start_pos, end_pos, time):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.time = time

    def get_positions(self):
        positions = []
        start_x, start_y = self.start_pos
        end_x, end_y = self.end_pos
        step_x, step_y = (end_x - start_x) / self.time, (end_y - start_y) / self.time
        for i in range(self.time):
            positions.append((int(start_x + (i + 1) * step_x), int(start_y + (i + 1) * step_y)))
        return positions


class ImageState:
    def __init__(self, file_name, start_pos, num_frames):
        self.file_name = file_name
        self.start_pos = start_pos
        self.time = num_frames
        self.movement = {}
        self.movement_start_time = 0
        self.movement_start_pos = start_pos

    def add_movement(self, end_pos, time, start_time_delta=0, mode='linear', freq=None):
        if mode == 'linea':
            movement = Translation(self.movement_start_pos, end_pos, time)
        elif mode == 'bounce':
            movement = Bounce(self.movement_start_pos, end_pos, time, freq)
        self.movement[self.movement_start_time + start_time_delta] = movement
        self.movement_start_time += time + start_time_delta
        self.movement_start_pos = end_pos

    def get_image_state_frame(self):
        images = []
        positions = [self.start_pos]
        print(self.movement)
        for i in range(self.time):
            if i in self.movement:
                positions = self.movement[i].get_positions()
            if len(positions) > 1:
                position = positions[0]
                del positions[0]
            else:
                position = positions[0]
            images.append(ImageStateFrame(self.file_name, position))
        return images


###
#
#  GIF
#
###

class ImageStateFrame:
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
    def __init__(self, bg, fg=None, text=None):
        self.background = bg
        if fg:
            self.foreground_objs = fg
        else:
            self.foreground_objs = []
        self.text = text

    def get_bg(self):
        return self.background

    def get_fg(self):
        return self.foreground_objs

    def add_fg_obj(self, fg_obj):
        self.foreground_objs.append(fg_obj)

    def generate(self):
        font = ImageFont.truetype(font_path, 32)
        background = Image.open(self.background.get_file_name())
        image = background
        for fg_obj in self.foreground_objs:
            foreground_obj = Image.open(fg_obj.get_file_name())
            image.paste(foreground_obj, fg_obj.get_pos(), mask=foreground_obj)
        if self.text:
            draw = ImageDraw.Draw(image)
            draw.text((150, 60), self.text, (255, 100, 100), font=font)
        return image


class GIFGenerator:
    def __init__(self, gif_length=None, bg=None):
        self.type = None
        self.frames = []
        if gif_length:
            for _ in range(gif_length):
                self.add_frame(bg=bg)

    def add_frame(self, bg=None, fg=None, reuse_last=False):
        if reuse_last:
            bg = self.get_frame().get_bg()
            fg = self.get_frame().get_fg()
        frame = FrameState(copy.deepcopy(bg), copy.deepcopy(fg))
        self.frames.append(frame)

    def get_frame(self, pos=-1):
        return self.frames[pos]

    def add_foreground_object(self, obj, start_frame):
        images = obj.get_image_state_frame()
        for i, image in enumerate(images):
            frame = self.get_frame(start_frame + i)
            frame.add_fg_obj(image)

    def add_text(self, text, time):
        start, duration = time
        for t in range(duration):
            frame = self.get_frame(start + t)
            frame.text = text

    def generate_gif(self, output_path="output/", file_name="test.gif"):
        frames = []
        for frame in self.frames:
            frames.append(frame.generate())
        imageio.mimsave(output_path + file_name, frames)
        optimize(output_path + file_name)


def check_font(path):
    if not os.path.isfile(path):
        url = 'https://github.com/ipython/xkcd-font/raw/master/xkcd-script/font/xkcd-script.ttf'
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)


font_path = 'xkcd-script.ttf'
check_font(font_path)

background = ImageStateFrame('images/landscape-winter.jpg', None)
background = ImageStateFrame('images/landscape-sommer.jpg', None)
foreground = ImageStateFrame('images/train_ice2.png', (-300,180))
gif = GIFGenerator(gif_length=50, bg=background)
train = ImageState('images/train_ice2.png', (50,180), 50)
#train.add_movement((500,100), 10, 10)
train.add_movement((0,20), 30, 10, mode='bounce', freq=4)
gif.add_foreground_object(train, 0)
gif.add_foreground_object(ImageState('images/log.png', (200,180), 10), 10)
gif.add_text("Welcome!", (10, 5))
gif.generate_gif()
