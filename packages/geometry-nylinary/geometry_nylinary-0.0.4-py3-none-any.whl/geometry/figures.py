from abc import ABC, abstractproperty, abstractmethod
from math import pi, sqrt
from geometry.exceptions import FigureError


class Figure(ABC):
    def __init__(self) -> None:
        self.validate()

    @abstractmethod
    def validate(self) -> None:
        ...

    @abstractproperty
    def area(self) -> float:
        ...

    @abstractproperty
    def perimeter(self) -> float:
        ...

    def _check_digit(self, arg_name: str, *args):
        for arg in args:
            try:
                float(arg)
            except (ValueError, TypeError):
                raise FigureError(f"{arg_name.capitalize()}={arg} must be a number")


class Circle(Figure):
    def __init__(self, radius: float) -> None:
        self.radius = radius
        super().__init__()

    def validate(self) -> None:
        self._check_digit("radius", self.radius)
        if self.radius <= 0:
            raise FigureError("Radius must be greater that zero")

    @property
    def area(self) -> float:
        return pi * self.radius**2

    @property
    def perimeter(self) -> float:
        return pi * self.radius * 2


class Triangle(Figure):
    def __init__(self, a: float, b: float, c: float) -> None:
        self.a = a
        self.b = b
        self.c = c
        super().__init__()

    def validate(self) -> None:
        self._check_digit("side", self.a, self.b, self.c)
        if not all((self.a + self.b > self.c, self.a + self.c > self.b, self.b + self.c > self.a)):
            raise FigureError("Not valid triangle")

    @property
    def area(self) -> float:
        p = self.perimeter / 2
        return sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))

    @property
    def perimeter(self) -> float:
        return self.a + self.b + self.c

    @property
    def is_equilateral(self) -> bool:
        return self.a == self.b == self.c

    @property
    def is_right(self) -> bool:
        sides = sorted([self.a, self.b, self.c])
        return sides.pop() ** 2 == sides.pop() ** 2 + sides.pop() ** 2
