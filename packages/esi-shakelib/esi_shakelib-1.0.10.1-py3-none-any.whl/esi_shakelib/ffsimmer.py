"""
Perform Monte Carlo simulation of  finite faults and perform a mixed effects
regression to obtain mean ground motions and uncertainties.
"""

import copy
from enum import Enum

import numpy as np
from scipy.stats import norm
import openquake.hazardlib.const as oqconst

from esi_utils_rupture.quad_rupture import QuadRupture
from esi_utils_rupture.point_rupture import PointRupture
from esi_utils_rupture.distance import Distance
from esi_shakelib.sites import Sites


class AutoName(Enum):
    """
    These enum members hold their name (as a string) as their value.
    For example: DistType.Rjb.value == 'Rjb'
    """

    def __init__(self):
        self._value_ = self.name


class MagScaling(AutoName):
    """
    Magnitude scaling relationship.
       - 'WC94' is for Wells and Coppersmith (1999)
       - 'HB08' is for Hanks and Bakun (2008)
       - 'S14' is for Somerville et al. (2014)
       - 'Sea10_interface' is for Strasser et al. (2010), for interface events
       - 'Sea10_slab' is for Strasser et al. (2010), for intraplate events
    """

    WC94 = ()
    HB08 = ()
    S14 = ()
    Sea10_interface = ()
    Sea10_slab = ()


class Mechanism(AutoName):
    """
    Source mechanism.
       - 'A' for all (mechanism is unknown/unspecified)
       - 'R' for reverse
       - 'N' for normal
       - 'SS' for strike-slip
    """

    ALL = ()
    RS = ()
    NM = ()
    SS = ()


