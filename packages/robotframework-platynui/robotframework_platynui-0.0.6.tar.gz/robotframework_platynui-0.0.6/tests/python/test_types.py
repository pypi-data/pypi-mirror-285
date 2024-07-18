from PlatynUI.core.types import Point, Rect


def test_contains_when_point_inside_rect() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=5, y=5)
    assert rect.contains(point) is True


def test_contains_when_point_outside_rect() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=15, y=15)
    assert rect.contains(point) is False


def test_contains_when_point_on_left_edge() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=0, y=5)
    assert rect.contains(point) is True


def test_contains_when_point_on_right_edge() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=9, y=5)
    assert rect.contains(point) is True


def test_contains_when_point_on_top_edge() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=5, y=0)
    assert rect.contains(point) is True


def test_contains_when_point_on_bottom_edge() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=5, y=9)
    assert rect.contains(point) is True


def test_contains_when_point_on_top_left_corner() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=0, y=0)
    assert rect.contains(point) is True


def test_contains_when_point_on_top_right_corner() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=9, y=0)
    assert rect.contains(point) is True


def test_contains_when_point_on_bottom_left_corner() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=0, y=9)
    assert rect.contains(point) is True


def test_contains_when_point_on_bottom_right_corner() -> None:
    rect = Rect(left=0, top=0, width=10, height=10)
    point = Point(x=9, y=9)
    assert rect.contains(point) is True
