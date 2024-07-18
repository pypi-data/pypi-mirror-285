# -*- coding: utf-8 -*-
"""
This module defines the most basic elements for tracking, including Element,
an abstract base class which is to be used as mother class to every elements
included in the tracking.
"""

from abc import ABCMeta, abstractmethod
from copy import deepcopy
from functools import wraps

import numpy as np

from mbtrack2.tracking.particles import Beam


class Element(metaclass=ABCMeta):
    """
    Abstract Element class used for subclass inheritance to define all kinds
    of objects which intervene in the tracking.
    """

    @abstractmethod
    def track(self, beam):
        """
        Track a beam object through this Element.
        This method needs to be overloaded in each Element subclass.

        Parameters
        ----------
        beam : Beam object
        """
        raise NotImplementedError

    @staticmethod
    def parallel(track):
        """
        Defines the decorator @parallel which handle the embarrassingly
        parallel case which happens when there is no bunch to bunch
        interaction in the tracking routine.

        Adding @Element.parallel allows to write the track method of the
        Element subclass for a Bunch object instead of a Beam object.

        Parameters
        ----------
        track : function, method of an Element subclass
            track method of an Element subclass which takes a Bunch object as
            input

        Returns
        -------
        track_wrapper: function, method of an Element subclass
            track method of an Element subclass which takes a Beam object or a
            Bunch object as input
        """

        @wraps(track)
        def track_wrapper(*args, **kwargs):
            if isinstance(args[1], Beam):
                self = args[0]
                beam = args[1]
                if beam.mpi_switch == True:
                    track(self, beam[beam.mpi.bunch_num], *args[2:], **kwargs)
                else:
                    for bunch in beam.not_empty:
                        track(self, bunch, *args[2:], **kwargs)
            else:
                self = args[0]
                bunch = args[1]
                track(self, bunch, *args[2:], **kwargs)

        return track_wrapper


class LongitudinalMap(Element):
    """
    Longitudinal map for a single turn in the synchrotron.

    Parameters
    ----------
    ring : Synchrotron object
    """

    def __init__(self, ring):
        self.ring = ring

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the element.
        No bunch to bunch interaction, so written for Bunch objects and
        @Element.parallel is used to handle Beam objects.

        Parameters
        ----------
        bunch : Bunch or Beam object
        """
        bunch["delta"] -= self.ring.U0 / self.ring.E0
        bunch["tau"] += self.ring.eta(
            bunch["delta"]) * self.ring.T0 * bunch["delta"]


class SynchrotronRadiation(Element):
    """
    Element to handle synchrotron radiation, radiation damping and quantum
    excitation, for a single turn in the synchrotron.

    Parameters
    ----------
    ring : Synchrotron object
    switch : bool array of shape (3,), optional
        allow to choose on which plane the synchrotron radiation is active
    """

    def __init__(self, ring, switch=np.ones((3, ), dtype=bool)):
        self.ring = ring
        self.switch = switch

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the element.
        No bunch to bunch interaction, so written for Bunch objects and
        @Element.parallel is used to handle Beam objects.

        Parameters
        ----------
        bunch : Bunch or Beam object
        """
        if self.switch[0] == True:
            rand = np.random.normal(size=len(bunch))
            bunch["delta"] = (1 - 2 * self.ring.T0 / self.ring.tau[2]) * bunch[
                "delta"] + 2 * self.ring.sigma_delta * (
                    self.ring.T0 / self.ring.tau[2])**0.5 * rand

        if self.switch[1] == True:
            rand = np.random.normal(size=len(bunch))
            bunch["xp"] = (1 - 2 * self.ring.T0 / self.ring.tau[0]
                           ) * bunch["xp"] + 2 * self.ring.sigma()[1] * (
                               self.ring.T0 / self.ring.tau[0])**0.5 * rand

        if self.switch[2] == True:
            rand = np.random.normal(size=len(bunch))
            bunch["yp"] = (1 - 2 * self.ring.T0 / self.ring.tau[1]
                           ) * bunch["yp"] + 2 * self.ring.sigma()[3] * (
                               self.ring.T0 / self.ring.tau[1])**0.5 * rand


