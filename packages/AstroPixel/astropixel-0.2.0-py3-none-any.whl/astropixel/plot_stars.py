from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.visualization import simple_norm

import numpy as np

import matplotlib.pyplot as plt

from . import catalog_querry
from . import make_star


class StarPlotter(object):
    """ 
    Object for plotting stars
    """

    def __init__(self, coord, size=(1000, 1000), radius=1*u.arcmin, catalog_name='2MASS'):
        """ 
        Initialize the class

        Args:
            coord (SkyCoord): Coordinates of the center of the field.
            size (tuple): Size of the field in pixels.
            radius (Quantity): Radius of the field.

        """

        self.coord = coord
        self.size = size
        self.size_scale = np.min(size)/10
        self.radius = radius
        self.scale = radius*2
        self.R = None
        self.G = None
        self.B = None
        self.catalog_name = catalog_name
        self.set_catalog(catalog_name)
        self.wcs = self.get_wcs()
        self.crosshair = False
    
    def set_catalog(self, catalog_name):
        """ 
        Function to get catalog

        Returns:
            Table: Table of stars.
        """
        self.catalog_name = catalog_name

        if catalog_name == '2MASS':
            self.cat = catalog_querry.get_2mass_catalog(self.coord, self.radius)
            self.R = 'Kmag'
            self.G = 'Hmag'
            self.B = 'Jmag'
        elif catalog_name == 'SDSS':
            self.cat = catalog_querry.get_sdss_catalog(self.coord, self.radius)
            self.R = 'r'
            self.G = 'g'
            self.B = 'u'
        else:
            self.cat = catalog_querry.get_catalog(catalog_name, self.coord, self.radius)
    
    def get_wcs(self):
        """ 
        Function to get WCS

        Returns:
            WCS: WCS object.
        """
        wcs = WCS(naxis=2)
        wcs.wcs.crpix = [self.size[0]/2, self.size[1]/2]  # Set the reference pixel to the center of the image
        wcs.wcs.crval = [self.coord.ra.deg, self.coord.dec.deg]  # Set the reference value to the given coordinates
        wcs.wcs.cdelt = np.array([-self.scale.to(u.deg).value/self.size[0], self.scale.to(u.deg).value/self.size[1]])  # Set the pixel scale 
        wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]  # Set the coordinate type to RA/DEC

        return wcs

    def plot_crosshair(ax):
        """
        Function to plot crosshair

        Args:
            ax (Axes): Axes object.

        Returns:
            ax (Axes): Axes object.
        """

        ax.scatter(self.coord.ra.deg, self.coord.dec.deg, s=100, edgecolor='r', facecolor='none')
        ax.scatter(self.coord.ra.deg, self.coord.dec.deg, s=100, marker='+', color='r')
        return ax

    def plot_scatter_field(self, labels=False, ax=None):
        """
        Function to plot field with scatter

        Args:
            labels (bool): Show labels.
            ax (Axes): Axes object.

        Returns:
            ax (Axes): Axes object.
        """

        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection=self.wcs)

        ax.scatter(self.cat['RAJ2000'], self.cat['DEJ2000'], s=50, transform=ax.get_transform('world'), marker='*', color='orange')
        if self.crosshair:
            ax = self.plot_crosshair(ax)

        if labels:
            ax.set_xlabel('Right Ascension')
            ax.set_ylabel('Declination')
        else:
            ax.set_axis_off()

        plt.tight_layout()
        return ax

    def get_cross_psf_field_image(self, band='Kmag'):
        """
        Function to get cross PSF field image

        Args:
            band (str): Band to use. Must match the column name in the catalog self.cat

        Returns:
            np.ndarray: Image of the field with cross PS
        """
        star = make_star.GaussianCrossPSF(amplitude=1)
        psf = np.zeros((self.size[1], self.size[0]))

        for c in self.cat:
            coordi = SkyCoord(c['RAJ2000'], c['DEJ2000'], unit=(u.deg, u.deg), frame='icrs')
            pix_cord = coordi.to_pixel(self.wcs)
            std = scale_the_magnitude(c[band], scale=5)*self.size_scale
            psf += star.generate_cross_psf(np.round(pix_cord[0]), np.round(pix_cord[1]), std, 0.5, size=self.size)
        
        return psf

    def plot_cross_psf_field(self, labels=False, ax=None):
        """
        Function to plot cross PSF field with imshow

        Args:
            labels (bool): Show labels.
            ax (Axes): Axes object.

        Returns:
            ax (Axes): Axes object.
        """
        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection=self.wcs)

        psf = self.get_cross_psf_field_image(band=self.R)

        ax.imshow(psf, origin='lower', cmap='gray', aspect='equal')
        if labels:
            ax.set_xlabel('Right Ascension')
            ax.set_ylabel('Declination')
        else:
            ax.set_axis_off()
        
        if self.crosshair:
            ax = self.plot_crosshair(ax)
        
        return ax

    def plot_cross_psf_field_rgb(self, labels=False, ax=None):
        """
        Function to plot cross PSF field with imshow

        Args:
            labels (bool): Show labels.
            ax (Axes): Axes object.

        Returns:
            ax (Axes): Axes object.
        """
        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection=self.wcs)

        #psf = self.get_cross_psf_field_image(band='Kmag')
        psf_R = self.get_cross_psf_field_image(band=self.R)
        psf_G = self.get_cross_psf_field_image(band=self.G)
        psf_B = self.get_cross_psf_field_image(band=self.B)
        
        rgb = make_rgb_scaled_image(psf_R, psf_G, psf_B)

        ax.imshow(rgb, origin='lower', aspect='equal')
        if labels:
            ax.set_xlabel('Right Ascension')
            ax.set_ylabel('Declination')
        else:
            ax.set_axis_off()

        if self.crosshair:
            ax = self.plot_crosshair(ax)
        
        return ax

