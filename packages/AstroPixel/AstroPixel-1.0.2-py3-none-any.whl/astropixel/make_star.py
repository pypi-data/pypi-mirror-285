import numpy as np
import matplotlib.pyplot as plt

class GaussianCrossPSF(object):
    """ 
    Class to generate star-like pixel art using Gaussian function and masking.
    """
    def __init__(self, amplitude=1):
        """
        Initialize the GaussianCrossPSF class

        Args:
            amplitude (float): Amplitude of the Gaussian function
        
        """
        self.amplitude = amplitude

    def generate_cross_psf(self, x_center, y_center, stddev, background_factor, size=(300, 200)):
        """
        Generate Stars using Gaussian

        Function to generate a star-like pixel art using gaussian function and masking.

        Args:
            x_center (float): x coordinate of the center of the star
            y_center (float): y coordinate of the center of the star
            stddev (float): Standard deviation of the Gaussian function to control the size
            background_factor (float): A number from 0 to 1 to tune the masking
            size (tuple): Size of the output image

        Returns:
            np.ndarray: A 2D numpy array representing the star
        
        """
        x = np.linspace(0, size[0]-1, size[0])
        y = np.linspace(0, size[1]-1, size[1])
        x, y = np.meshgrid(x, y)
        
        # Calculate the Gaussian
        psf = self.amplitude * np.exp(-((x - x_center)**2 + (y - y_center)**2) / (2 * stddev**2))
        
        # Calculate the Gaussian along the x and y axes
        psf_x = self.amplitude * np.exp(-((x - x_center)**2) / (2 * stddev**2))
        psf_y = self.amplitude * np.exp(-((y - y_center)**2) / (2 * stddev**2))
        
        # Create a mask that retains higher values along the x and y axes
        mask_x = np.abs(y - y_center) <= 1e-5
        mask_y = np.abs(x - x_center) <= 1e-5
        
        # Apply the mask to the PSF values
        psf_cross = background_factor * psf
        psf_cross[mask_x] = psf_x[mask_x]
        psf_cross[mask_y] = psf_y[mask_y]
        
        return psf_cross

    def plot_multiple_cross_psfs(self, centers_stddevs, size=(300, 200)):
        """
        Plot Multiple Stars
        
        Function to plot multiple star-like pixel art using gaussian function and masking.

        Args:
            centers_stddevs (list): A list of tuples containing the x_center, y_center, stddev, and background_factor of each star
            size (tuple): Size of the output image

        """

        combined_psf = np.zeros((size[1], size[0]))
        
        for (x_center, y_center, stddev, background_factor) in centers_stddevs:
            psf_cross = self.generate_cross_psf(x_center, y_center, stddev, background_factor, size=size)
            combined_psf += psf_cross
        
        plt.figure(figsize=(6, 6))
        plt.imshow(combined_psf, extent=(0, size[0]-1, 0, size[1]-1), origin='lower')
        plt.colorbar()
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

# Example:
def main():
    psf = GaussianCrossPSF(amplitude=1)
    centers_stddevs = [(5, 5, 2.5, 0.5), (10, 20, 3, 0.4), (25, 10, 5, 0.4)]
    psf.plot_multiple_cross_psfs(centers_stddevs, size=(100, 67))

if __name__ == '__main__':
    main()
