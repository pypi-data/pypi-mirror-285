from pathlib import Path

import numpy as np
from scipy import special
from scipy.stats import binned_statistic, halfnorm, lognorm, multivariate_normal, norm
from tqdm import trange

from .utils import PACKAGEDIR, PARAMS_PATH, extend, find_consecutive

RNG = np.random.default_rng(0)
MU_AMP, MU_FWHM, SIGMA_AMP, SIGMA_FWHM, RHO = np.load(PARAMS_PATH, allow_pickle=True)
MEAN = np.array([MU_AMP, MU_FWHM])
COV = np.array([[SIGMA_AMP**2, RHO * SIGMA_AMP * SIGMA_FWHM], [RHO * SIGMA_AMP * SIGMA_FWHM, SIGMA_FWHM**2]])
BIVARIATE_NORMAL = multivariate_normal(MEAN, COV)
CADENCE = 2  # minutes


def flare_eqn(t, ampl):
    """
    This function is from https://github.com/lupitatovar/Llamaradas-Estelares.

    The equation that defines the shape for the Continuous Flare Model
    """
    # Values were fit & calculated using MCMC 256 walkers and 30000 steps

    A, B, C, D1, D2, f1 = [
        0.9687734504375167,
        -0.251299705922117,
        0.22675974948468916,
        0.15551880775110513,
        1.2150539528490194,
        0.12695865022878844,
    ]

    f2 = 1 - f1

    eqn = (
        (1 / 2)
        * np.sqrt(np.pi)
        * A
        * C
        * f1
        * np.exp(-D1 * t + ((B / C) + (D1 * C / 2)) ** 2)
        * special.erfc(((B - t) / C) + (C * D1 / 2))
    ) + (
        (1 / 2)
        * np.sqrt(np.pi)
        * A
        * C
        * f2
        * np.exp(-D2 * t + ((B / C) + (D2 * C / 2)) ** 2)
        * special.erfc(((B - t) / C) + (C * D2 / 2))
    )
    return eqn * ampl


def flare_model(t, tpeak, fwhm, ampl, upsample=False, uptime=10):
    """
    This function is from https://github.com/lupitatovar/Llamaradas-Estelares.

    The Continuous Flare Model evaluated for single-peak (classical) flare events.
    Use this function for fitting classical flares with most curve_fit
    tools. Reference: Tovar Mendoza et al. (2022) DOI 10.3847/1538-3881/ac6fe6

    References
    --------------
    Tovar Mendoza et al. (2022) DOI 10.3847/1538-3881/ac6fe6
    Davenport et al. (2014) http://arxiv.org/abs/1411.3723
    Jackman et al. (2018) https://arxiv.org/abs/1804.03377

    Parameters
    ----------
    t : 1-d array
        The time array to evaluate the flare over

    tpeak : float
        The center time of the flare peak

    fwhm : float
        The Full Width at Half Maximum, timescale of the flare

    ampl : float
        The amplitude of the flare


    Returns
    -------
    flare : 1-d array
        The flux of the flare model evaluated at each time

        A continuous flare template whose shape is defined by the convolution of a Gaussian and double exponential
        and can be parameterized by three parameters: center time (tpeak), FWHM, and ampitude
    """

    t_new = (t - tpeak) / fwhm

    if upsample:
        dt = np.nanmedian(np.diff(np.abs(t_new)))
        timeup = np.linspace(min(t_new) - dt, max(t_new) + dt, t_new.size * uptime)

        flareup = flare_eqn(timeup, ampl)

        # and now downsample back to the original time...

        downbins = np.concatenate((t_new - dt / 2.0, [max(t_new) + dt / 2.0]))
        flare, _, _ = binned_statistic(timeup, flareup, statistic="mean", bins=downbins)
    else:
        flare = flare_eqn(t_new, ampl)

    return flare


def simulate_flare():
    ln_fwhm = 0
    while ln_fwhm < 1:
        ln_amp, ln_fwhm = BIVARIATE_NORMAL.rvs(random_state=RNG)
    t_fwhm = np.exp(ln_fwhm)
    t_length = t_fwhm * 10
    time = np.arange(t_length // CADENCE) * CADENCE

    amp = np.exp(ln_amp)
    model = flare_model(time, 2 * t_fwhm, t_fwhm, amp, upsample=True, uptime=10)

    return model


def simulate_non_flare():
    t_length = 0
    while t_length < CADENCE:
        sigma = lognorm.rvs(s=1, scale=np.exp(3), random_state=RNG)
        t_length = sigma * 8
    time = np.arange(t_length // CADENCE) * CADENCE

    model = norm.pdf(time, loc=t_length / 2, scale=sigma)
    amp = halfnorm.rvs(random_state=RNG)
    model *= amp / model.max()

    return model


def generate_simulated_event(event_type):
    satisfied = False
    while not satisfied:
        if event_type == "flare":
            model = simulate_flare()
        elif event_type == "non-flare":
            model = simulate_non_flare()
        else:
            raise ValueError

        flux = RNG.standard_normal(model.size + 10)
        i_outliers = (flux > 3) | (flux < -3)
        while i_outliers.any():
            flux[i_outliers] = RNG.standard_normal(np.nonzero(i_outliers)[0].size)
            i_outliers = (flux > 3) | (flux < -3)
        flux[5:-5] += model

        i_outliers = np.nonzero(flux > 3)[0]
        i_start, i_stop = find_consecutive(i_outliers, 2)

        if i_start is None or i_start.size == 0:
            continue

        time = np.arange(flux.size) * CADENCE / 1440
        if i_start.size > 1:
            n_groups = len(i_start)
            flux_max = np.zeros(n_groups)
            for i in range(n_groups):
                flux_max[i] = np.max(flux[i_start[i] : i_stop[i]])
            t_start = time[i_start[flux_max.argmax()]]
            t_stop = time[i_stop[flux_max.argmax()]]
        else:
            t_start = time[i_start]
            t_stop = time[i_stop]

        t_start_ext, t_stop_ext = extend(time, flux, t_start, t_stop, 1, n_right=2)
        flux = flux[np.nonzero((t_start_ext <= time) & (time <= t_stop_ext))]

        if flux.size < 4:
            continue
        if event_type == "non-flare" and flux.argmax() / (flux.size - 1) < 0.5 and flux.size >= 5:
            continue

        i_outliers = np.nonzero(flux > 3)[0]
        i_start, i_stop = find_consecutive(i_outliers, 2)
        if i_start is None:
            continue

        satisfied = True

    return np.column_stack([np.arange(flux.size) * CADENCE, flux])


def generate_simulated_data(n_train=3000, n_validation=1000, n_test=1000, sim_path=PACKAGEDIR / "simulation"):
    sim_path.mkdir(exist_ok=True)
    for n_simulation, set_type in zip([n_train, n_validation, n_test], ["training", "validation", "test"]):
        flare_simulations = []
        non_flare_simulations = []
        for _ in trange(n_simulation, desc="Generating"):
            flare_data = generate_simulated_event("flare")
            flare_simulations.append(flare_data)

            non_flare_data = generate_simulated_event("non-flare")
            non_flare_simulations.append(non_flare_data)

        np.savez(sim_path / Path("{}-flare.npz".format(set_type)), *flare_simulations)
        np.savez(sim_path / Path("{}-non-flare.npz".format(set_type)), *non_flare_simulations)