class FFSimmer:
    """
    Class to perform monte carlo simulations of finite faults to derive mean ground
    motions
    """

    def __init__(self, rff, measure="median"):
        """
        Args:
            rff (RandomFiniteFault object):
                An instance of the RandomFiniteFault object.
            measure (str):
                Either "mean" or "median" -- the measure of central tendency to report.
        """
        if measure not in ("mean", "median"):
            raise ValueError(f"Unknown measure of central tendency: {measure}")
        self.measure = measure
        self.rff = rff
        self.origin = copy.copy(rff.origin)

    def compute_grid(self, grid, gmpe, myimts):
        """
        Args:
            grid (Grid2D object):
                Basically the vs30grid that we're mapping, used for its dimensions.
                The site corrections have to be done elsewhere.
            gmpe (MultiGMPE object):
                The MultiGMPE to be used for the simulations.
            myimts (list):
                List of OQ IMTs to generate grids and transects for

        Returns:
            dictionary:
                {
                    oqimt: {
                        "mean": 2D Array (the median or mean ground motion values, at
                            a Vs30 of 760 m/s),
                        "transect": Array (a transect of the grid at the repis below),
                        "repi": Array (the Repis corresponding to "transect" above),
                        oqconst.StdDev.TOTAL: Array,
                        (if allowed:)
                        oqconst.StdDev.INTER_EVENT: Array,
                        oqconst.StdDev.INTRA_EVENT: Array,
                    },
                }
        """
        griddict = {}
        hypo = self.origin.getHypo()
        olon = hypo.x
        olat = hypo.y

        sd_types = list(gmpe[myimts[0]].DEFINED_FOR_STANDARD_DEVIATION_TYPES)

        #
        gd = grid.getGeoDict()
        # Increase the grid resolution if it is greater the 30 arc-seconds
        delta_y = gd.dy
        if delta_y > (30.0 / 3600.0):
            delta_y = delta_y / 2.0
        # Compute distance to all four corners of grid
        prup = PointRupture(self.origin)
        lons = np.array([gd.xmin, gd.xmin, gd.xmax, gd.xmax])
        lats = np.array([gd.ymin, gd.ymax, gd.ymin, gd.ymax])
        depths = np.zeros_like(lons)
        repi = prup.computeRepi(lons, lats, depths)
        rmax = np.max(repi)

        west = olon
        east = olon
        south = olat
        north = olat + rmax / 111.1
        if north > 90.0:
            north = olat
            south = olat - rmax / 111.1

        sites = Sites.fromBounds(
            west,
            east,
            south,
            north,
            delta_y,
            delta_y,
            defaultVs30=760.0,
            vs30File=None,
            padding=True,
            resample=True,
        )
        (nx, ny) = sites.getNxNy()
        sgd = sites.getVs30Grid().getGeoDict()
        sctx = sites.getSitesContext()
        for k in sctx.__dict__:
            if k == "_slots_":
                continue
            sctx.__dict__[k] = sctx.__dict__[k].flatten()

        nsim = self.rff.get_nsim()
        nimt = len(myimts)
        amps = np.empty((nimt, nsim, nx * ny))
        sigs = np.empty((nimt, nsim, nx * ny))
        if len(sd_types) > 1:
            taus = np.empty((nimt, nsim, nx * ny))
            phis = np.empty((nimt, nsim, nx * ny))

        for idx in range(nsim):
            rupt = self.rff.retrieve_rupt(idx)
            dist = Distance.fromSites(gmpe[myimts[0]], sites, rupt)
            dctx = dist.getDistanceContext()
            for k in dctx.__dict__:
                if k == "_slots_":
                    continue
                if not isinstance(dctx.__dict__[k], np.ndarray):
                    continue
                dctx.__dict__[k] = dctx.__dict__[k].flatten()
            rctx = rupt.getRuptureContext(gmpe[myimts[0]])

            for iimt, simt in enumerate(myimts):
                mean, stddevs = gmpe[simt].get_mean_and_stddevs(
                    sctx, rctx, dctx, simt, sd_types
                )
                amps[iimt, idx, :] = mean[0]
                sigs[iimt, idx, :] = stddevs[0][0]
                if len(sd_types) > 1:
                    taus[iimt, idx, :] = stddevs[1][0]
                    phis[iimt, idx, :] = stddevs[2][0]

        slat = np.linspace(sgd.ymin, sgd.ymax, sgd.ny)
        repi = prup.computeRepi(
            np.full_like(slat, sgd.xmin),
            slat,
            np.zeros_like(slat),
        )

        gd = grid.getGeoDict()
        glon, glat = np.meshgrid(
            np.linspace(gd.xmin, gd.xmax, gd.nx),
            np.linspace(gd.ymax, gd.ymin, gd.ny),
        )
        gdepth = np.zeros_like(glon)
        grepi = rupt.computeRepi(glon, glat, gdepth)

        # Compute Mean, Sigma, Phi, and Tau for each IMT
        for iimt in range(nimt):
            if self.measure == "median":
                mean_amps = np.median(amps[iimt], axis=0)
            else:
                mean_amps = np.mean(amps[iimt], axis=0)
            residuals = amps[iimt] - mean_amps
            extra_vars = np.var(amps[iimt], axis=0)

            try:
                avg_extra_tau = np.var(np.mean(residuals, axis=1))
                avg_extra_phi = np.mean(np.var(residuals, axis=1))
            except RuntimeWarning as exc:
                # Don't have an answer, so just guess
                print(f"Error in FFSimmer: {exc}")
                print("Using defaults")
                avg_extra_tau = 0.20
                avg_extra_phi = 0.80

            if (
                np.isnan(avg_extra_tau)
                or np.isnan(avg_extra_phi)
                or avg_extra_tau < 1e-8
                or avg_extra_phi < 1e-8
            ):
                print("mixedlm.fit produced unusable results")
                avg_extra_tau = 0.20
                avg_extra_phi = 0.80

            avg_tau_wgt = avg_extra_tau / (avg_extra_tau + avg_extra_phi)
            avg_phi_wgt = 1.0 - avg_tau_wgt
            extra_taus = avg_tau_wgt * extra_vars
            extra_phis = avg_phi_wgt * extra_vars

            # Take the mean over the realizations
            mean_sigs = np.sqrt(np.mean(sigs[iimt] ** 2, axis=0) + extra_vars)
            if len(sd_types) > 1:
                mean_taus = np.sqrt(np.mean(taus[iimt] ** 2, axis=0) + extra_taus)
                mean_phis = np.sqrt(np.mean(phis[iimt] ** 2, axis=0) + extra_phis)

            griddict[myimts[iimt]] = {
                "mean": np.interp(grepi, repi, np.flip(mean_amps)),
                oqconst.StdDev.TOTAL: np.interp(grepi, repi, np.flip(mean_sigs)),
                "transect": np.flip(mean_amps),
                "repi": repi,
            }
            if len(sd_types) > 1:
                griddict[myimts[iimt]][oqconst.StdDev.INTER_EVENT] = np.interp(
                    grepi, repi, np.flip(mean_taus)
                )
                griddict[myimts[iimt]][oqconst.StdDev.INTRA_EVENT] = np.interp(
                    grepi, repi, np.flip(mean_phis)
                )

        return griddict

    def compute_points(self, sctx, gmpe, myimts, rock_vs30=760.0, soil_vs30=180.0):
        """
        Compute median (or mean) ground motions for a set of sites defined in "sctx"
        for the imts in the list "myimts".

        Args:
            sctx: (Sites object)
                A sites context object set up for the points being output
            gmpe: (MultiGMPE object)
                The gmpe to perform the ground-motion realizations.
            myimts (list)
                List of OQ IMTs to generate rock and site amplified values for

        Returns:
            dictionary:
                {
                    oqimt: {
                        "site": The sites at their actual Vs30
                            {
                                "mean": Array,
                                oqconst.StdDev.TOTAL: Array,
                                (if allowed:)
                                oqconst.StdDev.INTER_EVENT: Array,
                                oqconst.StdDev.INTRA_EVENT: Array,
                            }
                        "rock": The sites at a reference rock vs30 of 760 m/s
                        "soil": The sites at a reference soil vs30 of 180 m/s
                    },
                }
        """
        outdict = {}

        sd_types = list(gmpe.DEFINED_FOR_STANDARD_DEVIATION_TYPES)

        sctx_rock = copy.deepcopy(sctx)
        sctx_rock.vs30 = np.full_like(sctx.vs30, rock_vs30)
        sctx_soil = copy.deepcopy(sctx)
        sctx_soil.vs30 = np.full_like(sctx.vs30, soil_vs30)

        nporig = np.size(sctx.lons)
        sx = copy.deepcopy(sctx)
        for k in sctx.__dict__:
            if k == "_slots_":
                continue
            sx.__dict__[k] = np.hstack(
                (sctx.__dict__[k], sctx_rock.__dict__[k], sctx_soil.__dict__[k])
            )
        sx.sids = np.array(list(range(len(sx.lons))))
        depths = np.zeros_like(sx.lons)

        nsd = len(sd_types)
        ctxt_names = ("site", "soil", "rock")
        ctxts = (sctx, sctx_soil, sctx_rock)
        nctx = len(ctxts)

        nimt = len(myimts)
        nsim = self.rff.get_nsim()

        amps = np.empty((nctx, nimt, nsim, nporig))
        sigs = np.empty((nctx, nimt, nsim, nporig))
        if len(sd_types) > 1:
            taus = np.empty((nctx, nimt, nsim, nporig))
            phis = np.empty((nctx, nimt, nsim, nporig))

        for idx in range(nsim):
            rupt = self.rff.retrieve_rupt(idx)
            dist_obj = Distance(gmpe, sx.lons, sx.lats, depths, rupt)
            dctx = dist_obj.getDistanceContext()
            rctx = rupt.getRuptureContext(gmpe)

            mean, stddevs = gmpe.get_mean_and_stddevs(sx, rctx, dctx, myimts, sd_types)
            for iimt, _ in enumerate(myimts):
                for ictx in range(nctx):
                    amps[ictx, iimt, idx, :] = mean[iimt][
                        ictx * nporig : (ictx + 1) * nporig
                    ]
                    sigs[ictx, iimt, idx, :] = stddevs[iimt * nsd][
                        ictx * nporig : (ictx + 1) * nporig
                    ]
                    if len(sd_types) > 1:
                        taus[ictx, iimt, idx, :] = stddevs[iimt * nsd + 1][
                            ictx * nporig : (ictx + 1) * nporig
                        ]
                        phis[ictx, iimt, idx, :] = stddevs[iimt * nsd + 2][
                            ictx * nporig : (ictx + 1) * nporig
                        ]

        # Compute Mean, Sigma, Phi, and Tau for each IMT
        for iimt in range(nimt):
            outdict[myimts[iimt]] = {}
            for ictx, ctx_name in enumerate(ctxt_names):
                # Take the mean over the realizations
                if self.measure == "median":
                    mean_amps = np.median(amps[ictx, iimt], axis=0)
                else:
                    mean_amps = np.mean(amps[ictx, iimt], axis=0)
                # Compute the residuals for the simulations
                residuals = amps[ictx, iimt] - mean_amps
                # Find the variance over the realizations, this is the variance we
                # have to account for
                extra_vars = np.var(amps[ictx, iimt], axis=0)

                try:
                    avg_extra_tau = np.var(np.mean(residuals, axis=1))
                    avg_extra_phi = np.mean(np.var(residuals, axis=1))
                except RuntimeWarning as exc:
                    # Don't have an answer, so just guess
                    print(f"Error in FFSimmer: {exc}")
                    print("Using defaults")
                    avg_extra_tau = 0.20
                    avg_extra_phi = 0.80

                if (
                    np.isnan(avg_extra_tau)
                    or np.isnan(avg_extra_phi)
                    or avg_extra_tau < 1e-8
                    or avg_extra_phi < 1e-8
                ):
                    print("mixedlm.fit produced unusable results")
                    avg_extra_tau = 0.20
                    avg_extra_phi = 0.80

                avg_tau_wgt = avg_extra_tau / (avg_extra_tau + avg_extra_phi)
                avg_phi_wgt = 1.0 - avg_tau_wgt
                extra_taus = avg_tau_wgt * extra_vars
                extra_phis = avg_phi_wgt * extra_vars

                mean_sigs = np.sqrt(np.mean(sigs[ictx, iimt] ** 2, axis=0) + extra_vars)
                if len(sd_types) > 1:
                    mean_taus = np.sqrt(
                        np.mean(taus[ictx, iimt] ** 2, axis=0) + extra_taus
                    )
                    mean_phis = np.sqrt(
                        np.mean(phis[ictx, iimt] ** 2, axis=0) + extra_phis
                    )

                outdict[myimts[iimt]].update(
                    {
                        ctx_name: {
                            "mean": mean_amps.reshape(sctx.lons.shape),
                            oqconst.StdDev.TOTAL: mean_sigs.reshape(sctx.lons.shape),
                        }
                    }
                )
                if len(sd_types) > 1:
                    outdict[myimts[iimt]][ctx_name][oqconst.StdDev.INTER_EVENT] = (
                        mean_taus.reshape(sctx.lons.shape)
                    )
                    outdict[myimts[iimt]][ctx_name][oqconst.StdDev.INTRA_EVENT] = (
                        mean_phis.reshape(sctx.lons.shape)
                    )
        return outdict

    def true_grid(self, grid, gmpe, myimts):
        """
        Perform the simulations on a full grid, including the actual Vs30
        Args:
            grid (Grid2D object):
                The vs30grid that we're mapping.
            gmpe (MultiGMPE object):
                The MultiGMPE to be used for the simulations.
            myimts (list):
                List of OQ IMTs to generate grids and transects for

        Returns:
            dictionary:
                {
                    oqimt: {
                        "mean": 2D Array (the median or mean ground motion values, at
                            a Vs30 of 760 m/s),
                        oqconst.StdDev.TOTAL: Array,
                        (if allowed:)
                        oqconst.StdDev.INTER_EVENT: Array,
                        oqconst.StdDev.INTRA_EVENT: Array,
                    },
                }
        """
        griddict = {}
        sd_types = list(gmpe[myimts[0]].DEFINED_FOR_STANDARD_DEVIATION_TYPES)
        sites = Sites(grid, defaultVs30=760.0)
        (nx, ny) = sites.getNxNy()
        sctx = sites.getSitesContext()
        for k in sctx.__dict__:
            if k == "_slots_":
                continue
            sctx.__dict__[k] = sctx.__dict__[k].flatten()

        nsim = self.rff.get_nsim()
        nimt = len(myimts)
        amps = np.empty((nimt, nsim, nx * ny))
        sigs = np.empty((nimt, nsim, nx * ny))
        if len(sd_types) > 1:
            taus = np.empty((nimt, nsim, nx * ny))
            phis = np.empty((nimt, nsim, nx * ny))

        for idx in range(nsim):
            rupt = self.rff.retrieve_rupt(idx)
            dist = Distance.fromSites(gmpe[myimts[0]], sites, rupt)
            dctx = dist.getDistanceContext()
            for k in dctx.__dict__:
                if k == "_slots_":
                    continue
                if not isinstance(dctx.__dict__[k], np.ndarray):
                    continue
                dctx.__dict__[k] = dctx.__dict__[k].flatten()
            rctx = rupt.getRuptureContext(gmpe[myimts[0]])

            for iimt, simt in enumerate(myimts):
                mean, stddevs = gmpe[simt].get_mean_and_stddevs(
                    sctx, rctx, dctx, simt, sd_types
                )
                amps[iimt, idx, :] = mean[0]
                sigs[iimt, idx, :] = stddevs[0][0]
                if len(sd_types) > 1:
                    taus[iimt, idx, :] = stddevs[1][0]
                    phis[iimt, idx, :] = stddevs[2][0]

        # Compute Mean, Sigma, Phi, and Tau for each IMT
        for iimt in range(nimt):
            if self.measure == "median":
                mean_amps = np.median(amps[iimt], axis=0)
            else:
                mean_amps = np.mean(amps[iimt], axis=0)
            residuals = amps[iimt] - mean_amps
            extra_vars = np.var(amps[iimt], axis=0)

            try:
                avg_extra_tau = np.var(np.mean(residuals, axis=1))
                avg_extra_phi = np.mean(np.var(residuals, axis=1))
            except RuntimeWarning as exc:
                # Don't have an answer, so just guess
                print(f"Error in FFSimmer: {exc}")
                print("Using defaults")
                avg_extra_tau = 0.20
                avg_extra_phi = 0.80

            if (
                np.isnan(avg_extra_tau)
                or np.isnan(avg_extra_phi)
                or avg_extra_tau < 1e-8
                or avg_extra_phi < 1e-8
            ):
                print("mixedlm.fit produced unusable results")
                avg_extra_tau = 0.20
                avg_extra_phi = 0.80

            avg_tau_wgt = avg_extra_tau / (avg_extra_tau + avg_extra_phi)
            avg_phi_wgt = 1.0 - avg_tau_wgt
            extra_taus = avg_tau_wgt * extra_vars
            extra_phis = avg_phi_wgt * extra_vars

            # Take the mean over the realizations
            mean_sigs = np.sqrt(np.mean(sigs[iimt] ** 2, axis=0) + extra_vars)
            if len(sd_types) > 1:
                mean_taus = np.sqrt(np.mean(taus[iimt] ** 2, axis=0) + extra_taus)
                mean_phis = np.sqrt(np.mean(phis[iimt] ** 2, axis=0) + extra_phis)

            griddict[myimts[iimt]] = {
                "mean": mean_amps.reshape((ny, nx)),
                oqconst.StdDev.TOTAL: mean_sigs.reshape((ny, nx)),
            }
            if len(sd_types) > 1:
                griddict[myimts[iimt]][oqconst.StdDev.INTER_EVENT] = mean_taus.reshape(
                    (ny, nx)
                )
                griddict[myimts[iimt]][oqconst.StdDev.INTRA_EVENT] = mean_phis.reshape(
                    (ny, nx)
                )

        return griddict


