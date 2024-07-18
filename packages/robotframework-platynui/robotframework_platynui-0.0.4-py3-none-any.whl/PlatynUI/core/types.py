from typing import Any, Callable, Iterator, Optional

__all__ = ["Point", "VirtualPoint", "Rect", "Size"]


class Point:
    def __init__(self, x: Optional[float] = None, y: Optional[float] = None) -> None:
        self._x = x
        self._y = y

    @property
    def is_valid(self) -> bool:
        return self._x is not None and self._y is not None

    @property
    def x(self) -> float:
        if self._x is None:
            raise ValueError("x is not set")

        return self._x

    @x.setter
    def x(self, v: float) -> None:
        self._x = v

    def x_is_valid(self) -> bool:
        return self._x is not None

    def y_is_valid(self) -> bool:
        return self._y is not None

    @property
    def y(self) -> float:
        if self._y is None:
            raise ValueError("y is not set")

        return self._y

    @y.setter
    def y(self, v: float) -> None:
        self._y = v

    def __iter__(self) -> Iterator[Optional[float]]:
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return "Point(x=%s, y=%s)" % (self.x, self.y)

    def clone(self) -> "Point":
        return Point(self.x, self.y)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y

        return False

    def __bool__(self) -> bool:
        return self.is_valid

    def __add__(self, other: Any) -> "Point":
        if isinstance(other, Point):
            return Point(
                self.x + other.x if self.x is not None and other.x is not None else None,
                self.y + other.y if self.y is not None and other.y is not None else None,
            )

        raise NotImplementedError


class VirtualPoint(Point):
    def __init__(self, name: Any, func: Callable[["Rect"], Point]):
        super().__init__()
        self.name = name
        self.func = func

    @property
    def is_valid(self) -> bool:
        return False

    def calc_rect(self, r: Optional["Rect"]) -> Point:
        if r is None:
            return Point()

        return self.func(r)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, VirtualPoint):
            return bool(self.name == other.name)

        raise NotImplementedError

    def __repr__(self) -> str:
        return "VirtualPoint(%s)" % repr(self.name)


class Size:
    def __init__(self, width: Optional[float] = None, height: Optional[float] = None):
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        if self._width is None:
            raise ValueError("width is not set")

        return self._width

    @width.setter
    def width(self, v: float) -> None:
        self._width = v

    @property
    def height(self) -> float:
        if self._height is None:
            raise ValueError("height is not set")
        return self._height

    @height.setter
    def height(self, v: float) -> None:
        self._height = v

    @property
    def is_valid(self) -> bool:
        return self.width is not None and self.height is not None

    def __iter__(self) -> Iterator[Optional[float]]:
        yield self.width
        yield self.height

    def __repr__(self) -> str:
        return "Size(width=%s, height=%s)" % (self.width, self.height)

    def clone(self) -> "Size":
        return Size(self.width, self.height)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Size):
            return self.width == other.width and self.height == other.height

        return False

    def __bool__(self) -> bool:
        return self.is_valid


