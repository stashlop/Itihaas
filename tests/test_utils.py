"""Pure helper functions."""
import pytest

from itihaas.auth import _safe_next_url
from itihaas.utils import allowed_image, is_valid_email, parse_float, parse_int


@pytest.mark.parametrize("value, expected", [("5", 5), ("x", None), (None, None), ("0", None), ("11", None)])
def test_parse_int_range(value, expected):
    assert parse_int(value, minimum=1, maximum=10) == expected


def test_parse_float_rejects_nan():
    assert parse_float("nan") is None
    assert parse_float("2.5", minimum=0) == 2.5


@pytest.mark.parametrize("target, expected", [
    ("/shop", "/shop"), ("https://evil.example", None), ("//evil.example", None), ("javascript:alert(1)", None), (None, None),
])
def test_safe_next_url(target, expected):
    assert _safe_next_url(target) == expected


def test_allowed_image():
    assert allowed_image("a.PNG") and allowed_image("b.webp")
    assert not allowed_image("c.svg") and not allowed_image("noext") and not allowed_image(None)


def test_is_valid_email():
    assert is_valid_email("a@b.co")
    assert not is_valid_email("a@b") and not is_valid_email("") and not is_valid_email("a b@c.de")