class RandomFiniteFault(object):
    """
    Class to dole out random finite faults efficiently.
    """

    def __init__(
        self,
        origin,
        nsim,
        min_strike=-180.0,
        max_strike=180.0,
        min_dip=None,
        max_dip=None,
        dx_min_frac=0.0,
        dx_max_frac=1.0,
        delta_depth=20.0,
        ztor=-1,
        seed=None,
    ):
        """
        Args:
            origin (Origin object): The origin of the earthquake. Can include
                attributes "tectonic_region" ("Active", "Stable", "Subduction" are
                recognized) and "mech" ("ALL", "NM" (normal), "RS" (reverse), "SS"
                (strike-slip)).
            nsim (int): The number of simulations to run.
            min_strike/max_strike (float/float): Limit the range of the strike (in
                degrees) of realized faults. The default -180/180 allows any strike.
            min_dip/max_dip (float/float): Limit the range of the dip (in degrees)
                of the realized faults. The default is to use the "mech" of the
                origin to limit the range or, if none, use the "ALL" mech which
                defaults to 35/90.
            dx_min_frac/dx_max_frac (float/float): Limit the range of the along-
                strike placement of the hypocenter to from dx_min_frac * length to
                dx_max_frac * length. (default 0.0/1.0)
            delta_depth (float): The depth range of the hypocenter is uniformly drawn
                from depth - delta_depth to depth + delta_depth (kilometers)
                (Default: 20.0)
            ztor (float): Fix the top of rupture to a specific depth (kilometers,
                positive down). Negative values allow the TOR to float. (Default -1.)
            seed (int): A seed for the random number generator (for testing only).
        """
        self.origin = origin
        self.nsim = nsim
        self.rupts = []
        self.rng = np.random.default_rng(seed)
        self.initialize(
            min_strike,
            max_strike,
            min_dip,
            max_dip,
            dx_min_frac,
            dx_max_frac,
            delta_depth,
            ztor,
        )

    def initialize(
        self,
        min_strike,
        max_strike,
        min_dip,
        max_dip,
        dx_min_frac,
        dx_max_frac,
        delta_depth,
        ztor,
    ):
        """
        Initialize the random arrays
        """
        (mscale, aspect, mindip_deg, maxdip_deg, szdepth, smech) = get_scaling_params(
            self.origin
        )
        _, _, _, _, area_mean, area_std = dimensions_from_magnitude(
            self.origin.mag, mscale, 1, 0, smech
        )
        hypo = self.origin.getHypo()
        depth = hypo.z
        if depth > szdepth:
            szdepth = depth
        depth = self.rng.uniform(
            np.maximum(depth - delta_depth, 0),
            np.minimum(depth + delta_depth, szdepth),
            self.nsim,
        )
        area = 10 ** self.rng.normal(np.log10(area_mean[0]), area_std, self.nsim)
        width = np.sqrt(area / aspect)
        if min_dip is not None:
            mindip_deg = min_dip
            maxdip_deg = max_dip
        dip = np.radians(self.rng.uniform(mindip_deg, maxdip_deg, self.nsim))
        # Need to apply a max to dy that might be less than width based on the
        # eq depth.
        # height = vertical projection of plane
        # height = width * sin(dip)
        #  ------------------
        #  _____ztor       |
        #  \dip    |       |
        #   \      |       |
        #    \     |       |
        #   dy\    |height |
        #      *- -|- - - - depth
        #       \  |
        #        \ |
        #    width\|
        #
        #  ---------------- szdepth
        #
        height = width * np.sin(dip)
        # Don't allow the rupture to extend below the seismogenic depth
        height[height > szdepth] = szdepth
        width = height / np.sin(dip)
        # Limit the rupture to stay between the surface and the szdepth
        # but allow it to float in between
        if ztor < 0:
            dy = self.rng.uniform(
                np.maximum(0, width - (szdepth - depth) / np.sin(dip)),
                np.minimum(width, width - (height - depth) / np.sin(dip)),
            )
        else:
            # Fix ztor to a specific depth. This is a weak contraint: there is
            # no guarantee that for a given depth, dip, and width that the TOR
            # will reach ztor
            dy = (depth - ztor) / np.sin(dip)
            dy[dy > width] = width[dy > width]

        length = area / width
        dx = self.rng.uniform(dx_min_frac * length, dx_max_frac * length)
        strike = self.rng.uniform(min_strike, max_strike, self.nsim)
        hx = np.array([hypo.x])
        hy = np.array([hypo.y])

        for idx in range(self.nsim):
            self.rupts.append(
                QuadRupture.fromOrientation(
                    hx,
                    hy,
                    np.array([depth[idx]]),
                    [dx[idx]],
                    [dy[idx]],
                    [length[idx]],
                    [width[idx]],
                    [strike[idx]],
                    [np.degrees(dip[idx])],
                    self.origin,
                )
            )

    def retrieve_rupt(self, isim):
        """
        Retrieve one fault.
        """
        if isim > self.nsim:
            raise IndexError(
                f"RandomFiniteFault.retrieve_rupt {isim=} exceeds maximum {self.nsim}"
            )
        return self.rupts[isim]

    def get_nsim(self):
        """
        Get the number of simulated faults that this object holds.
        """
        return self.nsim