class Rect:
    def __init__(
        self,
        left: Optional[float] = None,
        top: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ):
        self._left = left
        self._top = top
        self._width = width
        self._height = height

    @property
    def x1(self) -> float:
        return self.left

    @property
    def y1(self) -> float:
        return self.top

    @property
    def x2(self) -> float:
        return self.left + self.width - 1

    @property
    def y2(self) -> float:
        return self.top + self.height - 1

    @property
    def is_valid(self) -> bool:
        return (
            self._left is not None
            and self._top is not None
            and self._width is not None
            and self._height is not None
            and self.x1 <= self.x2
            and self.y1 <= self.y2
        )

    @property
    def is_null(self) -> bool:
        return self.x2 == self.x1 - 1 and self.y2 == self.y1 - 1

    @property
    def is_empty(self) -> bool:
        return self.x1 > self.x2 or self.y1 > self.y2

    @property
    def left(self) -> float:
        if self._left is None:
            raise ValueError("left is not set")
        return self._left

    @left.setter
    def left(self, v: float) -> None:
        self._left = v

    @property
    def top(self) -> float:
        if self._top is None:
            raise ValueError("top is not set")

        return self._top

    @top.setter
    def top(self, v: float) -> None:
        self._top = v

    @property
    def width(self) -> float:
        if self._width is None:
            raise ValueError("width is not set")

        return self._width

    @width.setter
    def width(self, v: float) -> None:
        self._width = v

    @property
    def height(self) -> float:
        if self._height is None:
            raise ValueError("height is not set")

        return self._height

    @height.setter
    def height(self, v: float) -> None:
        self._height = v

    @property
    def right(self) -> float:
        return self.left + self.width - 1

    @property
    def bottom(self) -> float:
        return self.top + self.height - 1

    @property
    def top_left(self) -> Point:
        if not self:
            return Point()
        return Point(self.left, self.top)

    @property
    def top_right(self) -> Point:
        if not self:
            return Point()
        return Point(self.right, self.top)

    @property
    def bottom_right(self) -> Point:
        if not self:
            return Point()
        return Point(self.right, self.bottom)

    @property
    def bottom_left(self) -> Point:
        if not self:
            return Point()
        return Point(self.left, self.bottom)

    @property
    def center(self) -> Point:
        if not self:
            return Point()
        return Point(self.left + self.width / 2, self.top + self.height / 2)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def __iter__(self) -> Iterator[float]:
        yield self.left
        yield self.top
        yield self.width
        yield self.height

    def __repr__(self) -> str:
        return "Rect(left=%s, top=%s, width=%s, height=%s)" % (self.left, self.top, self.width, self.height)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Rect):
            o = other
            return self.left == o.left and self.top == o.top and self.width == o.width and self.height == o.height

        return False

    def __bool__(self) -> bool:
        return self.is_valid

    def contains(
        self, p: Optional[Point] = None, x: Optional[float] = None, y: Optional[float] = None, proper: bool = False
    ) -> bool:
        if not self:
            return False

        if p is None:
            p = Point()

        if x is not None:
            p.x = x
        if y is not None:
            p.y = y

        if not p:
            return False

        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2

        if x2 < x1 - 1:
            l = x2
            r = x1
        else:
            l = x1
            r = x2

        if proper:
            if p.x <= l or p.x >= r:
                return False
        else:
            if p.x < l or p.x > r:
                return False

        if y2 < y1 - 1:
            t = y2
            b = y1
        else:
            t = y1
            b = y2

        if proper:
            if p.y <= t or p.y >= b:
                return False
        else:
            if p.y < t or p.y > b:
                return False

        return True

    def __contains__(self, p: Point) -> bool:
        return self.contains(p)

    def intersected(self, r: "Rect") -> "Rect":
        if not self or not r:
            return Rect()

        l1 = self.x1
        r1 = self.x1
        if self.x2 - self.x1 + 1 < 0:
            l1 = self.x2
        else:
            r1 = self.x2

        l2 = r.x1
        r2 = r.x1
        if r.x2 - r.x1 + 1 < 0:
            l2 = r.x2
        else:
            r2 = r.x2

        if l1 > r2 or l2 > r1:
            return Rect()

        t1 = self.y1
        b1 = self.y1
        if self.y2 - self.y1 + 1 < 0:
            t1 = self.y2
        else:
            b1 = self.y2

        t2 = r.y1
        b2 = r.y1
        if r.y2 - r.y1 + 1 < 0:
            t2 = r.y2
        else:
            b2 = r.y2

        if t1 > b2 or t2 > b1:
            return Rect()

        x1 = max(l1, l2)
        x2 = min(r1, r2)
        y1 = max(t1, t2)
        y2 = min(b1, b2)

        return Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1)

    def inflated(self, dx: float, dy: float) -> "Rect":
        if not self:
            return Rect()

        return Rect(self.left - dx, self.top - dy, self.width + dx, self.height + dy)

    def deflated(self, dx: float, dy: float) -> "Rect":
        if not self:
            return Rect()

        return Rect(self.left + dx, self.top + dy, self.width - dx, self.height - dy)

    TOP_LEFT = VirtualPoint("top_left", lambda r: r.top_left)
    TOP_RIGHT = VirtualPoint("top_left", lambda r: Point(r.right, r.top))
    TOP = VirtualPoint("top", lambda r: Point(None, r.top))
    VMIDDLE = VirtualPoint("bottom", lambda r: Point(None, r.top + r.height // 2))
    HMIDDLE = VirtualPoint("right", lambda r: Point(r.left + r.width // 2, None))
    BOTTOM = VirtualPoint("bottom", lambda r: Point(None, r.top + r.height - 1))
    LEFT = VirtualPoint("left", lambda r: Point(r.left, None))
    RIGHT = VirtualPoint("right", lambda r: Point(r.left + r.width - 1, None))
    CENTER = VirtualPoint("center", lambda r: r.center)
    BOTTOM_RIGHT = VirtualPoint("bottom_right", lambda r: r.bottom_right)
