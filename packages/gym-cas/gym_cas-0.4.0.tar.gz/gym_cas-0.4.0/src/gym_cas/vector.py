from warnings import filterwarnings

from numpy import array
from spb import plot3d_parametric_line, plot3d_parametric_surface
from spb.defaults import THREE_D_B  # type: ignore
from spb.graphics import arrow_2d, graphics
from spb.plot_functions.functions_2d import _create_generic_data_series, _set_labels
from spb.series import BaseSeries, Vector3DSeries
from spb.utils import _check_arguments, _plot_sympify
from sympy import Matrix, N

# Filter xlim, ylim, and zlim warnings for 3D quiver
filterwarnings("ignore", module="spb", lineno=514)
filterwarnings("ignore", module="spb", lineno=521)
filterwarnings("ignore", module="spb", lineno=535)

# Based on
# https://sympy-plot-backends.readthedocs.io/en/latest/tutorials/tut-6.html
# https://github.com/Chrillebon/DTUMathTools/blob/main/src/dtumathtools/dtuplot/quiverplot.py
# https://github.com/Davide-sd/sympy-plot-backends/blob/master/spb/series.py#L2857
# https://github.com/Davide-sd/sympy-plot-backends/blob/master/spb/backends/matplotlib/renderers/vector2d.py


class Arrow3DSeries(BaseSeries):
    normalize = False
    is_3Dvector = True  # noqa: N815
    is_streamlines = False
    is_slice = False
    _allowed_keys = ()

    def __init__(self, start, direction, label="", **kwargs):
        """
        start: Start position of vector or list of vectors
        direction: Direction of vector or list of vectors
        label: Label to be shown for the series

        **kwargs : Keyword arguments to be passed on
        """
        super().__init__(**kwargs)
        self._set_use_quiver_solid_color(**kwargs)

        if hasattr(start[0], "__iter__"):
            self.start = start
            self.direction = direction
        else:
            self.start = [start]
            self.direction = [direction]

        if label != "":
            self.rendering_kw.setdefault("label", label)

    def _set_use_quiver_solid_color(self, **kwargs):
        self.use_quiver_solid_color = (
            True
            if ("scalar" not in kwargs.keys())
            else (False if (not kwargs["scalar"]) or (kwargs["scalar"] is None) else True)
        )

    def get_data(self):
        return array(
            [[x[i] for x in self.start] for i in range(3)] + [[x[i] for x in self.direction] for i in range(3)]
        )

    def __str__(self):
        if len(self.start) == 1:
            return f"3D Vector: s{self.start[0]} v{self.direction[0]}"

        s = "3D Vectors: "
        for i in range(len(self.start)):
            s += f"{i}: s{self.start[i]} v{self.direction[i]} "
        return s


THREE_D_B.renderers_map.update({Arrow3DSeries: THREE_D_B.renderers_map[Vector3DSeries]})


def check_dims(v, s=None):
    if hasattr(v[0], "__iter__") or isinstance(v[0], Matrix):
        d = len(v[0])
        if d not in (2, 3):
            err = "First vector was neither 2D or 3D"
            raise TypeError(err)
        for vv in v:
            if len(vv) != d:
                err = "A vector didn't match the dimensions of the first vector"
                raise TypeError(err)
            if s is not None:
                for ss in s:
                    if len(ss) != d:
                        err = "A starting point didn't match the dimensions of the vectors."
                        raise TypeError(err)
        return d, True

    d = len(v)
    if d not in (2, 3):
        err = "The vector must be either 2D or 3D."
        raise TypeError(err)
    if s not in {None, d}:
        err = "Starting point and vector must both be either 2D or 3D."
        raise TypeError(err)
    return d, False


def calc_limits(v, s):
    kw = ["xlim", "ylim", "zlim"]
    result = {}

    if not hasattr(v[0], "__iter__"):
        v = [v]
        s = [s]

    for d in range(len(v[0])):
        d_min = v[0][d] + s[0][d] if v[0][d] + s[0][d] < s[0][d] else s[0][d]
        d_max = v[0][d] + s[0][d] if v[0][d] + s[0][d] > s[0][d] else s[0][d]
        for i in range(len(v)):
            if v[i][d] + s[i][d] > s[i][d]:
                nextmax = v[i][d] + s[i][d]
                nextmin = s[i][d]
            else:
                nextmin = v[i][d] + s[i][d]
                nextmax = s[i][d]
            if nextmin < d_min:
                d_min = nextmin
            if nextmax > d_max:
                d_max = nextmax
        extra = (d_max - d_min) / 10
        result[kw[d]] = (d_min - extra, d_max + extra)
    return result


