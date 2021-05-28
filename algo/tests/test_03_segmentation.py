from itertools import product

import numpy as np
from algo.image_segmentation import Segmentator, gaussian
from algo.utils import correctness_ratio, generate_mask, jaccard_score
from PIL import Image


def test_1():
    neighbors = 8
    lambda_ = 1.0
    sigma = 1.0

    boxes = {
        '/elefant-gr-320.jpg': (
            set(product(range(70), range(60))),
            set(product(range(120, 220), range(70, 140)))
        )
    }

    images_folder = './algo/tests/segmentation_test_imputs'
    masks_folder = './algo/tests/segmentation_test_outputs'

    filename = '/elefant-gr-320.jpg'

    im = Image.open(images_folder + filename).convert('L')
    mask_true = np.array(Image.open(masks_folder + filename).convert('L'))

    print(type(mask_true))
    background, object = boxes[filename]

    segmentator = Segmentator(im, neighbors, lambda_, gaussian(sigma))
    s, t = segmentator.mark(object, background)

    mask_ours = generate_mask(s, t, mask_true.shape)

    print('Jaccard:', jaccard_score(mask_true, mask_ours))
    print('Correctness ratio:', correctness_ratio(mask_true, mask_ours))
