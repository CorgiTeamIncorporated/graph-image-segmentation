from itertools import product

import numpy as np
from skimage.transform import rescale


def generate_mask(s, t, shape):
    mask = np.zeros(shape)

    s.remove('s')
    t.remove('t')

    for px, py in s:
        mask[py, px] = 1

    for px, py in t:
        mask[py, px] = 0

    return mask


def scale_cut(s, t, shape, scale):
    mask = np.zeros(shape)

    if 's' in s:
        s.remove('s')
    if 't' in t:
        t.remove('t')

    for px, py in s:
        mask[py, px] = 1
    for px, py in t:
        mask[py, px] = 2

    rescaled = rescale(mask, scale, order=0)
    height, width = rescaled.shape

    # print(1 in rescaled)

    new_s = set((x, y)
                for (x, y) in product(range(width), range(height))
                if rescaled[y, x] == 1)
    new_t = set((x, y)
                for (x, y) in product(range(width), range(height))
                if rescaled[y, x] == 2)

    return new_s, new_t


def jaccard_score(mask1, mask2):
    mask1 = mask1.astype(int)
    mask2 = mask2.astype(int)
    numerator = np.sum(mask1 & mask2)
    denominator = np.sum(mask1 | mask2)
    return numerator/denominator


def correctness_ratio(mask1, mask2):
    mask1 = mask1.astype(int)
    mask2 = mask2.astype(int)
    mask1_inv = (mask1 + 1) - 2*mask1
    mask2_inv = (mask2 + 1) - 2*mask2
    numerator = np.sum(mask1 & mask2) + np.sum(mask1_inv & mask2_inv)
    denominator = mask1.shape[0]*mask1.shape[1]
    return numerator/denominator