def plot_vector(*args, **kwargs):
    """Plot 2D or 3D vectors or list of vectors. Typical usage examples:

    - Plotting a vector with (0,0) as starting point:

        `plot_vector(v, **kwargs)`

    - Plotting multiple vectors with custom starting points:

        `plot_vector([s1,s2], [v1,v2], **kwargs)`

    Parameters
    ==========

    args :
        s : Vector, or Matrix/list/tuple of vector each with 2 or 3 elements.
            Represents the starting point(s) of the vector(s) to be plotted.

        v : Vector, or Matrix/list/tuple of vector each with 2 or 3 elements.
            Represents the vector(s) to be plotted.

    label : str, optional
        The name of the vector(s) to be shown on the label.

    quiver_kw : dict
        A dictionary of keywords/values which is passed to the backend quivers-
        plotting function to customize the appearance. Refer to the plotting
        library (backend) manual for more informations.

    rendering_kw : list of dicts, optional
        A list of dictionaries of keywords/values which is passed to the
        backend's functions to customize the appearance.

    show : boolean
        The default value is set to `True`. Set show to `False` and
        the function will not display the plot. The returned instance of
        the `Plot` class can then be used to save or display the plot
        by calling the `save()` and `show()` methods respectively.

    size : (float, float), optional
        A tuple in the form (width, height) to specify the size of
        the overall figure. The default value is set to `None`, meaning
        the size will be set by the backend.

    title : str, optional
        Title of the plot. It is set to the latex representation of
        the expression, if the plot has only one expression.

    xlabel, ylabel, zlabel : str, optional
        Labels for the x-axis, y-axis, z-axis, respectively.
        ``zlabel`` is only available for 3D plots.

    xlim, ylim, zlim : (float, float), optional
        Denotes the axis limits, `(min, max)`, visible in the chart.
        ``zlim`` is only available for 3D plots
    """
    if len(args) == 1:
        v = args[0]
        dim, lst = check_dims(v)

        if lst:
            for i in range(len(v)):
                if isinstance(v[i], Matrix):
                    v[i] = [float(N(x)) for x in v[i]]
            s = [[0] * dim] * len(v)
        else:
            if type(v) == Matrix:
                v = [float(N(x)) for x in v]
            s = [0] * dim

    elif len(args) == 2:  # noqa: PLR2004
        s = args[0]
        v = args[1]
        dim, lst = check_dims(v, s)
        if lst:
            for i in range(len(v)):
                if isinstance(v[i], Matrix):
                    v[i] = [float(N(x)) for x in v[i]]
            for i in range(len(s)):
                if isinstance(s[i], Matrix):
                    s[i] = [float(N(x)) for x in s[i]]
        if type(v) == Matrix:
            v = [float(N(x)) for x in v]
        if type(s) == Matrix:
            s = [float(N(x)) for x in s]

    else:
        err = f"plot_vector() expects 1 or 2 arguments ({len(args)} were given)"
        raise TypeError(err)

    limits = calc_limits(v, s)
    for lim in limits:
        kwargs.setdefault(lim, limits[lim])

    show = kwargs.get("show", True)
    kwargs.setdefault("aspect", "equal")
    kwargs.setdefault("xlabel", "x")
    kwargs.setdefault("ylabel", "y")
    if kwargs.get("label", False):
        kwargs.setdefault("legend", True)
    else:
        kwargs.setdefault("legend", False)

    if dim == 2:  # noqa: PLR2004
        global_labels = kwargs.pop("label", [])
        global_rendering_kw = kwargs.pop("rendering_kw", None)
        arrows = []
        if hasattr(s[0], "__iter__"):
            for start, vec in zip(s, v):
                arrows.extend(arrow_2d(start, vec, **kwargs))
        else:
            arrows.extend(arrow_2d(s, v, **kwargs))
        _set_labels(arrows, global_labels, global_rendering_kw)
        gs = _create_generic_data_series(**kwargs)
        return graphics(*arrows, gs, **kwargs)

        # backend = kwargs.get("backend", TWO_D_B)
        # p = backend(Arrow2DSeries(s, v, **kwargs), **kwargs)
    elif dim == 3:  # noqa : PLR2004
        kwargs.setdefault("zlabel", "z")
        backend = kwargs.get("backend", THREE_D_B)
        p = backend(Arrow3DSeries(s, v, **kwargs), **kwargs)
    else:
        err = "Mixing 2D vectors with 3D vectors is not allowed."
        raise ValueError(err)

    if show:
        p.show()
    return p


def plot3d_line(*args, **kw_args):
    """Afbild en eller flere parameterfremstillinger for linjer i et rumligt koordinatsystem.

    - Afbild en linje.

        `plot3d_line(line, range, **kwargs)`

    - Afbild flere linjer med samme interval.

        `plot3d_line(line_1, line_2, ..., range, **kwargs)`

    - Afbild flere linjer med forskellige intervaller.

        `plot3d_line((line_1, range1), (line_2, range2), ..., **kwargs)`

    - Afbild flere linjer med forskellige intervaller og labels.

        `plot3d_line((line_1, range1, label1), (line_2, range2, label2), ..., **kwargs)`

    Parametre
    ---------
    line : 3D iterables or matrices
        Parameterfremstillingen for en linje.

    range : tuple
        Intervallet for den frie parameter. Angives som tuple: (t, t_min, t_max).

    Label : str
        Tekst til at identificere linjen.

    kwargs : se `line_parametric_3d`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: line_parametric_3d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.line_parametric_3d)
    """
    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 1)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] is None:
            if plot_expr[i][2] is None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_line(*plot_expr, **kw_args)


