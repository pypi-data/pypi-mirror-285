from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.sdss import SDSS
import numpy as np
import matplotlib.pyplot as plt

from catalog_querry import get_sdss_catalog, get_random_coordinates

def test_get_random_coordinates():
    ra, dec = get_random_coordinates()
    assert ra >= 0
    assert ra <= 360
    assert dec >= -90
    assert dec <= 90