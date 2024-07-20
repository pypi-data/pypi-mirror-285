"""
    Copyright (C) 1999-2024, Michele Cappellari

    E-mail: michele.cappellari_at_physics.ox.ac.uk

    Updated versions of the software are available from my web page
    https://purl.org/cappellari/software

    If you have found this software useful for your
    research, I would appreciate an acknowledgement to use of
    "the MGE fitting method and software by Cappellari (2002)".

    https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C

    This software is provided as is without any warranty whatsoever.
    Permission to use, for non-commercial purposes is granted.
    Permission to modify for personal or internal use is granted,
    provided this copyright and disclaimer are included unchanged
    at the beginning of the file. All other rights are reserved.
    In particular, redistribution of the code is not allowed.

"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import special
from time import perf_counter as clock

from mgefit.cap_mpfit import mpfit
from capfit.capfit import lsq_box

#----------------------------------------------------------------------------

def linspace_open(a, b, num=50):

    dx = (b - a)/num
    x = a + (0.5 + np.arange(num))*dx

    return x

#----------------------------------------------------------------------------

class mge_fit_sectors:
    """
    mge_fit_sectors
    ===============

    Purpose
    -------

    Approximates the surface brightness of a galaxy with a Multi-Gaussian Expansion
    (MGE) model, using the robust and automated fitting method of
    `Cappellari (2002) <https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C>`_.

    The measurements are taken along sectors with a previous call to the
    procedure ``sectors_photometry`` in the ``MgeFit`` package .
    All measurements within this program are in the instrumental units of ``pixels``
    and ``counts``. This routine fits MGE models with constant position angle and
    common center.

    Calling Sequence
    ----------------

    .. code-block:: python

        from mgefit.mge_fit_sectors import mge_fit_sectors

        m = mge_fit_sectors(radius, angle, counts, eps,
                 bulge_disk=False, fignum=1, linear=False, negative=False,
                 ngauss=None, normpsf=1., outer_slope=4, plot=False, qbounds=None,
                 quiet=False, rbounds=None, scale=1., sigmapsf=0., sol=0)

        total_counts, sigma, q_obs = m.sol  # assign the solution to variables
        print(m.sol.T)  # Print a table of best-fitting MGE parameters

    Example programs are in the ``mgefit/examples`` directory.
    It can be found within the main ``MgeFit`` package installation folder
    inside `site-packages <https://stackoverflow.com/a/46071447>`_.

    A PDF manual ``readme_mge_fit_sectors.pdf`` is contained in the main
    installation directory ``mgefit`` of the package inside
    `site-packages <https://stackoverflow.com/a/46071447>`_.

    Input Parameters
    ----------------

    radius: array_like with shape (n,)
        Vector containing the radius of the surface brightness
        measurements, taken from the galaxy center. This is given
        in units of PIXELS (!) of the image. When fitting multiple images
        simultaneously this is in pixels units of the high-resolution image.
    angle: array_like with shape (n,)
        Vector containing the polar angle of the surface brightness
        measurements, measured from the galaxy major axis (in degrees).
    counts: array_like with shape (n,)
        Vector containing the surface brightness measurements in COUNTS/PIXEL (!) at
        the polar coordinates specified by the vectors ``radius`` and ``angle``.
        When fitting multiple images simultaneously this is in counts/pixels units
        of the high-resolution image.
    eps:
        Crude estimate for the galaxy characteristic ellipticity
        ``eps = 1 - b/a = 1 - q'``

    Optional Keywords
    -----------------

    bulge_disk:
        Set ``bulge_disk=True`` to perform a non-parametric bulge/disk
        decomposition using MGE. When ``bulge_disk=True`` the Gaussians
        are divided into two sets, each with a unique axial ratio. The two
        sets are meant to describe and model the contribution of bulge and
        disks in spiral or lenticular galaxies, or nuclear disk in ellipticals.

        When this keyword is set one should increase ``ngauss``.
        One should also either set ``qbounds=None`` or specify four
        elements in ``qbounds`` for the even/odd Gaussians.
    fignum:
        Optional number to assign to the plotting window.
    linear:
        Set this keyword to start with the fully linear algorithm
        and then optimize the fit with the nonlinear method
        [see Section 3.4 of `Cappellari (2002)`_ for details].
        Nowadays using this keyword introduces a small speed penalty but
        produces more robust fits and is always recommended.
    negative:
        Set this keyword to allow for negative Gaussians in the fit.
        Use this only if everything else didn't work or if there is clear
        evidence that negative Gaussians are actually needed.
        Negative Gaussians are needed e.g. when fitting a boxy bulge.
    ngauss:
        Maximum number of Gaussians allowed in the MGE fit.
        Typical values are in the range 10-20 when ``linear=False``
        (default: ``ngauss=12``) and ``20**2-40**2`` when ``linear=True``
        (default: ``ngauss=30**2=900``).
    normpsf: array_like with shape (p,)
        This is optional if only a scalar is given for ``sigmapsf``, otherwise it
        must contain the normalization of each MGE component of the PSF, whose
        sigma is given by ``sigmapsf``. The vector needs to have the same number of
        elements as ``sigmapsf`` and it must be normalized as ``normpsf.sum() = 1``
        (default: ``normpsf=1``).
    outer_slope:
        This scalar forces the surface brightness profile of
        the MGE model to decrease at least as fast as ``R**(-outer_slope)``
        at the largest measured radius (Default: ``outer_slope=2``).
    plot:
        Set ``plot=True`` to plot the best-fitting MGE profiles.
    qbounds:
        This can be either a two or a four elements vector.

        If ``qbounds`` has two elements, it gives the minimum and maximum
        axial ratio ``q`` allowed in the MGE fit.

        If ``qbounds`` has four elements ``[[qMin1, qMax1], [qMin2, qMax2]]``,
        then the first two elements give the limits on ``q`` for the even
        Gaussians, while the last two elements give the limits on ``q`` for the
        odd Gaussians. In this way ``qbounds`` can be used to perform disk/bulges
        decompositions in a way similar to the ``bulge_disk`` keyword.
    quiet:
        Set ``quiet = True`` to suppress printed output.
    rbounds:
        Two elements vector giving the minimum and maximum ``sigma``
        allowed in the MGE fit. This is in the same PIXELS units as ``radius``.
    scale:
        The pixel scale in arcsec/pixels. This is *only* used for the scale on
        the plots. It has no influence on the output. (default: 1)
    sigmapsf: array_like with shape (p,)
        Scalar giving the ``sigma`` of the PSF, or vector with the ``sigma`` of an
        MGE model for the circular PSF. This is in the same PIXELS units as ``radius``.
        When fitting multiple images simultaneously this is the PSF of the
        high-resolution image [see pg. 406 of `Cappellari (2002)`_ for details].
        (Default: no convolution)
    sol:
        If this keyword has at least 6 elements in input, the sigma
        and q_obs will be used as starting point for the optimization.
        This is useful for testing but is never needed otherwise.
        The format is described in the Output Parameters below.

    Output Parameters
    -----------------

    Stored as attributes of the ``MgeFit`` class:

    .sol: array_like with shape (3, ngauss)
        Array with the best-fitting MGE solution. If the PSF parameters are
        given in input, this model is deconvolved for the PSF and pixels
        effects:

        .sol[0]: array_like with shape (ngauss)
            ``total_counts`` of the Gaussian components;
        .sol[1]: array_like with shape (ngauss)
            ``sigma`` is the dispersion of the best-fitting Gaussians in pixels;
        .sol[2]: array_like with shape (ngauss)
            ``q_obs`` is the observed axial ratio of the best-fitting
            Gaussian components [q' in the notation of `Cappellari (2002)`_].

        The relation below gives the Gaussians peak surface brightness ``surf``::

            total_counts, q_obs, sigma = m.sol  # Assign MGE solution to variables
            surf = total_counts/(2*np.pi*q_obs*sigma**2)

    absdev:
        Mean absolute deviation between the fitted MGE and the
        data expressed as a fraction. Good fits to high S/N images
        can reach values of ``absdev < 0.02 = 2%``.

    ###########################################################################
    """
    def __init__(self, radius, angle, counts, eps,
                 bulge_disk=False, fignum=1, linear=False, negative=False,
                 ngauss=None, normpsf=1., outer_slope=4, plot=False, qbounds=None,
                 quiet=False, rbounds=None, scale=1., sigmapsf=0., sol=0):
        """
        This is the main routine. It is the only one that has to be called from outside.

        """
        # Starting from here the biggest part of this routine is devoted to input
        # checking and loading of shared parameters into a common block
        #
        assert np.all(counts > 0), 'Input counts must be positive'
        assert radius.size == angle.size == counts.size, 'Input vectors must have the same length'
        outer_slope = np.clip(outer_slope, 1, 4)

        # load data vectors into class attributes
        #
        self.radius = radius
        self.counts = counts
        self.angle = angle
        self.scale = scale
        sol = np.asarray(sol)
        self.sigmapsf = np.atleast_1d(sigmapsf)
        self.normpsf = np.atleast_1d(normpsf)
        self.negative = negative
        self.scale = scale
        self.quiet = quiet

        nPsf = self.sigmapsf.size
        if nPsf > 1:
            assert self.normpsf.size == nPsf, 'sigmapsf and normpsf must have the same length'
            assert round(np.sum(normpsf), 2) == 1, 'PSF not normalized'

        self.sectors = np.unique(angle) # Finds the different position angles

        # Open grid in the range [rminLog,rmaxLog]
        # The logarithmic slope of a Gaussian is slope(R) = -(R/sigma)**2
        # so to have a slope -n one needs to be at R = sqrt(n)*sigma.
        # Below we constrain the largest Gaussian to have sigma < rmax/sqrt(n)
        # to force the surface brightness of the MGE model to decrease
        # at least as fast as R**-n at the largest measured radius.
        #
        if rbounds is None:
            lrbounds = np.log10([np.min(radius), np.max(radius)/np.sqrt(outer_slope)])
        else:
            lrbounds = np.log10([rbounds[0], rbounds[1]/np.sqrt(outer_slope)])

        if qbounds is None:
            qbounds = np.array([0.05, 1.]) # no Gaussians flatter than q=0.05
        else:
            qbounds = np.asarray(qbounds)

        # If the smallest intrinsic Gaussian has sigma=0.75*sigmapsf it will produce an
        # observed Gaussian with sigmaObs=SQRT(sigma**2+sigmapsf**2)=1.25*sigmapsf.
        # We require the sigma of the Gaussians to be larger than 0.75*sigmapsf,
        # or the smallest measured radius, whichever is larger.
        #
        if np.sum(sigmapsf) > 0:
            lrbounds[0] = max(lrbounds[0], np.log10(0.75*np.min(sigmapsf)))

        # Here the actual calculation starts. The path is different depending on whether the
        # user has requested the nonlinear method or the linear one by setting the /LINEAR keyword
        #
        t = clock()
        if linear:
            assert not bulge_disk, 'BULGE_DISK not supported with LINEAR keyword'
            assert qbounds.size == 2, 'Multiple qbounds not supported with LINEAR keyword'
            if ngauss is None:
                ngauss = 100**2
            else:
                assert ngauss >= 10**2, 'Too few Gaussians for the LINEAR method'
            if not self.quiet:
                print('Starting the LINEAR fit with ',  ngauss, ' Gaussians. Please wait...')
            bestNorm = 1e30
            nIter = 0
        else:
            if ngauss is None:
                ngauss = 15
            else:
                assert ngauss < 35, 'Too many Gaussians for the non-linear method'
            if sol.size < 6:
                logsigma = linspace_open(*lrbounds, num=ngauss)  # open grid
                q = np.full_like(logsigma, 1 - eps)
            else:
                ngauss = sol.size//3
                logsigma = np.log10(sol[1, :]).clip(*lrbounds) # Log(sigma)
                q = sol[2, :]     # q_obs

            parinfo = [{'step':0.01, 'limits':lrbounds, 'limited':[1, 1], 'tied':''}
                        for j in range(2*ngauss)]

            if qbounds.size == 2:
                q = q.clip(*qbounds)
                for j in range(ngauss, 2*ngauss):
                    parinfo[j]['limits'] = qbounds
            elif qbounds.size == 4:  # Different bounds for bulge and disk
                q[::2] = q[::2].clip(*qbounds[0])
                q[1::2] = q[1::2].clip(*qbounds[1])
                for j in range(ngauss, 2*ngauss, 2):
                    parinfo[j]['limits'] = qbounds[0]
                    parinfo[j+1]['limits'] = qbounds[1]
            else:
                raise ValueError('qbounds must have 2 or 2x2=4 elements')

            if bulge_disk:
                for j in range(ngauss, 2*ngauss-2, 2):
                    parinfo[j+2]['tied'] = 'p['+str(ngauss)+']'   # Ties axial ratio of even Gaussians
                    parinfo[j+3]['tied'] = 'p['+str(ngauss+1)+']' # Ties axial ratio of odd Gaussians

            if quiet:
                iterfunc = None
            else:
                iterfunc = self._print

            pars = np.append(logsigma, q)
            mp = mpfit(self._fitfunc, pars, iterfunct=iterfunc,
                       nprint=10, parinfo=parinfo, quiet=quiet)
            sol = mp.params
            bestNorm = mp.fnorm
            nIter = mp.niter # Use iterations of the longer part

        if (not bulge_disk) and (qbounds.size == 2):
            sol, bestNorm = self._linear_fit(sol, bestNorm, lrbounds, qbounds, ngauss)

        # Print the results for the nonzero Gaussians sorted by increasing sigma
        logsigma, q = sol.reshape(2, -1)
        w = self.weights != 0
        m = w.sum()
        self.weights, self.gauss, logsigma, q = self.weights[w], self.gauss[:, w], logsigma[w], q[w]

        j = np.argsort(logsigma)
        self.sol = np.vstack([self.weights[j], 10**logsigma[j], q[j]])
        self.absdev = np.mean(np.abs(self.err))

        # Force Gaussians with minor axis smaller than the PSF, which have
        # a degenerate axial ratio, to have the same axial ratio as the mean
        # of the first two well determined Gaussians. Flux is conserved by
        # PSF convolution so no other changes are required
        #
        if (not bulge_disk) and (qbounds.size == 2):
            sigy = self.sol[1, :]*self.sol[2, :]
            w = sigy < np.min(sigmapsf)
            self.sol[2, w] = np.mean(self.sol[2, ~w][:2])

        if not self.quiet:
            print('############################################')
            print('  Computation time: %.2f seconds' % (clock() - t))
            print('  Total Iterations: ', nIter)
            print(' Nonzero Gaussians: ', m)
            print('  Unused Gaussians: ', ngauss - m)
            print(' Sectors used in the fit: ', self.sectors.size)
            print(' Total number of points fitted: ', radius.size)
            print(' Chi2: %.4g ' % bestNorm)
            print(' STDEV: %.4g ' % np.std(self.err))
            print(' MEANABSDEV: %.4g ' % self.absdev)
            print('############################################')
            print('  Total_Counts   sigma_Pixels     q_obs')
            print('############################################')
            for sol in self.sol.T:
                print(('{:13.4e}{:#13.4g}{:13.4f}').format(*sol))
            print('++++++++++++++++++++++++++++++++++++++++++++')

        if plot:
            self.plot(fignum)

#----------------------------------------------------------------------------

    def _fitfunc(self, pars, fjac=None):

        logsigma, q = pars.reshape(2, -1)

        r2 = (self.radius**2)[:, None, None]
        ang = np.radians(self.angle)[:, None, None]
        sigma2 = (10**(2*logsigma))[None, :, None]
        q2 = (q**2)[None, :, None]
        sigmapsf2 = (self.sigmapsf**2)[None, None, :]
        normpsf = self.normpsf[None, None, :]

        # Analytic convolution with an MGE circular PSF
        # Equations (4,5) in Cappellari (2002)
        sigmaX = np.sqrt(sigma2 + sigmapsf2)
        sigmaY = np.sqrt(sigma2*q2 + sigmapsf2)

        # Normalized (volume=1) 2-dim Gaussian in polar coordinates
        g = np.exp(-0.5*r2*((np.cos(ang)/sigmaX)**2 + (np.sin(ang)/sigmaY)**2))
        self.gauss = np.sum(normpsf/(2*np.pi*sigmaX*sigmaY)*g, 2)

        # Analytic integral of the MGE on the central pixel.
        # Below we assume the central pixel is aligned with the galaxy axes.
        # This is generally not the case, but the error due to this
        # approximation is negligible in realistic situations.
        w = self.radius < 0.5
        g = special.erf(2**-1.5/sigmaX) * special.erf(2**-1.5/sigmaY)
        self.gauss[w, :] = np.sum(normpsf*g, 2)

        A = self.gauss/self.counts[:, None] # gauss*SQRT(weights) = gauss/y
        b = np.ones_like(self.radius)  # y*SQRT(weights) = 1 <== weights = 1/sigma**2 = 1/y**2

        if self.negative:   # Solution by LAPACK linear least-squares
            self.weights = np.linalg.lstsq(A, b, rcond=None)[0]
        else:               # Solution by NNLS
            self.weights = lsq_box(A, b, bounds=(0, np.inf)).x

        self.yfit = self.gauss @ self.weights   # Evaluate predictions by matrix multiplications
        self.err = 1 - self.yfit / self.counts     # relative error: yfit, counts are positive quantities
        self.chi2 = self.err @ self.err  # rnorm**2 = TOTAL(err**2) (this value is only used with the /LINEAR keyword)

        return self.err.astype(np.float32)

#----------------------------------------------------------------------------

    def _linear_fit(self, sol, chi2Best, lrbounds, qbounds, ngauss):
        """
        This implements the algorithm described in Sec.3.4 of Cappellari (2002)

        """
        if sol.size < 6:
            neps = int(np.sqrt(ngauss))  # Adopt neps~nrad. This may not always be optimal
            nrad = ngauss // neps
            logsigma = np.linspace(*lrbounds, num=nrad)
            q = np.linspace(*qbounds, num=neps)
            sol = np.append(*np.meshgrid(logsigma, q))
            self.nIter = 0
            self._fitfunc(sol)                  # Get initial chi**2
            chi2Best = self.chi2
            self._print(0, sol, 0, chi2Best)    # print initial chi2

        ########
        # Starting from the best linear solution we iteratively perform the following steps:
        # 1) Eliminate the Gaussians = 0
        # 2) Eliminate all Gaussians whose elimination increase chi2 less than "factor"
        # 3) Perform nonlinear optimization of these Gaussians (chi2 can only decrese)
        # 4) if the number of Gaussians decreased go back to step (1)
        ########

        factor = 1.01  # Maximum accepted factor of increase in chi**2 from the best solution

        while True:
            sol = sol.reshape(2, -1)
            ngauss = sol.shape[1]
            sol = sol[:, self.weights != 0] # Extract the nonzero Gaussians
            m = sol.shape[1]
            if not self.quiet:
                print('Nonzero Gaussians: %d/%d' % (m, ngauss))
                print('Eliminating not useful Gaussians...')
            while True:
                chi2v = np.zeros(m)
                for k in range(m):
                    tmp = np.delete(sol, k, axis=1)  # Drop element k from the solution
                    self._fitfunc(tmp.ravel()) # Try the new solution
                    chi2v[k] = self.chi2

                k = np.argmin(chi2v)
                if chi2v[k] > factor*chi2Best:
                    break
                sol = np.delete(sol, k, axis=1)  # Delete element k from the solution
                m -= 1                           # Update the gaussian count
                if not self.quiet:
                    print(f'ngauss: {m}          chi2: {chi2v[k]:#.4g}')

            if m == ngauss:
                if not self.quiet:
                    print('All Gaussians are needed!')
                break
            ngauss = m

            parinfo = [{'step':0.01, 'limits':lrbounds, 'limited':[1, 1]}
                        for j in range(2*ngauss)]

            for j in range(ngauss, 2*ngauss):
                parinfo[j]['limits'] = qbounds

            if not self.quiet:
                print('Starting nonlinear fit...')

            mp = mpfit(self._fitfunc, sol.ravel(), iterfunct=self._print,
                       nprint=10, parinfo=parinfo, quiet=self.quiet)
            sol = mp.params

            if mp.fnorm < chi2Best:
                chi2Best = mp.fnorm

        # Load proper values in self.weights and chi2best before returning

        sol = sol.ravel()
        self._fitfunc(sol)
        chi2Best = self.chi2

        return [sol, chi2Best]

#----------------------------------------------------------------------------

    def _print(self, myfunct, logsigma, it, fnorm,
                functkw=None, args=None, parinfo=None, dof=None, quiet=0):
        """
        This is called every NPRINT iterations of MPFIT

        """
        print('Iteration:%d  chi2: %#.4g  Nonzero: %d/%d' %
              (it, fnorm, np.sum(self.weights != 0), self.weights.size))

#----------------------------------------------------------------------------

    def plot(self, fignum=1):
        """
        Produces final best-fitting plot

        """
        # Select an x and y plot range that is the same for all plots
        #
        minrad = np.min(self.radius)*self.scale
        maxrad = np.max(self.radius)*self.scale
        mincnt = np.min(self.counts)
        maxcnt = np.max(self.counts)
        xran = minrad * (maxrad/minrad)**np.array([-0.02, +1.02])
        yran = mincnt * (maxcnt/mincnt)**np.array([-0.05, +1.05])

        n = self.sectors.size
        dn = int(round(n/6.))
        nrows = (n-1)//dn + 1 # integer division

        fig, ax = plt.subplots(nrows, 2, sharex=True, sharey='col', num=fignum)
        fig.subplots_adjust(hspace=0.01)

        fig.text(0.04, 0.5, 'counts', va='center', rotation='vertical')
        fig.text(0.96, 0.5, 'error (%)', va='center', rotation='vertical')

        ax[-1, 0].set_xlabel("arcsec")
        ax[-1, 1].set_xlabel("arcsec")

        row = 0
        for j in range(0, n, dn):
            w = np.nonzero(self.angle == self.sectors[j])[0]
            w = w[np.argsort(self.radius[w])]
            r = self.radius[w]*self.scale
            txt = "$%.f\\degree$" % self.sectors[j]

            ax[row, 0].set_xlim(xran)
            ax[row, 0].set_ylim(yran)
            ax[row, 0].loglog(r, self.counts[w], 'C0o')
            ax[row, 0].loglog(r, self.yfit[w], 'C1', linewidth=2)
            ax[row, 0].text(0.98, 0.95, txt, ha='right', va='top', transform=ax[row, 0].transAxes)
            ax[row, 0].loglog(r, self.gauss[w, :]*self.weights[None, :])

            ax[row, 1].semilogx(r, self.err[w]*100, 'C0o')
            ax[row, 1].axhline(linestyle='--', color='C1', linewidth=2)
            ax[row, 1].yaxis.tick_right()
            ax[row, 1].yaxis.set_label_position("right")
            ax[row, 1].set_ylim([-19.5, 20])

            row += 1

#----------------------------------------------------------------------------
