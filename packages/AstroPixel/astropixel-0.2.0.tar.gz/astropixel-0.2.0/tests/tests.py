import pytest
import numpy as np
import astropixel
from astropixel import catalog_querry
from astropixel import plot_stars
from astropixel import make_star
from astropixel.make_star import GaussianCrossPSF
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table

def test_generate_cross_psf():
    psf = GaussianCrossPSF(amplitude=1)
    x_center = 150
    y_center = 100
    stddev = 10
    background_factor = 0.1
    size = (300, 200)
    psf_cross = psf.generate_cross_psf(x_center, y_center, stddev, background_factor, size=size)
    assert psf_cross.shape == size
    assert np.max(psf_cross) == 1
    assert np.min(psf_cross) == 0
    assert np.argmax(psf_cross) == (150, 100)

if __name__ == "__main__":
    catalog_querry.get_2mass_catalog(SkyCoord(ra=0, dec=0, unit='deg'), 1*u.arcmin)
    test_generate_cross_psf()