
**CapFit: linearly-constrained non-linear least-squares optimization**

.. image:: http://www-astro.physics.ox.ac.uk/~cappellari/software/capfit_logo.svg
    :target: https://pypi.org/project/capfit/
    :width: 100
.. image:: https://img.shields.io/pypi/v/capfit.svg
    :target: https://pypi.org/project/capfit/
.. image:: https://img.shields.io/badge/arXiv-2208.14974-orange.svg
    :target: https://arxiv.org/abs/2208.14974
.. image:: https://img.shields.io/badge/DOI-10.1093/mnras/stad2597-green.svg
    :target: https://doi.org/10.1093/mnras/stad2597

This ``CapFit`` package contains a Python implementation of the
linearly-constrained non-linear least-squares optimization method described in
Section 3.2 of `Cappellari (2023) <https://ui.adsabs.harvard.edu/abs/2023MNRAS.526.3273C>`_.

.. contents:: :depth: 1

Attribution
-----------

If you use this software for your research, please cite `Cappellari (2023)`_,
where the algorithm was described in Sec. 3.2. The BibTeX entry for the paper is::

    @ARTICLE{Cappellari2023,
        author = {{Cappellari}, M.},
        title = "{Full spectrum fitting with photometry in PPXF: stellar population
            versus dynamical masses, non-parametric star formation history and
            metallicity for 3200 LEGA-C galaxies at redshift $z\approx0.8$}",
        journal = {MNRAS},
        eprint = {2208.14974},
        year = 2023,
        volume = 526,
        pages = {3273-3300},
        doi = {10.1093/mnras/stad2597}
    }

Installation
------------

install with::

    pip install capfit

Without write access to the global ``site-packages`` directory, use::

    pip install --user capfit

To upgrade ``CapFit`` to the latest version use::

    pip install --upgrade capfit

Usage Examples
--------------

To learn how to use the ``CapFit`` package, see the ``capfit_examples.py`` file
within the ``capfit/examples`` directory. It can be found within the main
``capfit`` package installation folder inside 
`site-packages <https://stackoverflow.com/a/46071447>`_. 
The detailed documentation is contained in the docstring of the file
``capfit.py``, or on `PyPi <https://pypi.org/project/capfit/>`_.

###########################################################################
