# some stuff for images

### Tested against Windows 10 / Python 3.11 / Anaconda

### pip install cythonimagever

### Cython and a C compiler must be installed! 

```PY
import numpy as np
import cv2
from cythonimagever import all_colors_in,any_colors_in,average_rgb,find_colors,rgb_color_count_numpy,rgb_color_count_sorted_by_qty_numpy,rgb_color_count_sorted_by_color_numpy
from a_cv_imwrite_imread_plus import open_image_in_cv
from time import perf_counter
# 4525 x 6623 x 3 picture https://www.pexels.com/pt-br/foto/foto-da-raposa-sentada-no-chao-2295744/
picpath = r"C:\Users\hansc\Downloads\pexels-alex-andrews-2295744.jpg"
picture = open_image_in_cv(picpath, channels_in_output=3)
colors1 = np.array(
    [
        (66, 71, 69),
        (62, 67, 65),
        (144, 155, 153),
        (52, 57, 55),
        (127, 138, 136),
        (53, 58, 56),
        (51, 56, 54),
        (32, 27, 18),
        (24, 17, 8),
        (10, 15, 122),
    ],
    dtype=np.uint8,
)
print(f'{rgb_color_count_numpy(picture, picture.shape) =}')
print(f'{rgb_color_count_sorted_by_qty_numpy(picture, picture.shape) =}')
print(f'{rgb_color_count_sorted_by_color_numpy(picture, picture.shape) =}')
print(f'{find_colors(picture, colors1) =}')
print(f'{average_rgb(picture) =}')
print(f'{any_colors_in(picture, colors1) =}')
print(f'{all_colors_in(picture, colors1) =}')

# rgb_color_count_numpy(picture, picture.shape) =array([[   0,    0,    0,   38],
#        [   1,    0,    0,   33],
#        [   3,    0,    0,   41],
#        ...,
#        [ 252,  255,  255,  183],
#        [ 254,  255,  255, 1495],
#        [ 255,  255,  255, 4588]], dtype=uint32)
# rgb_color_count_sorted_by_qty_numpy(picture, picture.shape) =array([[   132,     83,     76,      1],
#        [   184,     71,     31,      1],
#        [   189,     71,     31,      1],
#        ...,
#        [    12,     21,     26, 417740],
#        [    13,     22,     27, 418847],
#        [    11,     20,     25, 447605]], dtype=uint32)
# rgb_color_count_sorted_by_color_numpy(picture, picture.shape) =array([[   0,    0,    0,   38],
#        [   1,    0,    0,   33],
#        [   3,    0,    0,   41],
#        ...,
#        [ 252,  255,  255,  183],
#        [ 254,  255,  255, 1495],
#        [ 255,  255,  255, 4588]], dtype=uint32)
# find_colors(picture, colors1) =array([[ 127,  138,  136,   38,    0],
#        [  66,   71,   69, 4522,    0],
#        [  62,   67,   65, 4523,    0],
#        ...,
#        [  24,   17,    8, 4522, 6622],
#        [  24,   17,    8, 4523, 6622],
#        [  24,   17,    8, 4524, 6622]], dtype=int64)
# average_rgb(picture) =(76, 83, 85)
# any_colors_in(picture, colors1) =True
# all_colors_in(picture, colors1) =array([[ 66,  71,  69,   1],
#        [ 62,  67,  65,   1],
#        [144, 155, 153,   1],
#        [ 52,  57,  55,   1],
#        [127, 138, 136,   1],
#        [ 53,  58,  56,   1],
#        [ 51,  56,  54,   1],
#        [ 32,  27,  18,   1],
#        [ 24,  17,   8,   1],
#        [ 10,  15, 122,   0]], dtype=uint8)
```