def make_rgb_scaled_image(psf_R, psf_G, psf_B):
    """
    Function to make RGB image

    Args:
        psf_R (np.ndarray): Image of the field for the R color.
        psf_G (np.ndarray): Image of the field for the G color.
        psf_B (np.ndarray): Image of the field for the B color.

    Returns:
        np.ndarray: RGB image.
    """
    rgb = np.array(
        [
            psf_R,
            psf_G,
            psf_B
        ]
    ).swapaxes(0,2).swapaxes(0,1)

    rgb_scaled = np.array([
            simple_norm(rgb[:,:,0], stretch='asinh', min_cut=0, max_cut=1)(rgb[:,:,0]),
            simple_norm(rgb[:,:,1], stretch='asinh', min_cut=0, max_cut=1)(rgb[:,:,1]),
            simple_norm(rgb[:,:,2], stretch='asinh', min_cut=0, max_cut=1)(rgb[:,:,2]),
        ]
    ).swapaxes(0,2)

    return rgb_scaled.swapaxes(0,1)

def plot_random_scatter_field(size=(1000, 1000), radius=1*u.arcmin, ax=None):
    """
    Function to plot random field.

    Args:
        size (tuple): Size of the field in pixels.
        radius (Quantity): Radius of the field.
        ax (Axes): Axes object.

    Returns:
        ax (Axes): Axes object.
    """
    coord = catalog_querry.get_random_coordinates_gal()
    field = StarPlotter(coord, radius=radius, size=size)
    field.plot_field(ax=ax)

def magnitude_to_luminosity(magnitude):
    """ 
    Function to convert magnitude to luminosity

    Args:
        magnitude (float): Magnitude of the star.

    Returns:
        float: Luminosity of the star

    """
    # Convert magnitude to flux
    flux = 10**(-0.4 * magnitude)
    
    # Convert flux to luminosity
    luminosity = 4 * np.pi * (10)**2 * flux
    
    return luminosity

def scale_the_magnitude(magnitude, scale=5):
    """ 
    Function to scale the magnitude

    Args:
        magnitude (float): Magnitude of the star.
        scale (float): Scale factor.

    Returns:
        float: Scaled magnitude.
    """
    lum = magnitude_to_luminosity(magnitude)

    return lum**(1/scale)

def example_plot_scatter_field(ax=None):
    """
    Example to plot scatter field

    Args:
        ax (Axes): Axes object.

    Returns:
        ax (Axes): Axes object.
    """
    coord = SkyCoord.from_name('Barnard\'s Star')
    field = StarPlotter(coord, size=(1000, 1000), radius=1*u.arcmin)

    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = plt.subplot(111, projection=field.wcs)

    ax = field.plot_scatter_field(ax=ax)
    plt.show()

def example_plot_cross_psf_field(ax=None):
    """ 
    Example to plot cross PSF field

    Args:
        ax (Axes): Axes object.

    Returns:
        ax (Axes): Axes object.
    """

    coord = SkyCoord.from_name('Barnard\'s Star')
    field = StarPlotter(coord, size=(1000, 1000), radius=1*u.arcmin)

    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax = plt.subplot(111, projection=field.wcs)
    
    ax = field.plot_cross_psf_field(ax=ax)
    plt.show()

def example_plot_cross_psf_field_rgb():
    """
    Example to plot cross PSF field RGB
    """
    coord = SkyCoord.from_name('Barnard\'s Star')
    field = StarPlotter(coord, size=(50, 100), radius=1*u.arcmin)

    fig = plt.figure(figsize=(10, 8))
    ax = plt.subplot(111, projection=field.wcs)
    
    ax = field.plot_cross_psf_field_rgb(ax=ax)
    plt.show()

def main():
    #example_plot_cross_psf_field()
    example_plot_cross_psf_field_rgb()

if __name__ == '__main__':
    main()