class TransverseMap(Element):
    """
    Transverse map for a single turn in the synchrotron.

    Parameters
    ----------
    ring : Synchrotron object
    """

    def __init__(self, ring):
        self.ring = ring
        self.alpha = self.ring.optics.local_alpha
        self.beta = self.ring.optics.local_beta
        self.gamma = self.ring.optics.local_gamma
        self.dispersion = self.ring.optics.local_dispersion
        if self.ring.adts is not None:
            self.adts_poly = [
                np.poly1d(self.ring.adts[0]),
                np.poly1d(self.ring.adts[1]),
                np.poly1d(self.ring.adts[2]),
                np.poly1d(self.ring.adts[3]),
            ]

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the element.
        No bunch to bunch interaction, so written for Bunch objects and
        @Element.parallel is used to handle Beam objects.

        Parameters
        ----------
        bunch : Bunch or Beam object
        """

        # Compute phase advance which depends on energy via chromaticity and ADTS
        if self.ring.adts is None:
            phase_advance_x = (
                2 * np.pi *
                (self.ring.tune[0] + self.ring.chro[0] * bunch["delta"]))
            phase_advance_y = (
                2 * np.pi *
                (self.ring.tune[1] + self.ring.chro[1] * bunch["delta"]))
        else:
            Jx = ((self.ring.optics.local_gamma[0] * bunch["x"]**2) +
                  (2 * self.ring.optics.local_alpha[0] * bunch["x"] *
                   bunch["xp"]) +
                  (self.ring.optics.local_beta[0] * bunch["xp"]**2))
            Jy = ((self.ring.optics.local_gamma[1] * bunch["y"]**2) +
                  (2 * self.ring.optics.local_alpha[1] * bunch["y"] *
                   bunch["yp"]) +
                  (self.ring.optics.local_beta[1] * bunch["yp"]**2))
            phase_advance_x = (
                2 * np.pi *
                (self.ring.tune[0] + self.ring.chro[0] * bunch["delta"] +
                 self.adts_poly[0](Jx) + self.adts_poly[2](Jy)))
            phase_advance_y = (
                2 * np.pi *
                (self.ring.tune[1] + self.ring.chro[1] * bunch["delta"] +
                 self.adts_poly[1](Jx) + self.adts_poly[3](Jy)))

        # 6x6 matrix corresponding to (x, xp, delta, y, yp, delta)
        matrix = np.zeros((6, 6, len(bunch)), dtype=np.float64)

        # Horizontal
        c_x = np.cos(phase_advance_x)
        s_x = np.sin(phase_advance_x)

        matrix[0, 0, :] = c_x + self.alpha[0] * s_x
        matrix[0, 1, :] = self.beta[0] * s_x
        matrix[0, 2, :] = self.dispersion[0]
        matrix[1, 0, :] = -1 * self.gamma[0] * s_x
        matrix[1, 1, :] = c_x - self.alpha[0] * s_x
        matrix[1, 2, :] = self.dispersion[1]
        matrix[2, 2, :] = 1

        # Vertical
        c_y = np.cos(phase_advance_y)
        s_y = np.sin(phase_advance_y)

        matrix[3, 3, :] = c_y + self.alpha[1] * s_y
        matrix[3, 4, :] = self.beta[1] * s_y
        matrix[3, 5, :] = self.dispersion[2]
        matrix[4, 3, :] = -1 * self.gamma[1] * s_y
        matrix[4, 4, :] = c_y - self.alpha[1] * s_y
        matrix[4, 5, :] = self.dispersion[3]
        matrix[5, 5, :] = 1

        x = (matrix[0, 0] * bunch["x"] + matrix[0, 1] * bunch["xp"] +
             matrix[0, 2] * bunch["delta"])
        xp = (matrix[1, 0] * bunch["x"] + matrix[1, 1] * bunch["xp"] +
              matrix[1, 2] * bunch["delta"])
        y = (matrix[3, 3] * bunch["y"] + matrix[3, 4] * bunch["yp"] +
             matrix[3, 5] * bunch["delta"])
        yp = (matrix[4, 3] * bunch["y"] + matrix[4, 4] * bunch["yp"] +
              matrix[4, 5] * bunch["delta"])

        bunch["x"] = x
        bunch["xp"] = xp
        bunch["y"] = y
        bunch["yp"] = yp


class SkewQuadrupole:
    """
    Thin skew quadrupole element used to introduce betatron coupling (the
    length of the quadrupole is neglected).

    Parameters
    ----------
    strength : float
        Integrated strength of the skew quadrupole [m].

    """

    def __init__(self, strength):
        self.strength = strength

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the element.
        No bunch to bunch interaction, so written for Bunch objects and
        @Element.parallel is used to handle Beam objects.

        Parameters
        ----------
        bunch : Bunch or Beam object
        """

        bunch["xp"] = bunch["xp"] - self.strength * bunch["y"]
        bunch["yp"] = bunch["yp"] - self.strength * bunch["x"]


