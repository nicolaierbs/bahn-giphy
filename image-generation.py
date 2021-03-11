import imageio
import os
from pygifsicle import optimize
from PIL import Image

im_landscape = Image.open(r'images/landscape-winter.jpg')
im_train = Image.open(r'images/train_ice2.png')

images = list()
y=180
for i in range(55):
    image = im_landscape.copy()
    x = i*20-550
    image.paste(im_train, (x, y), mask=im_train)
    images.append(image)

output_gif = 'output/bahn-giphy.gif'
imageio.mimsave(output_gif, images)
optimize(output_gif)