def plot3d_plane(*args, **kw_args):
    """Afbild en eller flere parameterfremstillinger for planer i et rumligt koordinatsystem.

    - Afbild en plan.

        `plot3d_plane(plane, range_s, range_t, **kwargs)`

    - Afbild flere planer med samme intervaller.

        `plot3d_plane(plane_1, plane_2, range_s, range_t, **kwargs)`

    - Afbild flere planer med forskellige intervaller.

        `plot3d_plane((plane_1, range_s1, range_t1), (plane_2, range_s2, range_t2), **kwargs)`

    - Afbild flere planer med forskellige intervaller og labels.

        `plot3d_plane((plane_1, range_s1, range_t1, label1), (plane_2, range_s2, range_t2, label2), **kwargs)`

    Parametre
    ---------
    plane : 3D iterables or matrices
        Parameterfremstillingen for en plan.

    range_s : tuple
        Intervallet for den første frie parameter. Angives som tuple: (s, s_min, s_max).

    range_t : tuple
        Intervallet for den anden frie parameter. Angives som tuple: (t, t_min, t_max).

    Label : str
        Tekst til at identificere planen.

    kwargs : se `surface_parametric`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: surface_parametric](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.surface_parametric)
    """
    kw_args.setdefault("use_cm", False)

    args = _plot_sympify(args)
    plot_expr = _check_arguments(args, 1, 2)
    for i in range(len(plot_expr)):
        if plot_expr[i][3] is None:
            if plot_expr[i][2] is None:
                plot_expr[i] = (plot_expr[i][0][0], plot_expr[i][0][1], plot_expr[i][0][2], plot_expr[i][1])
            else:
                plot_expr[i] = (
                    plot_expr[i][0][0],
                    plot_expr[i][0][1],
                    plot_expr[i][0][2],
                    plot_expr[i][1],
                    plot_expr[i][2],
                )
        else:
            plot_expr[i] = (
                plot_expr[i][0][0],
                plot_expr[i][0][1],
                plot_expr[i][0][2],
                plot_expr[i][1],
                plot_expr[i][2],
                plot_expr[i][3],
            )
    return plot3d_parametric_surface(*plot_expr, **kw_args)


def vector(*args):
    """Hjælpefunktion til at danne en SymPy matrix til at repræsentere en vektor.

    - 2D vektor

        `vector(x,y)`

    - 3D vektor

        `vector(x,y,z)`

    Bemærk at Vector klassen i SymPy behandler vektorer anderledes og ikke benyttes.

    Parametre
    ---------
    args: Vektorkoordinater

    Returnerer
    ---------
    m : Matrix
        Plotobjektet.

    Se også
    ---------
    - [SymPy: Matrix](https://docs.sympy.org/latest/modules/matrices/matrices.html)
    """
    return Matrix([*args])


if __name__ == "__main__":
    # a = plot_vector((0, 0), (5, 5), show=False, label="test")
    # b = plot_vector([4, 4], show=False)
    # c = plot_vector([(2, 3), (1, 1)], label="(2,3) og (1,1)", show=False)
    # plot_vector([(0, 0), (1, 1)],[(2, 3), (1, 1)])
    # (a + b + c).show()
    # print(a)
    # print(c)

    # d = plot_vector([5, 5, 5], label="hej", show=False)
    # e = plot_vector([1, 1, 1], Matrix([1, 2, 3]), label="matrix", show=False)
    # f = plot_vector([Matrix([0, 1, 1]), Matrix([1, 1, 0])], label="matrix", show=False)
    # (d + e + f).show()

    # print(d)

    from sympy.abc import s, t

    a = Matrix([1, 2, 3])
    b = Matrix([1, 1, 1])
    line = a + t * b
    # plot3d_line(line,(t,0,10))
    # plot3d_line( line, b+t*a, (t,0,10))
    # plot3d_line((line,(t,0,20)),(b+t*a, (t,0,10)))
    # plot3d_line((line, (t, 0, 20), "hej"), (b + t * a, (t, 0, 10), "hej2"))

    c = Matrix([0, 0, 1])
    plane = a + t * b + s * c
    # plot3d_plane(plane, (t, 0, 10), (s, -10, 0))

    # plot3d_plane( plane , (t, 0, 10), (s, -10, 0))
    # plot3d_plane(plane, t*a + b + s * c, (t, 0, 10), (s, -10, 0))
    # plot3d_plane((plane,(t, 0, 10), (s, -10, 0)), (t*a + b + s * c, (t, 0, 10), (s, -10, 20)))
    plot3d_plane((plane, (t, 0, 10), (s, -10, 0), "p1"), (t * a + b + s * c, (t, 0, 10), (s, -10, 20), "p2"))

    print(vector(3, 4))
