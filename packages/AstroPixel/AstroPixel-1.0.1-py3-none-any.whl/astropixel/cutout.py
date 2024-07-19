from astropy.nddata import Cutout2D
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from spectral_cube import SpectralCube


def get_cutout_fn(filename, position, l, w, format='fits'):
    if format == 'fits':
        try: 
            hdu = fits.open(filename)
            data = np.squeeze(hdu['SCI'].data)
            head = hdu['SCI'].header
        except: 
            hdu = fits.open(filename)[0]
            data = np.squeeze(hdu.data)
            head = hdu.header
    elif format == 'casa':
        hdu = SpectralCube.read(filename, format='casa').hdu
        data = np.squeeze(hdu.data)
        head = hdu.header
    ww = WCS(head).celestial
    size = (l, w)
    cutout = Cutout2D(data, position=position, size=size, wcs=ww)
    return cutout

def get_cutout_hdu(hdu, position, l, w):
    data = np.squeeze(hdu.data)
    head = hdu.header
    ww = WCS(head).celestial
    size = (l, w)
    cutout = Cutout2D(data, position=position, size=size, wcs=ww)
    return cutout

