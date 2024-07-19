cimport cython
import cython
cimport numpy as np
import numpy as np
from libc.stdlib cimport qsort

np.import_array()
cdef:
    cython.uint[:] values

cdef int cmpfunc (const void *a , const void *b) noexcept nogil:
    cdef cython.uint a_v = (<cython.uint *> a)[0]
    cdef cython.uint b_v = (<cython.uint *> b)[0]
    return (values[a_v] - values[b_v]);

def sort(np.ndarray py_values, cython.uint[:] perm, cython.uint N):
    global values
    values = py_values
    qsort(&perm[0], N, perm.strides[0], &cmpfunc)

cpdef np.ndarray rgb_color_count_numpy(np.ndarray pic_full, tuple picshape):
    cdef:
        Py_ssize_t len_picshape=len(picshape)
        np.ndarray arr=pic_full.reshape(-1, picshape[len_picshape - 1]).astype(np.uint32)
        np.ndarray afull=((arr[..., 0] << 16) + (arr[..., 1] << 8) + (arr[...,2])).astype(np.uint32)
        cython.uint[:] a = afull
        np.ndarray tmparray_full = np.zeros(256 * 256 * 256, dtype=np.uint32)
        cython.uint[:] tmparray = tmparray_full
        Py_ssize_t aindex = a.shape[0]
        Py_ssize_t v
        np.ndarray notnull_index, foundcolors

    with nogil:
        for v in range(aindex):
            tmparray[a[v]] += 1
    notnull_index = np.where(tmparray_full != 0)[0]
    foundcolors = notnull_index.astype(np.uint32).view(np.uint8).reshape((-1, 4)).astype(np.uint32)
    foundcolors[..., 3] = tmparray_full[notnull_index]
    return foundcolors

cpdef np.ndarray rgb_color_count_sorted_by_qty_numpy(np.ndarray pic_full, tuple picshape):
    cdef:
        np.ndarray allcolors,perm
    allcolors= rgb_color_count_numpy(pic_full, picshape)
    perm = np.arange(len(allcolors), dtype=np.uint32)
    sort(allcolors[...,3], perm,len(allcolors))
    return allcolors[perm]

cpdef np.ndarray rgb_color_count_sorted_by_color_numpy(np.ndarray pic_full, tuple picshape):
    cdef:
        Py_ssize_t len_picshape=len(picshape)
        np.ndarray arr=pic_full.reshape(-1, picshape[len_picshape - 1]).astype(np.uint32)
        np.ndarray afull=((arr[..., 0] << 16) + (arr[..., 1] << 8) + (arr[...,2])).astype(np.uint32)
        cython.uint[:] a = afull
        np.ndarray tmparray_full = np.zeros(256 * 256 * 256, dtype=np.uint32)
        cython.uint[:] tmparray = tmparray_full
        Py_ssize_t aindex = a.shape[0]
        Py_ssize_t v
        np.ndarray notnull_index, foundcolors, foundcolorsnew, perm

    with nogil:
        for v in range(aindex):
            tmparray[a[v]] += 1
    notnull_index = np.where(tmparray_full != 0)[0]
    foundcolors = notnull_index.astype(np.uint32)  #.view(np.uint8).reshape((-1, 4)).astype(np.uint32)
    perm = np.arange(len(foundcolors), dtype=np.uint32)
    sort(foundcolors, perm,len(foundcolors))
    foundcolorsnew=foundcolors.view(np.uint8).reshape((-1, 4)).astype(np.uint32)
    foundcolorsnew[..., 3] = tmparray_full[notnull_index]
    return foundcolorsnew[perm]

cpdef np.ndarray find_colors(cython.uchar[:,:,:] pic, cython.uchar[:,:] colors):
    cdef:
        Py_ssize_t shape0_pic = pic.shape[0]
        Py_ssize_t shape1_pic = pic.shape[1]
        Py_ssize_t shape0_colors = colors.shape[0]
        Py_ssize_t i,j,k
        Py_ssize_t resultcounter=0
        np.ndarray resultsfull = np.zeros((shape0_pic*shape1_pic,5),dtype=np.int64)
        Py_ssize_t[:,:] results = resultsfull

    with nogil:
        for i in range(shape0_pic):
            for j in range(shape1_pic):
                for k in range(shape0_colors):
                    if (pic[i][j][0] == colors[k][0] ) and (pic[i][j][1] == colors[k][1] ) and (pic[i][j][2] == colors[k][2] ):
                        results[resultcounter][0]=colors[k][0]
                        results[resultcounter][1]=colors[k][1]
                        results[resultcounter][2]=colors[k][2]
                        results[resultcounter][3]=j
                        results[resultcounter][4]=i
                        resultcounter+=1
                        break
    return resultsfull[:resultcounter]

cpdef tuple average_rgb(cython.uchar[:,:,:] pic):
    cdef:
        Py_ssize_t shape0_pic = pic.shape[0]
        Py_ssize_t shape1_pic = pic.shape[1]
        Py_ssize_t i,j
        Py_ssize_t resultcounter=shape0_pic*shape1_pic
        Py_ssize_t r=0
        Py_ssize_t g=0
        Py_ssize_t b=0
    with nogil:
        for i in range(shape0_pic):
            for j in range(shape1_pic):
                b+=pic[i][j][0]
                g+=pic[i][j][1]
                r+=pic[i][j][2]


    return b//resultcounter, g//resultcounter, r//resultcounter

cpdef bint any_colors_in(cython.uchar[:,:,:] pic, cython.uchar[:,:] colors):
    cdef:
        Py_ssize_t shape0_pic = pic.shape[0]
        Py_ssize_t shape1_pic = pic.shape[1]
        Py_ssize_t shape0_colors = colors.shape[0]
        Py_ssize_t i,j,k

    with nogil:
        for i in range(shape0_pic):
            for j in range(shape1_pic):
                for k in range(shape0_colors):
                    if (pic[i][j][0] == colors[k][0] ) and (pic[i][j][1] == colors[k][1] ) and (pic[i][j][2] == colors[k][2] ):
                        return True
    return False

cpdef np.ndarray all_colors_in(cython.uchar[:,:,:] pic, cython.uchar[:,:] colors):
    cdef:
        Py_ssize_t shape0_pic = pic.shape[0]
        Py_ssize_t shape1_pic = pic.shape[1]
        Py_ssize_t shape0_colors = colors.shape[0]
        Py_ssize_t i,j,k
        np.ndarray results_full = np.zeros((colors.shape[0],colors.shape[1]+1),dtype=np.uint8)
        cython.uchar[:,:] results = results_full
        Py_ssize_t resultscounter=0

    for k in range(shape0_colors):
        results[k][0] = colors[k][0]
        results[k][1] = colors[k][1]
        results[k][2] = colors[k][2]
    with nogil:
        for i in range(shape0_pic):
            for j in range(shape1_pic):
                for k in range(shape0_colors):
                    if results[k][3]==1:
                        continue
                    if (pic[i][j][0] == colors[k][0] ) and (pic[i][j][1] == colors[k][1] ) and (pic[i][j][2] == colors[k][2] ):
                        results[k][3]=1
                        resultscounter+=1
                        if resultscounter == shape0_colors:
                            with gil:
                                return results_full
                        break
    return results_full
