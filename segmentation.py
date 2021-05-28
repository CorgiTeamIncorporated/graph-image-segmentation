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
    './graph-image-segmentation/static/elefant-gr-320.jpg': (
        set(product(range(70), range(60))),
        set(product(range(120, 220), range(70, 140)))
    ),
    './graph-image-segmentation/static/fullmoon-gr-320.jpg': (
        set(product(range(100), range(100))),
        set(product(range(125, 180), range(100, 140)))
    ),
    './graph-image-segmentation/static/banana1-gr-320.jpg': (
        set(product(range(200), range(101))),
        set(product(range(125, 190), range(146, 195)))
    ),
    './graph-image-segmentation/static/cat-purr-icon.png': (
        set(product(range(7), range(31, 45))),
        set(product(range(11, 22), range(25, 32)))
    )
}

# Filename to run test on
filename = './graph-image-segmentation/static/elefant-gr-320.jpg'

image = Image.open(filename).convert('L')
background, object = boxes[filename]

segmentator = Segmentator(image, neighbors, lambda_, gaussian(sigma))
s, t = segmentator.mark(object, background)

draw_mask(image.size, s, t).show()

s, t = segmentator.mark(background_pixels=set(product(range(290, 310),
                                                      range(10))))

draw_mask(image.size, s, t).show()
