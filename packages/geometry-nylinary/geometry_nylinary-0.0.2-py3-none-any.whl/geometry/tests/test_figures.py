import pytest
from geometry.fugures import Circle, Triangle, Figure
from geometry.exceptions import FigureError
from unittest.mock import patch


class TestFigure:
    @pytest.mark.parametrize(
        ("is_error", "args"),
        (
            (False, ("1",),),
            (False, ("1", 2, True,),),
            (False, (0,-1, False,),),
            (True, (3, "a", "1",),),
            (True, (sum, 12,),),
        )
    )
    @patch.multiple(Figure, __abstractmethods__=set())
    def test__check_digit(self, is_error, args):
        if is_error:
            with pytest.raises(FigureError):
                Figure()._check_digit("name", *args)
        else:
            Figure()._check_digit("name", *args)


class TestCircle:
    @pytest.mark.parametrize(
        ("radius", "is_error"),
        (
            (1, False), 
            (999.99, False), 
            (0, True), 
            (-123, True),
        )
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
            (False, (1,1,1)),
            (False, (3,4,5)),
            (True, (1,2,3)),
        )
    )
    def test_validate(self, is_error, sides):
        if is_error:
            with pytest.raises(FigureError):
                Triangle(*sides)
        else:
            Triangle(*sides)