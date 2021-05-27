from itertools import product

from PIL import Image

from algo.image_segmentation import Segmentator, gaussian


def draw_mask(size, s, t):
    mask = Image.new('RGB', size)

    for pixel in s:
        if pixel == 's':
            continue
        mask.putpixel(pixel, (0, 0, 0))

    for pixel in t:
        if pixel == 't':
            continue
        mask.putpixel(pixel, (255, 255, 255))

    return mask


# Configuration
neighbors = 8
lambda_ = 1.0
sigma = 1.0

# Rectangles with background and object
boxes = {
    './static/elefant-gr-320.jpg': (
        set(product(range(70), range(60))),
        set(product(range(120, 220), range(70, 140)))
    ),
    './static/fullmoon-gr-320.jpg': (
        set(product(range(100), range(100))),
        set(product(range(125, 180), range(100, 140)))
    ),
    './static/banana1-gr-320.jpg': (
        set(product(range(200), range(101))),
        set(product(range(125, 190), range(146, 195)))
    )
}

# Filename to run test on
filename = './static/elefant-gr-320.jpg'

image = Image.open(filename)
background, object = boxes[filename]

segmentator = Segmentator(image, neighbors, lambda_, gaussian(sigma))
s, t = segmentator.mark(object, background)

draw_mask(image.size, s, t).show()