class TransverseMapSector(Element):
    """
    Transverse map for a sector of the synchrotron, from an initial
    position s0 to a final position s1.

    Parameters
    ----------
    ring : Synchrotron object
        Ring parameters.
    alpha0 : array of shape (2,)
        Alpha Twiss function at the initial location of the sector.
    beta0 : array of shape (2,)
        Beta Twiss function at the initial location of the sector.
    dispersion0 : array of shape (4,)
        Dispersion function at the initial location of the sector.
    alpha1: array of shape (2,)
        Alpha Twiss function at the final location of the sector.
    beta1 : array of shape (2,)
        Beta Twiss function at the final location of the sector.
    dispersion1 : array of shape (4,)
        Dispersion function at the final location of the sector.
    phase_diff : array of shape (2,)
        Phase difference between the initial and final location of the
        sector.
    chro_diff : array of shape (2,)
        Chromaticity difference between the initial and final location of
        the sector.
    adts : array of shape (4,), optional
        Amplitude-dependent tune shift of the sector, see Synchrotron class
        for details. The default is None.

    """

    def __init__(self,
                 ring,
                 alpha0,
                 beta0,
                 dispersion0,
                 alpha1,
                 beta1,
                 dispersion1,
                 phase_diff,
                 chro_diff,
                 adts=None):
        self.ring = ring
        self.alpha0 = alpha0
        self.beta0 = beta0
        self.gamma0 = (1 + self.alpha0**2) / self.beta0
        self.dispersion0 = dispersion0
        self.alpha1 = alpha1
        self.beta1 = beta1
        self.gamma1 = (1 + self.alpha1**2) / self.beta1
        self.dispersion1 = dispersion1
        self.tune_diff = phase_diff / (2 * np.pi)
        self.chro_diff = chro_diff
        if adts is not None:
            self.adts_poly = [
                np.poly1d(adts[0]),
                np.poly1d(adts[1]),
                np.poly1d(adts[2]),
                np.poly1d(adts[3]),
            ]
        else:
            self.adts_poly = None

    @Element.parallel
    def track(self, bunch):
        """
        Tracking method for the element.
        No bunch to bunch interaction, so written for Bunch objects and
        @Element.parallel is used to handle Beam objects.

        Parameters
        ----------
        bunch : Bunch or Beam object
        """

        # Compute phase advance which depends on energy via chromaticity and ADTS
        if self.adts_poly is None:
            phase_advance_x = (
                2 * np.pi *
                (self.tune_diff[0] + self.chro_diff[0] * bunch["delta"]))
            phase_advance_y = (
                2 * np.pi *
                (self.tune_diff[1] + self.chro_diff[1] * bunch["delta"]))
        else:
            Jx = ((self.gamma0[0] * bunch["x"]**2) +
                  (2 * self.alpha0[0] * bunch["x"] * self["xp"]) +
                  (self.beta0[0] * bunch["xp"]**2))
            Jy = ((self.gamma0[1] * bunch["y"]**2) +
                  (2 * self.alpha0[1] * bunch["y"] * bunch["yp"]) +
                  (self.beta0[1] * bunch["yp"]**2))
            phase_advance_x = (
                2 * np.pi *
                (self.tune_diff[0] + self.chro_diff[0] * bunch["delta"] +
                 self.adts_poly[0](Jx) + self.adts_poly[2](Jy)))
            phase_advance_y = (
                2 * np.pi *
                (self.tune_diff[1] + self.chro_diff[1] * bunch["delta"] +
                 self.adts_poly[1](Jx) + self.adts_poly[3](Jy)))

        # 6x6 matrix corresponding to (x, xp, delta, y, yp, delta)
        matrix = np.zeros((6, 6, len(bunch)))

        # Horizontal
        matrix[0, 0, :] = np.sqrt(self.beta1[0] / self.beta0[0]) * (
            np.cos(phase_advance_x) + self.alpha0[0] * np.sin(phase_advance_x))
        matrix[0, 1, :] = np.sqrt(
            self.beta0[0] * self.beta1[0]) * np.sin(phase_advance_x)
        matrix[0, 2, :] = (self.dispersion1[0] -
                           matrix[0, 0, :] * self.dispersion0[0] -
                           matrix[0, 1, :] * self.dispersion0[1])
        matrix[1, 0, :] = (
            (self.alpha0[0] - self.alpha1[0]) * np.cos(phase_advance_x) -
            (1 + self.alpha0[0] * self.alpha1[0]) *
            np.sin(phase_advance_x)) / np.sqrt(self.beta0[0] * self.beta1[0])
        matrix[1, 1, :] = np.sqrt(self.beta0[0] / self.beta1[0]) * (
            np.cos(phase_advance_x) - self.alpha1[0] * np.sin(phase_advance_x))
        matrix[1, 2, :] = (self.dispersion1[1] -
                           matrix[1, 0, :] * self.dispersion0[0] -
                           matrix[1, 1, :] * self.dispersion0[1])
        matrix[2, 2, :] = 1

        # Vertical
        matrix[3, 3, :] = np.sqrt(self.beta1[1] / self.beta0[1]) * (
            np.cos(phase_advance_y) + self.alpha0[1] * np.sin(phase_advance_y))
        matrix[3, 4, :] = np.sqrt(
            self.beta0[1] * self.beta1[1]) * np.sin(phase_advance_y)
        matrix[3, 5, :] = (self.dispersion1[2] -
                           matrix[3, 3, :] * self.dispersion0[2] -
                           matrix[3, 4, :] * self.dispersion0[3])
        matrix[4, 3, :] = (
            (self.alpha0[1] - self.alpha1[1]) * np.cos(phase_advance_y) -
            (1 + self.alpha0[1] * self.alpha1[1]) *
            np.sin(phase_advance_y)) / np.sqrt(self.beta0[1] * self.beta1[1])
        matrix[4, 4, :] = np.sqrt(self.beta0[1] / self.beta1[1]) * (
            np.cos(phase_advance_y) - self.alpha1[1] * np.sin(phase_advance_y))
        matrix[4, 5, :] = (self.dispersion1[3] -
                           matrix[4, 3, :] * self.dispersion0[2] -
                           matrix[4, 4, :] * self.dispersion0[3])
        matrix[5, 5, :] = 1

        x = (matrix[0, 0, :] * bunch["x"] + matrix[0, 1, :] * bunch["xp"] +
             matrix[0, 2, :] * bunch["delta"])
        xp = (matrix[1, 0, :] * bunch["x"] + matrix[1, 1, :] * bunch["xp"] +
              matrix[1, 2, :] * bunch["delta"])
        y = (matrix[3, 3, :] * bunch["y"] + matrix[3, 4, :] * bunch["yp"] +
             matrix[3, 5, :] * bunch["delta"])
        yp = (matrix[4, 3, :] * bunch["y"] + matrix[4, 4, :] * bunch["yp"] +
              matrix[4, 5, :] * bunch["delta"])

        bunch["x"] = x
        bunch["xp"] = xp
        bunch["y"] = y
        bunch["yp"] = yp


