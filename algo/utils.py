import numpy as np


def generate_mask(s, t, shape):
    mask = np.zeros(shape)

    s.remove('s')
    t.remove('t')

    for px, py in s:
        mask[py, px] = 1

    for px, py in t:
        mask[py, px] = 0

    return mask


def jaccard_score(mask1, mask2):
    mask1 = mask1.astype(int)
    mask2 = mask2.astype(int)
    numerator = np.sum(mask1 & mask2)
    # denominator = np.sum(mask1 | mask2)
    denominator = np.sum((mask1 + mask2) > 0)
    print(numerator)
    print(denominator)
    return numerator/denominator


def correctness_ratio(mask1, mask2):
    mask1 = mask1.astype(int)
    mask2 = mask2.astype(int)
    mask1_inv = (mask1 + 1) - 2*mask1
    mask2_inv = (mask2 + 1) - 2*mask2
    numerator = np.sum(mask1 & mask2) + np.sum(mask1_inv & mask2_inv)
    denominator = mask1.shape[0]*mask1.shape[1]
    return numerator/denominator
