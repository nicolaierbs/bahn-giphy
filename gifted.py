import imageio
# from pygifsicle import optimize
from PIL import Image, ImageDraw, ImageFont
import time
from datetime import datetime
import copy

font_path = 'fonts/DB Sans Regular.otf'

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
        if mode == 'linear':
            movement = Translation(self.movement_start_pos, end_pos, time)
        elif mode == 'bounce':
            movement = Bounce(self.movement_start_pos, end_pos, time, freq)
        self.movement[self.movement_start_time + start_time_delta] = movement
        self.movement_start_time += time + start_time_delta
        self.movement_start_pos = end_pos

    def get_image_state_frame(self):
        images = []
        positions = [self.start_pos]
        # print(self.movement)
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
    def __init__(self, bg, fg=None, messages=None):
        self.background = bg
        if fg:
            self.foreground_objs = fg
        else:
            self.foreground_objs = []
        self.messages = messages

    def get_bg(self):
        return self.background

    def get_fg(self):
        return self.foreground_objs

    def add_fg_obj(self, fg_obj):
        self.foreground_objs.append(fg_obj)

    def generate(self):
        font = ImageFont.truetype(font_path, 14)
        background = Image.open(self.background.get_file_name())
        image = background
        for fg_obj in self.foreground_objs:
            foreground_obj = Image.open(fg_obj.get_file_name())
            image.paste(foreground_obj, fg_obj.get_pos(), mask=foreground_obj)
        if self.messages:
            for message in self.messages:
                draw = ImageDraw.Draw(image)
                draw.text(message['position'], message['text'], font=font, fill=message['color'])
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

    def add_message(self, message, start_frame=0, num_frames=0):
        for t in range(num_frames):
            frame = self.get_frame(start_frame + t)
            if not frame.messages:
                frame.messages = list()
            frame.messages.append(message)

    def generate_gif(self):
        frames = []
        for frame in self.frames:
            frames.append(frame.generate())
        path = 'temp.gif'
        frames[0].save(path,
                       save_all=True, append_images=frames[1:], optimize=True, duration=100, loop=0)
        return path


def rolling_train(train, num_frames):
    # TODO This can probably be automated
    if train == 'bahn_angela':
        train = ImageState('images/trains/' + train + '.png', (-620, 250), num_frames=num_frames)
        train.add_movement((610, 250), time=num_frames, start_time_delta=0, mode='linear')
        # train.add_movement((0,20), 30, 10, mode='bounce', freq=4)
        return train
    elif train == 'ice_comic':
        train = ImageState('images/trains/' + train + '.png', (-570, 170), num_frames=num_frames)
        train.add_movement((520, 170), time=num_frames, start_time_delta=0, mode='linear')
        return train
    elif train == 'rb_vbb':
        train = ImageState('images/trains/' + train + '.png', (-1200, 270), num_frames=num_frames)
        train.add_movement((550, 270), time=num_frames, start_time_delta=0, mode='linear')
        return train
    elif train == 're_vbb':
        train = ImageState('images/trains/' + train + '.png', (-2500, 270), num_frames=num_frames)
        train.add_movement((580, 270), time=num_frames, start_time_delta=0, mode='linear')
        return train
    elif train == 'sbahn_vbb':
        train = ImageState('images/trains/' + train + '.png', (-1500, 270), num_frames=num_frames)
        train.add_movement((580, 270), time=num_frames, start_time_delta=0, mode='linear')
        return train
    else:
        return None


def create(scene, train=None, num_frames=50, connections=None, text=None):
    background = ImageStateFrame('images/background/' + scene + '.jpg', None)
    gif = GIFGenerator(gif_length=num_frames, bg=background)

    gif.add_foreground_object(rolling_train(train, num_frames=num_frames), 0)

    if connections:
        table = ImageState('images/table.png', (280, 10), num_frames=num_frames)
        gif.add_foreground_object(table, 0)
        print(connections)
        message = {
            'text': connections['start'] + ' --> ' + connections['destination'],
            'position': (290, 18),
            'color': (255, 255, 255, 0)}
        gif.add_message(message=message, start_frame=0, num_frames=50)
        position = (300, 50)
        for connection in connections['trains']:
            train_information = '{type} {time} Uhr +{delay} min auf Gleis {platform}'.format(
                type=connection['train'],
                platform=connection['platform'],
                time=connection['planned_departure'][11:16],
                delay=connection['delay'])
            # print(train_information)
            message = {
                'text': train_information,
                'position': position,
                'color': (255, 255, 255, 0)}
            gif.add_message(message=message, start_frame=0, num_frames=50)
            position = (position[0], position[1]+25)

    if text:
        message = {
            'text': text,
            'position': (20, 20),
            'color': (255, 30, 30, 0)
                  }
        gif.add_message(message=message, start_frame=20, num_frames=30)

    return gif.generate_gif()