def get_scaling_params(origin):
    """

    Args:
        origin:
            An Origin object.
    """

    mech = getattr(origin, "mech", "ALL")
    if not hasattr(origin, "tectonic_region"):
        mscale = MagScaling.WC94
        smech = Mechanism.ALL
        mindip_deg = 35.0
        maxdip_deg = 90.0
        aspect = 1.7
        szdepth = np.inf
    elif origin.tectonic_region == "Active":
        mscale = MagScaling.HB08
        aspect = 1.7
        szdepth = np.inf
        if mech == "ALL":
            # HB08 doesn't have an 'ALL' mechanism, so use WC94
            mscale = MagScaling.WC94
            smech = Mechanism.ALL
            mindip_deg = 35.0
            maxdip_deg = 90.0
        elif mech == "RS":
            smech = Mechanism.RS
            mindip_deg = 35.0
            maxdip_deg = 50.0
        elif mech == "NM":
            smech = Mechanism.NM
            mindip_deg = 40.0
            maxdip_deg = 60.0
        elif mech == "SS":
            smech = Mechanism.SS
            mindip_deg = 75.0
            maxdip_deg = 90.0
    elif origin.tectonic_region == "Stable":
        mscale = MagScaling.S14
        aspect = 1.0
        szdepth = np.inf
        if mech == "ALL":
            smech = Mechanism.ALL
            mindip_deg = 35.0
            maxdip_deg = 90.0
        elif mech == "RS":
            smech = Mechanism.RS
            mindip_deg = 35.0
            maxdip_deg = 60.0
        elif mech == "NM":
            smech = Mechanism.NM
            mindip_deg = 40.0
            maxdip_deg = 60.0
        elif mech == "SS":
            smech = Mechanism.SS
            mindip_deg = 60.0
            maxdip_deg = 90.0
    elif origin.tectonic_region == "Subduction":
        aspect = 1.7
        szdepth = np.inf
        if mech == "ALL":
            mscale = MagScaling.Sea10_interface
            smech = Mechanism.ALL
            mindip_deg = 35.0
            maxdip_deg = 90.0
        elif mech == "RS":
            mscale = MagScaling.Sea10_interface
            smech = Mechanism.RS
            mindip_deg = 35.0
            maxdip_deg = 50.0
        elif mech == "NM":
            mscale = MagScaling.Sea10_slab
            smech = Mechanism.NM
            mindip_deg = 40.0
            maxdip_deg = 60.0
        elif mech == "SS":
            mscale = MagScaling.Sea10_slab
            smech = Mechanism.SS
            mindip_deg = 75.0
            maxdip_deg = 90.0
    else:
        print(
            "Unsupported tectonic region; using coefficients for unknown"
            "tectonic region."
        )
        mscale = MagScaling.WC94
        smech = Mechanism.ALL
        aspect = 1.7
        szdepth = np.inf
        mindip_deg = 35.0
        maxdip_deg = 90.0

    return (mscale, aspect, mindip_deg, maxdip_deg, szdepth, smech)


