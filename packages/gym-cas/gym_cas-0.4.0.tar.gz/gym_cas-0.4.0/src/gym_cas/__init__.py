# SPDX-FileCopyrightText: 2023-present JACS <jacs@zbc.dk>
#
# SPDX-License-Identifier: MIT

from math import pi

from numpy import mean, median, std, var
from spb import plot, plot3d_implicit, plot3d_list, plot_geometry, plot_implicit, plot_list
from sympy import (
    Function,
    Matrix,
    N,
    Piecewise,
    Symbol,
    acos,
    asin,
    atan,
    cos,
    diff,
    dsolve,
    exp,
    expand,
    factor,
    integrate,
    limit,
    ln,
    log,
    nsolve,
    sin,
    solve,
    sqrt,
    symbols,
    tan,
)

from .config import _configure_spb
from .logarithm import log10
from .ode import plot_ode
from .plot_helpers import plot_points
from .regression import regression_exp, regression_poly, regression_power
from .stat_plot import boxplot, plot_bars, plot_hist, plot_sum
from .stats import (
    degroup,
    frekvenstabel,
    group,
    group_mean,
    group_percentile,
    group_std,
    group_var,
    kvartiler,
    percentile,
)
from .trigonometry import Cos, Sin, Tan, aCos, aSin, aTan
from .vector import plot3d_line, plot3d_plane, plot_vector, vector

a, b, c, d, e, f, g, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = symbols(
    "a b c d e f g i j k l m n o p q r s t u v w x y z", real=True
)

_configure_spb()
