from spb import MB
from spb.series import List2DSeries

from gym_cas import plot_points


def test_plot_points():
    p = plot_points([1, 2, 3, 3], [1, 3, 5, 7], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [1, 2, 3, 3]).all()
    assert (s[0].get_data()[1] == [1, 3, 5, 7]).all()

    plot_points([-4, 0], [-2, 5], rendering_kw={"marker": "*"}, show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [1, 2, 3, 3]).all()
    assert (s[0].get_data()[1] == [1, 3, 5, 7]).all()

    plot_points([-4, 0], [-2, 5], rendering_kw={"marker": "*"}, aspect="equal", show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [1, 2, 3, 3]).all()
    assert (s[0].get_data()[1] == [1, 3, 5, 7]).all()
