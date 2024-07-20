#!/usr/bin/env python
"""
    #####################################################################

    Copyright (C) 1999-2024, Michele Cappellari
    E-mail: michele.cappellari_at_physics.ox.ac.uk

    For details on the method see:

        Cappellari M., 2002, MNRAS, 333, 400
        https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C

    Updated versions of the software are available from my web page
    https://purl.org/cappellari/software

    If you have found this software useful for your
    research, I would appreciate an acknowledgement to use of
    `the MGE fitting method and software by Cappellari (2002)'.

    This software is provided as is without any warranty whatsoever.
    Permission to use, for non-commercial purposes is granted.
    Permission to modify for personal or internal use is granted,
    provided this copyright and disclaimer are included unchanged
    at the beginning of the file. All other rights are reserved.
    In particular, redistribution of the code is not allowed.

    #####################################################################

    Changelog
    ---------

    V1.0.0 Michele Cappellari, Padova, February 2000

    V1.1.0 Minor revisions, MC, Leiden, June 2001

    V1.2.0 Updated documentation, MC, 18 October 2001

    V1.3.0 Added compilation options and explicit stepsize in parinfo
    structure of MPFIT, MC, Leiden 20 May 2002

    V1.3.1 Added ERRMSG keyword to MPFIT call. Leiden, 13 October 2002, MC

    V1.3.2: Use N_ELEMENTS instead of KEYWORD_SET to test
    non-logical keywords. Leiden, 9 May 2003, MC

    V1.3.3: Use updated calling sequence for BVLS. Leiden, 20 March 2004, MC

    V1.4.0: Force the surface brightness of the MGE model to decrease at
    least as R^-2 at the largest measured radius. Leiden, 8 May 2004, MC

    V1.4.1: Make sure this routine uses the Nov/2000 version of Craig Markwardt
    MPFIT which was renamed MGE_MPFIT to prevent potential conflicts with
    more recent versions of the same routine. Vicenza, 23 August 2004, MC.

    V1.4.2: Allow forcing the outer slope of the surface brightness profile of
    the MGE model to decrease at least as R^-n at the largest measured
    radius (cfr. version 1.4.0). Leiden, 23 October 2004, MC

    V1.4.3: Changed axes labels in plots. Leiden, 18 October 2005, MC

    V1.4.4: Fixed display not being updated while iterating under Windows.
    MC, Frankfurt, 21 July 2009

    V1.4.5: Fixed minor plotting bug introduced in V1.4.3.
    Show individual values with diamonds in profiles.
    MC, Oxford, 10 November 2009

    V1.4.6: Added keyword /QUIET. MC, Oxford, 12 November 2010

    V1.4.7: Added /NEGATIVE keyword as in the other routines of the package,
    after feedback from Nora Lutzgendorf. MC, Oxford, 15 June 2011

    V1.4.8: Suppress both printing and plotting with /QUIET keyword.
    MC, Oxford, 17 September 2011

    V2.0.0: Translated from IDL into Python. MC, Aspen Airport, 8 February 2014

    V2.0.1: Support both Python 2.6/2.7 and Python 3. MC, Oxford, 25 May 2014

    V2.0.2: Improved formatting of printed output. MC, Oxford, 16 April 2015

    V2.0.3: Properly print nonzero Gaussians only. MC, Atlantic Ocean, 6 June 2015

    V2.0.4: Only plot profiles for the best-fitting MGE. MC, Oxford, 6 July 2015

    V2.0.5: Allow for ``plot()`` to be called after the program terminates.
    Warns of large residuals in the final fit. MC, Oxford, 8 February 2017

    V2.0.6: Included `inner_slope` and `fignum` keywords.
    Plot sigma lines with same color as corresponding Gaussians.
    Adapted for Matplotlib 2.0. MC, Oxford, 10 February 2017

    V2.0.7: Changed imports for ``mgefit`` package. MC, Oxford, 17 April 2018

    V2.0.8: Fixed ``clock`` ``DeprecationWarning`` in Python 3.7.
    MC, Oxford, 27 September 2018

    V2.0.9: Updated documentation. Formatted docstring in reStructuredText.
    MC, Oxford, 6 December 2018

    V2.0.10: Use SciPy 1.1 `maxiter` keyword in `nnls`. MC, Oxford, 24 June 2019

    V2.0.11: Updated documentation.
    Thanks to Peter Teuben (umd.edu) for the feedback.
    MC, Oxford, 24 March 2021

    Vx.x.xx: Additional changes are now documented in the global CHANGELOG.rst
    file of the MgeFit package

"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg
from time import perf_counter as clock

from mgefit.cap_mpfit import mpfit
from capfit.capfit import lsq_box

#----------------------------------------------------------------------------

def linspace_open(a, b, num=50):

    dx = (b - a)/num
    x = a + (0.5 + np.arange(num))*dx

    return x

#----------------------------------------------------------------------------

class mge_fit_1d:
    """
    mge_fit_1d
    ==========

    Purpose
    -------

    Approximates the 1-dim radial profile of the density or surface-brightness 
    of a galaxy with a Multi-Gaussian Expansion (MGE) model, using the robust 
    and automated fitting method of
    `Cappellari (2002) <https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C>`_.

    Calling Sequence
    ----------------
    .. code-block:: python

        p = mge_fit_1d(x, y, negative=False, ngauss=12, rbounds=None,
                       inner_slope=2, outer_slope=3, quiet=False, fignum=1)
        
        total_counts, sigma = p.sol  # Assign the solution to variables
        print(p.sol.T)  # Print a table of best-fitting MGE parameters

    See usage example at the end of this file.

    Parameters
    ----------
    x: array_like with shape (n,)
        Vector of the logarithmically sampled (Important!)
        abscissa for the profile that has to be fitted.
    y: array_like with shape (n,)
        Ordinate of the profile evaluated at the abscissa `x`.

    More Parameters
    ---------------
    ngauss :
        Number of Gaussian one wants to fit. Typical values are 10-20.

    negative :
        Set ``negative=True`` to allow for negative Gaussians in the fit.
        Use this only if there is clear evidence that negative Gaussians
        are actually needed e.g. to fit a radially increasing profile.

    inner_slope :
        This scalar forces the surface brightness profile of the MGE model to
        decrease as ``R**(-inner_slope)`` at the smallest measured radius
        (Default: ``inner_slope=2``). The default is generally ok, but it can
        be changed e.g. to allow for steeper inner profiles.

    outer_slope :
        This scalar forces the surface brightness profile of the MGE model to
        decrease as ``R**(-outer_slope)`` at the largest measured radius
        (Default: ``outer_slope=3``). The default is generally ok, but it can
        be changed e.g. to allow for a sharper outer truncation.

    rbounds :
        Two elements vector giving the minimum and maximum sigma allowed in the
        MGE fit. This is in the same units of ``x``. With this keyword,
        ``inner_slope`` and ``outer_slope`` are ignored.

    quiet :
        Set ``quiet=True`` to suppress plots and printed output.

    Returns
    -------
    Stored as attributes of the ``mge_fit_1d`` class:

    .sol : array_like with shape (2, ngauss)
        Contains an array with the best-fitting solution:

        .sol[0] : array_like with shape (ngauss)
            ``total_counts`` (area under the 1-dim curve) of the Gaussians.

        .sol[1] : array_like with shape (ngauss)
            ``sigma``, is the dispersion of the Gaussians in units of ``x``.

        IMPORTANT: Given the ``total_counts`` definition:

        - If the fit was done to the projected surface density profile
          ``(Msun/pc^2)`` the Gaussians peak surface densities in the same
          units are given by::

            surf = total_counts/(np.sqrt(2*np.pi)*sigma)

        - If the fit was done to the intrinsic density profile ``(Msun/pc^3)``
          the Gaussians peak densities in the same units are still given by::

            dens = total_counts/(np.sqrt(2*np.pi)*sigma)

        - In either case, one can convert between the MGE describing the
          intrinsic density in ``(Msun/pc^3)`` to the MGE parametrizing the
          projected surface density in ``(Msun/pc^2)`` using equation (38) of
          `Cappellari (2020) <https://ui.adsabs.harvard.edu/abs/2020MNRAS.494.4819C>`_::

            dens = surf/(np.sqrt(2*np.pi)*sigma)
            
          EXAMPLE: If one fits an intrinsic density profile in ``(Msun/pc^3)``,
          the output attribute .sol[0] already contains the peak surface
          brightness ``surf`` of the *projected* MGE in ``(Msun/pc^2)``.

    Example
    -------
    The sequence of commands below was used to generate the
    one-dimensional MGE fit of Fig.3 in `Cappellari (2002)`_

    .. code-block:: python

        import numpy as np
        from mgefit.mge_fit_1d import mge_fit_1d

        n = 300 # Number of sampled points
        R = np.geomspace(0.01, 300, n)  # radii must be logarithmically sampled
        rho = (1 + R)**(-4)
        p = mge_fit_1d(R, rho, ngauss=16)

    ###########################################################################
    """
    def __init__(self, x, y, negative=False, ngauss=15, rbounds=None,
                 inner_slope=2, outer_slope=3, quiet=False, plot=False, fignum=1):

        assert x.size == y.size, '[X, Y] must have the same size'

        self.x = x  # load parameters into class
        self.y = y
        self.negative = negative

        inner_slope = np.clip(inner_slope, 1, 4)
        outer_slope = np.clip(outer_slope, 1, 4)
        if rbounds is None:
            lrbounds = np.log10([np.min(x)/np.sqrt(inner_slope), np.max(x)/np.sqrt(outer_slope)])
        else:
            lrbounds = np.log10(rbounds)

        log_sigma = linspace_open(*lrbounds, num=ngauss)
        parinfo = [{'step':0.01, 'limits':lrbounds, 'limited':[1,1]}
                    for j in range(ngauss)]

        if quiet:
            iterfunc = None
        else:
            iterfunc = self._print

        t = clock()
        mp = mpfit(self._fitfunc, log_sigma, iterfunct=iterfunc,
                   nprint=10, parinfo=parinfo, quiet=quiet)

        if mp.status <= 0:
            print("Mpfit error: %d, status: %d" % (mp.errmsg, mp.status))

        # Print the results for the nonzero Gaussians sorted by increasing sigma
        w = self.weights != 0
        self.weights, self.gauss, self.log_sigma = self.weights[w], self.gauss[:, w], mp.params[w]
        j = np.argsort(self.log_sigma)
        self.sol = np.vstack([self.weights[j], 10**self.log_sigma[j]])

        if np.any(np.abs(self.err) > 0.1):
            print("Residuals > 10%: Change `inner_slope` or `outer_slope` or increase `ngauss`")

        if not quiet:
            self._print(0, self.log_sigma, mp.niter, mp.fnorm) # plot best fitting solution
            print('############################################')
            print('  Computation time: %.2f seconds' % (clock() - t))
            print('  Total Iterations: ', mp.niter)
            print(' Nonzero Gaussians: ', self.log_sigma.size)
            print('  Unused Gaussians: ', ngauss - self.log_sigma.size)
            print(' Chi2: %.4g ' % mp.fnorm)
            print(' STDEV: %.4g' % np.std(self.err))
            print(' MEANABSDEV: %.4g' % np.mean(np.abs(self.err)))
            print('############################################')
            print('  Total_Counts       Sigma')
            print('############################################')
            for sol in self.sol.T:
                print(('{:13.4e} {:#13.4g}').format(*sol))
            print('############################################')

        if plot:
            self.plot(fignum)

#----------------------------------------------------------------------------

    def _print(self, myfunct, logsigma, it, fnorm,
                functkw=None, args=None, parinfo=None, dof=None, quiet=False):
        """
        This is called every NPRINT iterations of MPFIT

        """
        print('Iteration: %d  chi2: %#.4g Nonzero: %d/%d' %
              (it, fnorm, np.sum(self.weights != 0), self.weights.size))

#----------------------------------------------------------------------------

    def plot(self, fignum=1):
        """
        Produces final best-fitting plot

        """
        f, ax = plt.subplots(2, 1, sharex=True, num=fignum)
        f.subplots_adjust(hspace=0.03)

        miny = self.y.min()
        maxy = self.y.max()
        yran = miny*(maxy/miny)**np.array([-0.05, 1.05])

        ax[0].set_ylim(yran)
        ax[0].loglog(self.x, self.y, 'o')
        ax[0].loglog(self.x, self.yfit)
        ax[0].loglog(self.x, self.gauss*self.weights[None, :])
        ax[0].set_ylabel("arcsec")
        ax[0].set_ylabel("counts")

        ax[1].set_ylim([-20, 20])
        ax[1].axhline(linestyle='--', c='C1')
        ax[1].semilogx(self.x, self.err*100, c='C0')
        ax[1].semilogx(np.tile(10**self.log_sigma, [2, 1]), [-20, -15])
        ax[1].set_xlabel("arcsec")
        ax[1].set_ylabel("residuals (%)")

#----------------------------------------------------------------------------

    def _fitfunc(self, logSigma, fjac=None):

        sigma2 = 10**(2*logSigma)
        self.gauss = np.exp(-self.x[:, None]**2/(2*sigma2))
        self.gauss /= np.sqrt(2.*np.pi*sigma2)
        A = self.gauss / self.y[:, None]
        b = np.ones_like(self.x)

        if self.negative:  # Solution by LAPACK linear least-squares
            self.weights = linalg.lstsq(A, b)[0]
        else:             # Solution by NNLS
            self.weights = lsq_box(A, b, bounds=(0, np.inf)).x

        self.yfit = self.gauss @ self.weights
        self.err = 1 - self.yfit / self.y

        return self.err.astype(np.float32)

#----------------------------------------------------------------------------

def example_mge_fit_1d():
    """
    Usage example for mge_fit_1d().
    This example reproduces Figure 3 in Cappellari (2002)
    It takes <1s on a 2.5 GHz computer

    """
    n = 300  # number of sampled points
    x = np.geomspace(0.01, 300, n)  # logarithmically spaced radii
    y = (1 + x)**-4  # The profile must be logarithmically sampled!
    p = mge_fit_1d(x, y, ngauss=16, plot=True)
    plt.pause(1)  # allow the plot to appear in certain situations

#----------------------------------------------------------------------------

if __name__ == '__main__':
    example_mge_fit_1d()
