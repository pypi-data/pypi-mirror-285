import numpy as np

from openquake.hazardlib import const
from openquake.hazardlib.contexts import ContextMaker


def gmpe_gmas(gmpe, ctx, imt, stddev_types):
    """ """
    if isinstance(imt, list):
        nlist = len(imt)
        imtstr = imt[0].string
        imtl = imt
    else:
        nlist = 1
        imtstr = imt.string
        imtl = [imt]
    N = len(ctx)
    mean = np.zeros((nlist, N))
    sig = np.zeros((nlist, N))
    tau = np.zeros((nlist, N))
    phi = np.zeros((nlist, N))
    if gmpe.compute.__annotations__.get("ctx") is np.recarray:
        if isinstance(ctx.mag, np.ndarray):
            magstr = "%.2f" % ctx.mag[0]
        else:
            magstr = "%.2f" % ctx.mag
        param = dict(
            imtls={imtstr: [0]},
            maximum_distance=4000,
            truncation_level=3,
            investigation_time=1.0,
            mags=[magstr],
        )
        cmaker = ContextMaker("*", [gmpe], param)
        if not isinstance(ctx, np.ndarray):
            ctx = cmaker.recarray([ctx])
    try:
        gmpe.compute(ctx, imtl, mean, sig, tau, phi)
    except NotImplementedError:
        mean, stddevs = gmpe.get_mean_and_stddevs(ctx, ctx, ctx, imt, stddev_types)
        return mean, stddevs
    except Exception as exc:
        raise exc
    else:
        stddevs = []
        for i in range(nlist):
            for stddev_type in stddev_types:
                if stddev_type == const.StdDev.TOTAL:
                    stddevs.append(sig[i])
                elif stddev_type == const.StdDev.INTER_EVENT:
                    stddevs.append(tau[i])
                elif stddev_type == const.StdDev.INTRA_EVENT:
                    stddevs.append(phi[i])
        return mean, stddevs
