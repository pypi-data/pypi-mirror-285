from typing import Union
from astropy.io import fits
import astropy.constants as const
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def gaussian(x: np.array, lineFlux: float, cent_wave: float, sigma: float, cont: float) -> np.array:
    """
    Compute a Gaussian function with specified astronomical spectrum line parameters.

    Parameters
    ----------
    x: np.array
        The array of wavelength values.
    lineFlux: float
        The integrated flux of the line (the area under the Gaussian curve).
    cent_wave: float
        The central wavelength of the Gaussian peak.
    sigma: float
        The standard deviation of the Gaussian distribution (defines the width of the peak).
    cont: float
        The continuum level (a constant value added to the Gaussian).

    Returns
    ----------
    : np.array
        The computed Gaussian function values at each wavelength in x.

    Notes
    ----------
    - The Gaussian function is defined as: f(x) = (1/(sigma * sqrt(2 * pi))) * lineFlux * exp(-(x - cent_wave)**2 / (2 * sigma**2)) + cont
    """
    return (1/sigma*np.sqrt(2*np.pi))*lineFlux * np.exp(-(x - cent_wave)**2 / (2 * sigma**2)) + cont


def reduced_Chi2(model: np.array, obs: np.array, err: np.array) -> float:
    """
    Calculate the reduced chi-squared (χ²) statistic for assessing the goodness of fit.

    Parameters
    ----------
    model: np.array
        The array of model values or predicted data.
    obs: np.array 
        The array of observed or experimental data.
    err: np.array 
        The array of uncertainties or errors associated with the observed data.

    Returns
    ----------
    : float
        The reduced chi-squared statistic, a measure of the goodness of fit between the model and observed data.
    
    Notes
    ----------
    - The reduced chi-squared statistic is calculated using the formula: χ²_reduced = 0.5 * Σ[((model - obs) / err)²] where Σ denotes the sum over all data points. This statistic is used to evaluate how well the model fits the observed data. Lower values indicate a better fit.
    """
    return 0.5*np.sum(((model - obs)/err)**2.)


