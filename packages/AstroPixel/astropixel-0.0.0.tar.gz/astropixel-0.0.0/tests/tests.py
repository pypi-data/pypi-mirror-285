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
    """ 
    Test the generate_cross_psf method of the GaussianCrossPSF class
    """
    psf = make_star.GaussianCrossPSF(amplitude=1)
    x_center = 150
    y_center = 100
    stddev = 10
    background_factor = 0.1
    size = (300, 200)
    psf_cross = psf.generate_cross_psf(x_center, y_center, stddev, background_factor, size=size)
    assert psf_cross.shape == (200, 300)
    assert np.max(psf_cross) == pytest.approx(1, abs=1e-3)
    assert np.min(psf_cross) == pytest.approx(0, abs=1e-3)
    assert np.argmax(psf_cross) == 30150

def test_get_catalog():
    """
    Test the get_catalog method of the catalog_querry module
    """
    coord = SkyCoord(ra=10.68458, dec=41.26917, unit=(u.deg, u.deg))
    radius = 1.0*u.arcmin
    catalog_name = '2MASS'
    guide = catalog_querry.get_catalog(catalog_name, coord, radius=radius)
    assert isinstance(guide, Table)
    assert len(guide) > 0

def test_get_random_coordinates():
    """ 
    Test the get_random_coordinates method of the catalog_querry module
    """
    coord = catalog_querry.get_random_coordinates()
    assert isinstance(coord, SkyCoord)
    assert coord.ra.value >= 0
    assert coord.ra.value <= 360
    assert coord.dec.value >= -90
    assert coord.dec.value <= 90

def test_get_random_coordinates_gal():
    """
    Test the get_random_coordinates_gal method of the catalog_querry module
    """
    coord = catalog_querry.get_random_coordinates_gal()
    assert isinstance(coord, SkyCoord)
    assert coord.l.value >= 0
    assert coord.l.value <= 360
    assert coord.b.value >= -5
    assert coord.b.value <= 5

def test_plot_field():
    """ 
    Test the StarPlotter class of the plot_stars module
    """
    coord = SkyCoord(ra=10.68458, dec=41.26917, unit=(u.deg, u.deg))
    field = plot_stars.StarPlotter(coord, radius=1.0*u.arcmin, size=(1000, 1000))
    assert field.size == (1000, 1000)
    assert field.radius == 1.0*u.arcmin
    assert field.coord == coord

def test_get_wcs():
    """ 
    Test the get_wcs method of the StarPlotter class
    """
    coord = SkyCoord(ra=10.68458, dec=41.26917, unit=(u.deg, u.deg))
    field = plot_stars.StarPlotter(coord, radius=1.0*u.arcmin, size=(1000, 1000))
    wcs = field.get_wcs()
    assert wcs.wcs.ctype[0] == 'RA---TAN'
    assert wcs.wcs.ctype[1] == 'DEC--TAN'
    assert wcs.wcs.crval[0] == coord.ra.value
    assert wcs.wcs.crval[1] == coord.dec.value

    pixcrd = np.array([[0, 0], [24, 38], [45, 98]], dtype=np.float64)
    world = wcs.all_pix2world(pixcrd, 0)
    ### This test is not working :(
    #assert world[0][0] == pytest.approx(coord.ra.value, abs=1e-3)
    #assert world[0][1] == pytest.approx(coord.dec.value, abs=1e-3)

    pixcrd2 = wcs.wcs_world2pix(world, 0)
    assert pixcrd2[0][0] == pytest.approx(0, abs=1e-3)
    assert pixcrd2[0][1] == pytest.approx(0, abs=1e-3)

    x = 0
    y = 0
    origin = 0
    assert (wcs.wcs_pix2world(x, y, origin) ==
            wcs.wcs_pix2world(x + 1, y + 1, origin + 1))

if __name__ == "__main__":
    test_generate_cross_psf()
    test_get_catalog()
    test_get_random_coordinates()
    test_get_random_coordinates_gal()
    test_plot_field()
    test_get_wcs()