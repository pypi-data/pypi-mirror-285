import pytest
from geometry.figures import Circle, Triangle, Figure
from geometry.exceptions import FigureError
from unittest.mock import patch


class TestFigure:
    @pytest.mark.parametrize(
        ("is_error", "arg"),
        (
            (False, "1"),
            (False, True),
            (False, 0),
            (False, False),
            (True, "a"),
            (True, sum),
        ),
    )
    @patch.multiple(Figure, __abstractmethods__=set())
    def test__to_digit(self, is_error, arg):
        if is_error:
            with pytest.raises(FigureError):
                Figure()._to_digit(arg)
        else:
            Figure()._to_digit(arg)


class TestCircle:
    @pytest.mark.parametrize(
        ("radius", "is_error"),
        (
            (1, False),
            (999.99, False),
            (0, True),
            (-123, True),
        ),
    )
    def test_validate(self, radius, is_error):
        if is_error:
            with pytest.raises(FigureError):
                Circle(radius=radius)
        else:
            Circle(radius=radius)


class TestTriangle:
    @pytest.mark.parametrize(
        ("is_error", "sides"),
        (
            (False, (1, 1, 1)),
            (False, (3, 4, 5)),
            (True, (1, 2, 3)),
        ),
    )
    def test_validate(self, is_error, sides):
        if is_error:
            with pytest.raises(FigureError):
                Triangle(*sides)
        else:
            Triangle(*sides)
