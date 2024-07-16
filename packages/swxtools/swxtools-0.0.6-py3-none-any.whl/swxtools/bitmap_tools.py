import matplotlib as mpl
import numpy as np
import numpngw


def array_to_colormap_array(data, cmapname, zmin, zmax,
                            nancolor=np.array([0.5, 0.5, 0.5]),
                            dtype=np.uint16):
    cmap = mpl.colormaps[cmapname]
    norm = mpl.colors.Normalize(vmin=zmin, vmax=zmax)
    z = np.flip(data, axis=0)
    cmapped = cmap(norm(z))[:, :, 0:3]
    imagedata = np.zeros((*np.shape(z), 3), dtype=dtype)
    imagedata[:, :, 0:3] = (65535*cmapped).astype(dtype)
    imagedata[np.isnan(data), 0:3] = 65535*nancolor
    # imagedata[:, :, 3] = 1  # Alpha channel
    return imagedata


def array_to_colormap_png(data, filename, cmapname, zmin, zmax,
                          dtype=np.uint16, transparent=None):
    color_data = array_to_colormap_array(
        data=data,
        cmapname=cmapname,
        zmin=zmin,
        zmax=zmax,
        dtype=dtype
    )
    numpngw.write_png(filename, color_data, transparent=transparent)
