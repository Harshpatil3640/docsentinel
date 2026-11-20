import random

from docsentinel.gstin import checksum_char, is_valid_gstin, make_gstin


def test_known_valid_gstin():
    assert is_valid_gstin("27AAPFU0939F1ZV")


def test_wrong_checksum_is_invalid():
    assert not is_valid_gstin("27AAPFU0939F1ZX")


def test_wrong_shape_is_invalid():
    assert not is_valid_gstin("27AAPFU0939F1Z")  # 14 characters
    assert not is_valid_gstin("27aapfu0939f1zv")  # lower case
    assert not is_valid_gstin("")


def test_checksum_char_matches_known_example():
    assert checksum_char("27AAPFU0939F1Z") == "V"


def test_make_gstin_always_valid():
    rng = random.Random(1)
    for _ in range(500):
        assert is_valid_gstin(make_gstin("29", rng))
