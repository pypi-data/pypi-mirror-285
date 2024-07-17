from collections.abc import Iterable
from typing import Union

from spb.graphics import graphics, list_2d


def plot_points(x: Iterable, y: Iterable, label="", rendering_kw: Union[dict, None] = None, **kwargs):
    """Afbild punkter i et koordinatsystem

        `plot_points(x,y)`

    - Afbild punkter med angivelse af label og rendering_kw

        `plot_points(x,y,label,rendering_kw)`

    Parametre
    ---------
    x : Iterable
        Punkternes x-værdier

    y : Iterable
        Punkternes y-værdier

    label : String
        Label for alle punkter

    rendering_kw : se `list_2d`
    kwargs : se `list_2d`

    Returnerer
    ---------
    plt : Plot
        Plotobjektet.

    Se også
    ---------
    - [SPB: list_2d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_2d.html#spb.graphics.functions_2d.list_2d)
    """
    kwargs.setdefault("is_point", True)
    if rendering_kw is None:
        rendering_kw = {}
    if isinstance(label, (tuple, list)):
        label = label[0]
    return graphics(list_2d(x, y, label, rendering_kw, **kwargs), **kwargs)


if __name__ == "__main__":
    # p = plot_points([1, 2], [0, 10], label="as", show=False)
    # p2 = plot_points([2, 3], [0, 10], label="as2", show=False)
    # (p + p2).show()

    # p = plot_points([1, 2, 3, 3], [1, 3, 5, 7])

    # plot_points([-4, 0], [-2, 5], "", {"marker": "*"})

    plot_points([-4, 0], [-2, 5], "hej", {"marker": "*"}, aspect="equal")
