from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier
import numpy as np
import matplotlib.pyplot as plt

def get_catalog(catalog_name, coord, radius=1.0*u.arcmin):
    """ Get Catalog
    
    Function to get catalog at a given coordinate and radius using Vizier.

    Args:
        catalog_name (str): Name of the catalog.
        coord (SkyCoord): Coordinates of the center of the search.
        radius (Quantity): Radius of the search.

    Returns:
        Table: Table of the catalog.

    """
    try:
        guide = Vizier(catalog=catalog_name).query_region(coord, radius=radius)[0]
    except:
        print("No catalog found. Setting 2MASS catalog.")
        guide = get_2mass_catalog(coord, radius)

    return guide

def get_2mass_catalog(coord, radius=1.0*u.arcmin):
    """ Query 2MASS Catalog
    
    Function to get 2MASS catalog at a given coordinate and radius using Vizier.

    Args:
        coord (SkyCoord): Coordinates of the center of the search.
        radius (Quantity): Radius of the search.

    Returns:
        Table: Table of the 2MASS catalog.

    """
    guide = Vizier(catalog="II/246").query_region(coord, radius=radius)[0]
    return guide

def get_sdss_catalog(coord, radius=1.0*u.arcmin):
    """ Query SDSS Catalog
    
    Function to get SDSS catalog at a given coordinate and radius using Vizier.

    Args:
        coord (SkyCoord): Coordinates of the center of the search.
        radius (Quantity): Radius of the search.

    Returns:
        Table: Table of the SDSS catalog.

    """
    guide = Vizier(catalog="V/147").query_region(coord, radius=radius)[0]
    return guide

def get_random_coordinates():
    """ Get Random Coordinates

    Function to generate a random SkyCoord object.

    Returns:
        SkyCoord: Random SkyCoord object.
    """
    ra = np.random.uniform(0, 360)
    dec = np.random.uniform(-90, 90)
    return SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')

def get_random_coordinates_gal():
    """ Get Random Coordinates in Galactic Coordinates

        Function to generate a random SkyCoord object in Galactic coordinates within -5 < b < 5.

        Returns:
            SkyCoord: Random SkyCoord object in Galactic coordinates within -5 < b < 5.
    """
    l = np.random.uniform(0, 360)
    b = np.random.uniform(-5, 5)
    return SkyCoord(l=l, b=b, unit=(u.deg, u.deg), frame='galactic')