class Galaxy():
    """
    A class representing the spectral information of a galaxy.

    This class can be initialized with a zCOSMOS ID, in which case it retrieves the associated spectroscopic redshift and 1D spectra
    from the zCOSMOS 20K catalog. Alternatively, it can be initialized with user-provided spectral data.

    Parameters
    ----------
    id : int
        The Galaxy ID or zCOSMOS ID. This is used to cross-match with the zCOSMOS 20K catalog to retrieve the spectroscopic redshift and 1D spectra if no other spectral data is provided.
    zSpec : float, optional
        Spectroscopic redshift of the galaxy. This is used if the galaxy data is provided directly and not retrieved from the zCOSMOS catalog. Default is None.
    wave : np.array, optional
        Array of wavelength values for the galaxy's spectrum. This is used if the data is provided directly. Default is None.
    flux : np.array, optional
        Array of flux values for the galaxy's spectrum. This is used if the data is provided directly. Default is None.
    err : np.array, optional
        Array of error values for the galaxy's spectrum. This is used if the data is provided directly. Default is None.

    Notes
    -----
    - If only the Galaxy ID is provided, the class will attempt to retrieve the spectroscopic redshift and 1D spectra from the zCOSMOS 20K catalog.
    - The retrieved or provided 1D spectra will include wavelength, flux, and error values.
    - The class prints the range of observed rest-frame wavelengths covered by the spectrum.

    Methods
    -------
    find_z_spec()
        Retrieves the spectroscopic redshift from the zCOSMOS catalog based on the Galaxy ID.
    retrieve_1dspec()
        Retrieves the 1D spectrum from the examples folder based on the Galaxy ID.
    """

    def __init__(self, id: int, zSpec: float = None, wave: np.array = None, flux: np.array = None, err: np.array = None):
        """
        Initialize the Galaxy object with either a zCOSMOS ID or user-provided spectral data.

        Parameter:
        ------------
        id: int 
            The Galaxy ID or zCOSMOS ID used to retrieve the galaxy's data.
        zSpec: float, optional
            Spectroscopic redshift of the galaxy. Default is None.
        wave: np.array, optional
            Array of wavelength values for the galaxy's spectrum. Default is None.
        flux: np.array, optional
            Array of flux values for the galaxy's spectrum. Default is None.
        err: np.array, optional
            Array of error values for the galaxy's spectrum. Default is None.

        Raise:
        ------------
        TypeError: If the provided ID is not of type integer when it is expected to be a zCOSMOS ID.

        Notes:
        ------------
        - If `wave`, `flux`, and `err` are None and `zSpec` is also None, the class will use the provided `id` to retrieve the spectroscopic redshift
          and 1D spectrum from the zCOSMOS catalog.
        - If any of `wave`, `flux`, or `err` are provided, the class will use these values directly, bypassing the retrieval process.
        - The class prints the range of rest-frame wavelengths covered by the observed spectrum.
        """
        self.id = id

        # This will take in the zCOSMOS data
        if (wave is None) and (flux is None) and (err is None) and (zSpec is None):
            
            # test to make sure that the zCOSMOS ID is an integer
            if type(self.id) != int:
                raise TypeError("zCOSMOS ID needs to be of type integer")
            
            self.zSpec = self.find_z_spec()            
            self.wave,self.flux,self.err = self.retrieve_1dspec()
        
        # Otherwise use the user-input data
        else:
            self.zSpec = zSpec
            self.wave = wave
            self.flux = flux
            self.err = err

        # Rest-Frame Wavelength Range Observed
        print(
            f"Spectra covers rest-frame wavelengths between {np.min(self.wave)/(1.+self.zSpec)} and {np.max(self.wave)/(1.+self.zSpec)} Angstroms")

    #
    def find_z_spec(self) -> Union[float, ValueError]:
        """
        Retrieve the spectroscopic redshift from the zCOSMOS catalog based on the object's ID.

        Attempts to open the zCOSMOS FITS file from two possible locations. Searches the catalog for the entry with the matching
        object ID and returns the corresponding spectroscopic redshift. Raises a ValueError if the ID is not found in the catalog.

        Returns
        -------
        float
            The spectroscopic redshift of the object if the ID is found in the catalog.
            
        Raises
        ------
        ValueError
            If the object ID is not found in the zCOSMOS catalog.
        """
        try:
            data = fits.open('data/zCOSMOS_20K.fits')[1].data
        except:
            data = fits.open('../data/zCOSMOS_20K.fits')[1].data

        this_one = data['object_id'] == self.id

        if True in this_one:
            return data['Redshift'][this_one][0]
        else:
            raise ValueError("ID is not in catalog")

    def retrieve_1dspec(self) -> tuple:
        """
        Load and return the 1D spectrum data for the given object ID.

        Attempts to open the 1D FITS file from two possible locations. Extracts and returns the wavelength, flux, and error arrays
        from the FITS data. If the error array is not available, a default error estimate based on a 20% uncertainty in flux calibration
        is used.

        Returns
        -------
        tuple
            A tuple containing three numpy arrays:
            - wave (np.array): The array of wavelength values.
            - flux (np.array): The array of flux values.
            - err (np.array): The array of error values. If not present in the FITS file, a 20% uncertainty in flux is used as the error estimate.
        """
        try:
            spec_1d = fits.open(f'examples/{self.id}_1d.fits')[1].data
        except:
            spec_1d = fits.open(f'../examples/{self.id}_1d.fits')[1].data

        wave = spec_1d['WAVE'][0]
        flux = spec_1d['FLUX_REDUCED'][0]
        # err = spec_1d['ERR'][0]
        # TODO: zCOSMOS has 0 for error but says there is 20% uncertainty in the fluxcalibration
        err = np.abs(0.2*flux)
        return (wave, flux, err)

    def run_line(self, linewave: float, **kwargs) -> 'Line':
        """
        Instantiate a Line object with the specified wavelength and optional parameters.

        Creates and returns an instance of the `Line` class, initializing it with the provided wavelength and any additional keyword arguments.

        Parameters
        ----------
        linewave : float
            The central wavelength of the emission line.
        **kwargs
            Additional keyword arguments to be passed to the `Line` class constructor.

        Returns
        -------
        Line
            An instance of the `Line` class, initialized with the provided wavelength and optional parameters.

        Notes
        -----
        - Ensure that the `Line` class is properly defined in the context where this method is used.
        - This method assumes that the `Line` class is defined as a nested class or accessible within the scope of this method.
        """
        return self.Line(self, linewave, **kwargs)

    class Line():
        """
        This class defines the measurement of emission line profiles in astronomical spectra.

        Parameters
        ----------
        galaxy : Galaxy
            The galaxy object that contains the 1D spectra and redshift information.
        linewave : float
            The central wavelength of the emission line to be fitted.
        window : int, optional
            The wavelength window around the emission line for fitting. Default is 40 Angstroms.
        plot : bool, optional
            Whether to plot the observed and fitted spectra. Default is True.

        Methods
        -------
        check_input_in_wave_coverage()
            Validates if the emission line wavelength is within the 1D spectral coverage.
        fit()
            Fits a Gaussian profile to the emission line and returns the best-fit parameters and their errors.
        """

        def __init__(self, galaxy: 'Galaxy', linewave: float, window: int = 40, plot: bool = True):
            """
            Initialize the Line object with galaxy data and emission line parameters.

            Parameters
            ----------
            galaxy : Galaxy
                The galaxy object that contains the 1D spectra and redshift information.
            linewave : float
                The central wavelength of the emission line to be fitted.
            window : int, optional
                The wavelength window around the emission line for fitting. Default is 40 Angstroms.
            plot : bool, optional
                Whether to plot the observed and fitted spectra. Default is True.
            """
            self.galaxy = galaxy
            self.linewave = linewave
            self.window = window
            self.plot = plot

            # This will trigger a check if wavelength inputted is in the 1D spectral coverage
            self.check_input_in_wave_coverage()

            # Fitting the Line
            self.best_param, self.best_perr = self.fit()

        def check_input_in_wave_coverage(self):
            """
            Check if the emission line wavelength is within the 1D spectral coverage of the galaxy.

            Raises
            ------
            ValueError
                If the observed wavelength (`linewave * (1 + redshift)`) is outside the coverage of the 1D spectra.
            """
            obs_linewave = self.linewave*(1. + self.galaxy.zSpec)
            if (obs_linewave < np.min(self.galaxy.wave)) or \
                    (obs_linewave > np.max(self.galaxy.wave)):
                raise ValueError(
                    "Inputted Wavelength is outside the coverage of the 1D Spectra!")

        def fit(self) -> tuple:
            """
            Fit a Gaussian profile to the emission line and return the best-fit parameters and their errors.

            Returns
            -------
            tuple
                A tuple containing two elements:
                - params (np.array): The best-fit parameters of the Gaussian profile [lineFlux, cent_wave, sigma, cont].
                - perr (np.array): The uncertainties associated with the best-fit parameters.

            The fit results include:
                - Line Flux: Integrated flux of the line.
                - Central Wavelength: The peak wavelength of the emission line.
                - Sigma: The standard deviation of the Gaussian profile (width of the line).
                - Continuum Flux Density: The baseline level of the spectrum.
                - Reduced Chi-Square: A measure of the goodness of fit.

            Additionally, it prints:
                - The refined redshift based on the fitted parameters.
                - Plots the observed spectrum and the fitted Gaussian model if `self.plot` is True.
            """

            # Convert to Observed Wavelength
            obs_linewave = self.linewave*(1. + self.galaxy.zSpec)

            # Limit Fit
            keep = np.where((self.galaxy.wave > obs_linewave-self.window/2.)
                            & (self.galaxy.wave < obs_linewave+self.window/2.))

            # Fit the Model
            params, pcov = curve_fit(gaussian, self.galaxy.wave[keep],
                                     self.galaxy.flux[keep],
                                     p0=[1e-17, obs_linewave, 1., 0.],
                                     sigma=self.galaxy.err[keep])

            # Get Errors
            perr = np.sqrt(np.diag(pcov))

            # Get Bestfit Model
            bestfit_model = gaussian(self.galaxy.wave[keep], *params)

            # Print Parameters
            print("")
            print(f"Line Flux: {params[0]:.3e} +- {perr[0]:.3e} erg/s/cm2")
            print(
                f"Central Wavelength: {params[1]:.1f} +- {perr[1]:.1f} Angstrom")
            print(f"Sigma: {params[2]:.2f} +- {perr[2]:.2f} Angstrom")
            print(
                f"Continuum Flux Density: {params[3]:.3e} +- {perr[3]:.3e} erg/s/cm2/A")
            print(f'S/N:{params[0]/perr[0]:.2f}')

            # Get and Print Reduced Chi2
            dof = len(self.galaxy.flux[keep]) - len(params)
            red_chi2 = reduced_Chi2(
                bestfit_model, self.galaxy.flux[keep], self.galaxy.err[keep])/dof
            print(f"Reduced Chi-Square: {red_chi2:0.2f}")

            # Get Refined Redshift
            new_specz = params[1]/self.linewave - 1.
            new_specz_err = perr[1]/self.linewave

            print("")
            print(f"Old Redshift: {self.galaxy.zSpec:0.4f}")
            print(
                f"Refined Redshift: {new_specz:0.4f} +- {new_specz_err:0.4f}")

            # Plot the Model against Observations
            if self.plot == True:
                plt.plot(self.galaxy.wave[keep],
                         self.galaxy.flux[keep], label="Observed")
                plt.plot(self.galaxy.wave[keep],
                         bestfit_model, ls='--', label="Model")
                plt.legend(loc="upper right", ncol=1,
                           numpoints=1, fontsize=8, frameon=False)
                plt.show()

            return (params, perr)

        def getLineFlux(self, include_err: bool = False) -> Union[float, tuple]:
            """
            Retrieve the flux of the fitted emission line.

            Parameters
            ----------
            include_err : bool, optional
                Whether to include the error in the returned result. Default is False.

            Returns
            -------
            Union[float, tuple]
                - If `include_err` is False, returns the flux of the emission line as a float.
                - If `include_err` is True, returns a tuple containing:
                    - The flux of the emission line (float).
                    - The uncertainty in the flux (float).

            Notes
            -----
            - The flux value is obtained from the best-fit parameters of the Gaussian profile.
            - The error in the flux is also derived from the uncertainties associated with the best-fit parameters.
            """

            if include_err == False:
                return self.best_param[0]
            if include_err == True:
                return (self.best_param[0], self.best_perr[0])

        def getContinuumFluxDensity(self, include_err: bool = False) -> Union[float, tuple]:
            """
            Retrieve the continuum flux density of the fitted emission line.

            Parameters
            ----------
            include_err : bool, optional
                Whether to include the error in the returned result. Default is False.

            Returns
            -------
            Union[float, tuple]
                - If `include_err` is False, returns the continuum flux density as a float.
                - If `include_err` is True, returns a tuple containing:
                    - The continuum flux density (float).
                    - The uncertainty in the continuum flux density (float).

            Notes
            -----
            - The continuum flux density value is obtained from the best-fit parameters of the Gaussian profile.
            - The error in the continuum flux density is also derived from the uncertainties associated with the best-fit parameters.
            """
            if include_err == False:
                return self.best_param[3]
            if include_err == True:
                return (self.best_param[3], self.best_perr[3])

        def getVelocityDisp(self, units: str = "Angstrom", include_err: bool = False) -> Union[float, tuple]:
            """
            Retrieve the velocity dispersion of the fitted emission line in the specified units.

            Parameters
            ----------
            units : str, optional
                The units for the velocity dispersion. Options are "Angstrom" (default) or "km/s".
            include_err : bool, optional
                Whether to include the error in the returned result. Default is False.

            Returns
            -------
            Union[float, tuple]
                - If `units` is "Angstrom" and `include_err` is False, returns the velocity dispersion in Angstroms as a float.
                - If `units` is "Angstrom" and `include_err` is True, returns a tuple containing:
                    - The velocity dispersion in Angstroms (float).
                    - The uncertainty in the velocity dispersion (float).
                - If `units` is "km/s" and `include_err` is False, returns the velocity dispersion in km/s as a float.
                - If `units` is "km/s" and `include_err` is True, returns a tuple containing:
                    - The velocity dispersion in km/s (float).
                    - The uncertainty in the velocity dispersion (float).

            Raises
            ------
            ValueError
                If `units` is not "Angstrom" or "km/s".

            Notes
            -----
            - The velocity dispersion is derived from the Gaussian profile's standard deviation (sigma) and central wavelength.
            - When converting to km/s, the speed of light (`const.c`) is used for conversion, and error propagation is considered.
            """

            if units == "Angstrom":
                if include_err == True:
                    return (self.best_param[2], self.best_perr[2])
                if include_err == False:
                    return self.best_param[2]

            if units == "km/s":
                if include_err == True:
                    velDisp = self.best_param[2] / \
                        self.best_param[1]*const.c.to('km/s').value
                    velDisp_err = velDisp * \
                        np.sqrt((self.best_perr[2]/self.best_param[2]) **
                                2. + (self.best_perr[1]/self.best_param[1])**2.)
                    return (velDisp, velDisp_err)

                if include_err == False:
                    return self.best_param[2]/self.best_param[1]*const.c.to('km/s').value

            # In case user uses the wrong units
            if ("Angstrom" not in units) or ("km/s" not in units):
                raise ValueError("Available Units are Angstrom and km/s")


def main():
    #data = fits.open("../examples/701230_1d.fits")[1].data

    #wave = data["WAVE"][0]
    #flux = data["FLUX_REDUCED"][0]
    #err = flux*0.2

    #pedro = Galaxy("123",wave=wave,flux=flux,err=err,zSpec=0.6691)
    pedro = Galaxy(701230)
    hb = pedro.run_line(4959.)

    print(hb.getLineFlux(include_err=True))
    print(hb.getContinuumFluxDensity())
    print(hb.getVelocityDisp())
    print(hb.getVelocityDisp(units="km/s", include_err=True))


if __name__ == "__main__":
    main()
