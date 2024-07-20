""" Calibration module for noise and flux. """
import argparse

import fitsio
import numpy as np

from qsonic.mathtools import (
    FastCubic1DInterp, FastLinear1DInterp, _one_function)
from qsonic.mpi_utils import mpi_fnc_bcast


def add_calibration_parser(parser=None):
    """ Adds calibration related arguments to parser. These arguments are
    grouped under 'Noise and flux calibation options'.

    Arguments
    ---------
    parser: argparse.ArgumentParser, default: None

    Returns
    ---------
    parser: argparse.ArgumentParser
    """
    if parser is None:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    calib_group = parser.add_argument_group(
        'Noise and flux calibation options')

    calib_group.add_argument(
        "--noise-calibration", help="Noise calibration file.")
    calib_group.add_argument(
        "--varlss-as-additive-noise", action="store_true",
        help="var_lss as additive noise term after continuum fitting.")
    calib_group.add_argument(
        "--flux-calibration", help="Flux calibration file.")

    return parser


class NoiseCalibrator():
    """ Noise calibration object.

    .. math:: i \\rightarrow i / \\eta,

    where i is IVAR.

    FITS file must have 'VAR_FUNC' extension. This extension must have columns
    for 'lambda' and 'eta'. Wavelength array must be linearly and equally
    spaced. Uses cubic spline.

    Parameters
    ----------
    fname: str
        Filename to read by ``fitsio``.
    comm: None or MPI.COMM_WORLD, default: None
    mpi_rank: int, default: 0
    add_varlss: bool, default: False
        Use var_lss as an additive correction to noise in observed frame.
        Requires continuum.
    no_eta: bool, default: False
        Turns off eta scaling by using eta=1.

    Attributes
    ----------
    eta_interp: FastCubic1DInterp
        Eta interpolator.
    """

    def _read(self, fname):
        with fitsio.FITS(fname) as fts:
            data = fts['VAR_FUNC'].read()

        waves = data['lambda']
        waves_0 = waves[0]
        dwave = waves[1] - waves[0]

        if not np.allclose(np.diff(waves), dwave):
            raise Exception(
                "Failed to construct noise calibration from "
                f"{fname}::wave is not equally spaced.")

        var_lss = np.array(data['var_lss'], dtype='d')
        varlss_interp = FastCubic1DInterp(waves_0, dwave, var_lss)

        eta = np.array(data['eta'], dtype='d')
        eta[eta == 0] = 1
        eta_interp = FastCubic1DInterp(waves_0, dwave, eta)

        return eta_interp, varlss_interp

    def __init__(
            self, fname, comm=None, mpi_rank=0,
            add_varlss=False, no_eta=False
    ):
        self.eta_interp, self.varlss_interp = mpi_fnc_bcast(
            self._read, comm, mpi_rank,
            f"Error loading NoiseCalibrator from file {fname}.",
            fname)

        if not add_varlss:
            self.varlss_interp = None

        if no_eta:
            self.eta_interp = _one_function

    def apply(self, spectra_list):
        """ Apply the noise calibration by **only** scaling
        :attr:`forestivar <qsonic.spectrum.Spectrum.forestivar>`. Smooth
        component must be set after this.

        Arguments
        ----------
        spectra_list: list(Spectrum)
            Spectrum objects to noise calibrate.
        """
        if self.varlss_interp:
            if not all(spec.cont_params['cont'] for spec in spectra_list):
                raise Exception(
                    "NoiseCalibrator needs continuum for additive correction.")

            for spec in spectra_list:
                for arm, wave_arm in spec.forestwave.items():
                    eta = self.eta_interp(wave_arm)
                    vlss = self.varlss_interp(wave_arm)
                    vlss *= spec.cont_params['cont'][arm]**2
                    spec.forestivar[arm] /= (eta + spec.forestivar[arm] * vlss)
                    spec.forestivar[arm][spec.forestivar[arm] < 0] = 0
        else:
            for spec in spectra_list:
                for arm, wave_arm in spec.forestwave.items():
                    eta = self.eta_interp(wave_arm)
                    spec.forestivar[arm] /= eta


class FluxCalibrator():
    """ Flux calibration object.

    .. math::

        f &\\rightarrow f / s

        i &\\rightarrow i \\times s^2,

    where i is IVAR and s is the stacked flux.

    FITS file must have 'STACKED_FLUX' extension. This extension must have
    columns for 'lambda' and 'stacked_flux'. Wavelength array must be linearly
    and equally spaced. Uses linear interpolation.

    Parameters
    ----------
    fname: str
        Filename to read by ``fitsio``.
    comm: None or MPI.COMM_WORLD, default: None
    mpi_rank: int, default: 0

    Attributes
    ----------
    flux_interp: FastLinear1DInterp
        Flux interpolator.
    """

    def _read(self, fname):
        with fitsio.FITS(fname) as fts:
            data = fts['STACKED_FLUX'].read()

        waves = data['lambda']
        waves_0 = waves[0]
        dwave = waves[1] - waves[0]

        if not np.allclose(np.diff(waves), dwave):
            raise Exception(
                "Failed to construct flux calibration from "
                f"{fname}::wave is not equally spaced.")

        stacked_flux = np.array(data['stacked_flux'], dtype='d')
        stacked_flux[stacked_flux == 0] = 1

        return FastLinear1DInterp(waves_0, dwave, stacked_flux)

    def __init__(self, fname, comm=None, mpi_rank=0):
        self.stacked_flux_interp = mpi_fnc_bcast(
            self._read, comm, mpi_rank,
            f"Error loading FluxCalibrator from file {fname}.",
            fname)

    def apply(self, spectra_list):
        """ Apply the flux calibration by **only** scaling
        :attr:`forestflux <qsonic.spectrum.Spectrum.forestflux>` and
        :attr:`forestivar <qsonic.spectrum.Spectrum.forestivar>`. Smooth
        component must be set after this.

        Arguments
        ----------
        spectra_list: list(Spectrum)
            Spectrum objects to flux calibrate.
        """
        for spec in spectra_list:
            for arm, wave_arm in spec.forestwave.items():
                stacked_flux = self.stacked_flux_interp(wave_arm)
                spec.forestflux[arm] /= stacked_flux
                spec.forestivar[arm] *= stacked_flux**2
