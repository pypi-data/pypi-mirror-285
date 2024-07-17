from math import acos, asin, atan, cos, pi, sin, tan

from sympy import zoo

from gym_cas import Cos, Sin, Tan, aCos, aSin, aTan


def test_sin():
    assert Sin(90) == 1.0
    assert abs(Sin(135) - sin(135 * pi / 180)) < 0.01
    assert Sin(180) == 0.0
    assert abs(Sin(45) - sin(45 * pi / 180)) < 0.01
    assert Sin(0) == 0.0


def test_cos():
    assert Cos(90) == 0.0
    assert abs(Cos(135) - cos(135 * pi / 180)) < 0.01
    assert Cos(180) == -1.0
    assert abs(Cos(45) - cos(45 * pi / 180)) < 0.01
    assert Cos(0) == 1.0


def test_tan():
    assert Tan(45) == 1.0
    assert abs(Tan(60) - tan(60 * pi / 180)) < 0.01
    assert Tan(90) == zoo
    assert abs(Tan(30) - tan(30 * pi / 180)) < 0.01
    assert Tan(0) == 0.0


def test_asin():
    assert aSin(1) == 90.0
    assert abs(aSin(0.5) - asin(0.5) * 180 / pi) < 0.01
    assert aSin(0) == 0.0
    assert abs(aSin(0.75) - asin(0.75) * 180 / pi) < 0.01
    assert aSin(-1) == -90.0


def test_acos():
    assert aCos(1) == 0.0
    assert abs(aCos(0.5) - acos(0.5) * 180 / pi) < 0.01
    assert aCos(0) == 90.0
    assert abs(aCos(0.75) - acos(0.75) * 180 / pi) < 0.01
    assert aCos(-1) == 180.0


def test_atan():
    assert aTan(1) == 45.0
    assert abs(aTan(0.5) - atan(0.5) * 180 / pi) < 0.01
    assert aTan(0) == 0.0
    assert abs(aTan(0.75) - atan(0.75) * 180 / pi) < 0.01
    assert aTan(-1) == -45.0
