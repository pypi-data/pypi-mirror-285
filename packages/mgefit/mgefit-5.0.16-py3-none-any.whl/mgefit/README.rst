The MgeFit Package
==================

**MgeFit: Multi-Gaussian Expansion Fitting of Galactic Images**

.. image:: https://img.shields.io/pypi/v/mgefit.svg
        :target: https://pypi.org/project/mgefit/
.. image:: https://img.shields.io/badge/arXiv-astroph:0201430-orange.svg
        :target: https://arxiv.org/abs/astro-ph/0201430
.. image:: https://img.shields.io/badge/DOI-10.1046/...-green.svg
        :target: https://doi.org/10.1046/j.1365-8711.2002.05412.x

MgeFit is a Python implementation of the robust and efficient Multi-Gaussian
Expansion (MGE) fitting algorithm for galactic images of `Cappellari (2002)
<https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C>`_.

The MGE parameterization is useful in the construction of realistic dynamical 
models of galaxies (see `JAM modelling <https://pypi.org/project/jampy/>`_), 
for PSF deconvolution of images, for the correction and estimation of dust 
absorption effects, or for galaxy photometry.

.. contents:: :depth: 2

Attribution
-----------

If you use this software for your research, please cite
`Cappellari (2002) <https://ui.adsabs.harvard.edu/abs/2002MNRAS.333..400C>`_.
The BibTeX entry for the paper is::

    @Article{Cappellari2002,
        author = {{Cappellari}, M.},
        title = {Efficient multi-Gaussian expansion of galaxies},
        journal = {MNRAS},
        eprint = {arXiv:astro-ph/0201430}
        year = {2002},
        volume = {333},
        pages = {400-410},
        doi = {10.1046/j.1365-8711.2002.05412.x}
    }


Installation
------------

install with::

    pip install mgefit

Without writing access to the global ``site-packages`` directory, use::

    pip install --user mgefit
    
To upgrade MgeFit to the latest version use::

    pip install --upgrade mgefit    

Usage Examples
--------------

To learn how to use the ``MgeFit`` package, copy, modify and run 
the example programs in the ``mgefit/examples`` directory. 
It can be found within the main ``MgeFit`` package installation folder 
inside `site-packages <https://stackoverflow.com/a/46071447>`_. 
The detailed documentation is contained in the docstring of each file, 
or for the main procedure on `PyPi <https://pypi.org/project/mgefit/>`_.

###########################################################################