def dimensions_from_magnitude(M, rup_dim_model, neps, trunc, mech=Mechanism.ALL):
    """
    Compute dimensions of rupture from magnitude for a specified
    magnitude scaling relation.

    Args:
        M (float): Magnitude.
        rup_dim_model (MagScaling enum): Specifies the model for compputing the
            rupture dimensions from magnitude.
        neps (int): The number of steps to integrate from -trunc to +trunc.
            Larger numbers increase the accuracy of the result, but take
            longer to run.
        trunc (float): For the integration in area (or length and width), trunc
            is the truncation of the normal distribution (in units of sigma).
        mech (Mechanism enum): Optional string indicating earthquake
            mechanism, used by some of the models.

    Returns:
        tuple: A tuple containing the following, noting that some of these will
        be empty if the selected model does not provide them:

                - length: rupture length (km).
                - sig_length: standard deviation of rupture length.
                - W: rupture width (km).
                - sigw: standard devation of rupture width.
                - A: rupture area (km).
                - siga: standard deivaiton of rupture area.

    """
    epsmid, _, _ = compute_epsilon(neps, trunc)
    if not isinstance(rup_dim_model, MagScaling):
        raise TypeError("rup_dim_model must be of type MagScaling")
    if not isinstance(mech, Mechanism):
        raise TypeError("mech must be of type Mechanism")

    if rup_dim_model is MagScaling.WC94:
        # Use mech to get either M-A or (M-W) and (M-R) from Wells and
        # Coppersmith.
        if mech is Mechanism.SS:
            sig_length = 0.15
            length = 10 ** (-2.57 + 0.62 * M + sig_length * epsmid)
            sig_width = 0.14
            width = 10 ** (-0.76 + 0.27 * M + sig_width * epsmid)
            sig_area = 0.22
            area = 10 ** (-3.42 + 0.90 * M + sig_area * epsmid)
        elif mech is Mechanism.RS:
            sig_length = 0.16
            length = 10 ** (-2.42 + 0.58 * M + sig_length * epsmid)
            sig_width = 0.15
            width = 10 ** (-1.61 + 0.41 * M + sig_width * epsmid)
            sig_area = 0.26
            area = 10 ** (-3.99 + 0.98 * M + sig_area * epsmid)
        elif mech is Mechanism.NM:
            sig_length = 0.17
            length = 10 ** (-1.88 + 0.50 * M + sig_length * epsmid)
            sig_width = 0.12
            width = 10 ** (-1.14 + 0.35 * M + sig_width * epsmid)
            sig_area = 0.22
            area = 10 ** (-2.78 + 0.82 * M + sig_area * epsmid)
        elif mech is Mechanism.ALL:
            sig_length = 0.16
            length = 10 ** (-2.44 + 0.59 * M + sig_length * epsmid)
            sig_width = 0.15
            width = 10 ** (-1.01 + 0.32 * M + sig_width * epsmid)
            sig_area = 0.24
            area = 10 ** (-3.49 + 0.91 * M + sig_area * epsmid)
        else:
            raise TypeError("Unsupported value of 'mech'")
    elif rup_dim_model is MagScaling.S14:
        # Somerville (2014) model:
        #     - No length or width
        #     - No mechanism dependence
        sig_area = 0.3
        area = 10 ** (M - 4.25 + sig_area * epsmid)
        length = None
        sig_length = None
        width = None
        sig_width = None
    elif rup_dim_model == MagScaling.HB08:
        # Hanks and Bakun (2008)
        # These are the equations reported in the paper:
        #     M =       log10(A) + 3.98   for A <= 537 km^2 w/ se=0.03
        #     M = 4/3 * log10(A) + 3.07   for A >  537 km^2 w/ se=0.04
        # Using them is not so straight-forward beacuse we need to compute
        # the area from magnitude. Of course, this gives a different result
        # than if the equations were regressed for A as a function of M,
        # although since the equations were derived theoretically, this may
        # not be so bad.
        #
        # The inverted equation is simple enough:
        #     log10(A) =      M - 3.98    for M <= 6.71
        #     log10(A) = 3/4*(M - 3.07))  for M > 6.71
        #
        # The standard deviations are a little trickier.
        # First, convert standard errors of M to standard deviations of M:
        # (by my count, n=62 for A<=537, and n=28 for A>537)
        #     0.03*sqrt(62) = 0.236       for M <= 6.71
        #     0.04*sqrt(28) = 0.212       for M > 6.71
        # And convert to standard deviations of log(A) using the partial
        # derivatives
        #     dM/d(log10(A)) = 1          for M <= 6.71
        #     dM/d(log10(A)) = 3/4        for M >  6.71
        # So
        #     0.236*1   = 0.236 (pretty close to WC94)
        #     0.212*3/4 = 0.159 (seems a bit low...)
        if M > 6.71:
            sig_area = 0.236
            area = 10 ** (3 / 4 * (M - 3.07) + sig_area * epsmid)
        else:
            sig_area = 0.159
            area = 10 ** ((M - 3.98) + sig_area * epsmid)
        length = None
        sig_length = None
        width = None
        sig_width = None
    elif rup_dim_model == MagScaling.Sea10_interface:
        # Strasser et al. (2010), coefficients for interface events
        sig_length = 0.18
        length = 10 ** (-2.477 + 0.585 * M + sig_length * epsmid)
        sig_width = 0.173
        width = 10 ** (-0.882 + 0.351 * M + sig_width * epsmid)
        sig_area = 0.304
        area = 10 ** (-3.49 + 0.952 * M + sig_area * epsmid)
    elif rup_dim_model == MagScaling.Sea10_slab:
        # Strasser et al. (2010), coefficients for slab events
        sig_length = 0.146
        length = 10 ** (-2.35 + 0.562 * M + sig_length * epsmid)
        sig_width = 0.067
        width = 10 ** (-1.058 + 0.356 * M + sig_width * epsmid)
        sig_area = 0.184
        area = 10 ** (-3.225 + 0.89 * M + sig_area * epsmid)
    else:
        raise TypeError("Unsupported value of 'rup_dim_model'")
    return length, sig_length, width, sig_width, area, sig_area


def compute_epsilon(neps, trunc):
    """
    Compute midpoints and probabilities of epsilon bins.

    Args:
        neps (int): The number of steps to integrate from -trunc to +trunc.
            Larger numbers increase the accuracy of the result, but take
            longer to run.
        trunc (float): For the integration in area (or length and width), trunc
            is the truncation of the normal distribution (in units of sigma).
    Returns:
        tuple: epsilon midpoints, their probabilities, bin width.
    """
    # Need to assume a truncation level for normal distribution
    eps = np.linspace(-trunc, trunc, neps + 1)
    epsmid = 0.5 * (eps[1:] + eps[:-1])
    peps = norm.cdf(eps[1:]) - norm.cdf(eps[:-1])

    # define delta epsilons to normalize probabilities
    d_eps = 2 * trunc / neps
    epsfac = np.trapz(peps, dx=d_eps)

    if neps > 1:
        peps /= epsfac
    return epsmid, peps, d_eps