def transverse_map_sector_generator(ring, positions):
    """
    Convenience function which generate a list of TransverseMapSector elements
    from a ring:
        - if an AT lattice is loaded, the optics functions and chromaticity is
        computed at the given positions.
        - if no AT lattice is loaded, the local optics are used everywhere.

    Tracking through all the sectors is equivalent to a full turn (and thus to
    the TransverseMap object).

    Parameters
    ----------
    ring : Synchrotron object
        Ring parameters.
    positions : array
        List of longitudinal positions in [m] to use as starting and end points
        of the TransverseMapSector elements.
        The array should contain the initial position (s=0) but not the end
        position (s=ring.L), so like position = np.array([0, pos1, pos2, ...]).

    Returns
    -------
    sectors : list
        List of TransverseMapSector elements.

    """
    N_sec = len(positions)
    sectors = []
    if ring.optics.use_local_values:
        for i in range(N_sec):
            sectors.append(
                TransverseMapSector(
                    ring,
                    ring.optics.local_alpha,
                    ring.optics.local_beta,
                    ring.optics.local_dispersion,
                    ring.optics.local_alpha,
                    ring.optics.local_beta,
                    ring.optics.local_dispersion,
                    ring.tune / N_sec,
                    ring.chro / N_sec,
                ))
    else:
        import at

        def _compute_chro(ring, pos, dp=1e-4):
            lat = deepcopy(ring.optics.lattice)
            lat.append(at.Marker("END"))
            N = len(lat)
            refpts = np.arange(N)
            (*elem_neg_dp, ) = at.linopt2(lat, refpts=refpts, dp=-dp)
            (*elem_pos_dp, ) = at.linopt2(lat, refpts=refpts, dp=dp)

            s = elem_neg_dp[2]["s_pos"]
            mux0 = elem_neg_dp[2]["mu"][:, 0]
            mux1 = elem_pos_dp[2]["mu"][:, 0]
            muy0 = elem_neg_dp[2]["mu"][:, 1]
            muy1 = elem_pos_dp[2]["mu"][:, 1]

            Chrox = (mux1-mux0) / (2*dp) / 2 / np.pi
            Chroy = (muy1-muy0) / (2*dp) / 2 / np.pi
            chrox = np.interp(pos, s, Chrox)
            chroy = np.interp(pos, s, Chroy)

            return np.array([chrox, chroy])

        for i in range(N_sec):
            alpha0 = ring.optics.alpha(positions[i])
            beta0 = ring.optics.beta(positions[i])
            dispersion0 = ring.optics.dispersion(positions[i])
            mu0 = ring.optics.mu(positions[i])
            chro0 = _compute_chro(ring, positions[i])
            if i != (N_sec - 1):
                alpha1 = ring.optics.alpha(positions[i + 1])
                beta1 = ring.optics.beta(positions[i + 1])
                dispersion1 = ring.optics.dispersion(positions[i + 1])
                mu1 = ring.optics.mu(positions[i + 1])
                chro1 = _compute_chro(ring, positions[i + 1])
            else:
                alpha1 = ring.optics.alpha(positions[0])
                beta1 = ring.optics.beta(positions[0])
                dispersion1 = ring.optics.dispersion(positions[0])
                mu1 = ring.optics.mu(ring.L)
                chro1 = _compute_chro(ring, ring.L)
            phase_diff = mu1 - mu0
            chro_diff = chro1 - chro0
            sectors.append(
                TransverseMapSector(
                    ring,
                    alpha0,
                    beta0,
                    dispersion0,
                    alpha1,
                    beta1,
                    dispersion1,
                    phase_diff,
                    chro_diff,
                ))
    return sectors
