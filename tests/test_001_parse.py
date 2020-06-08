import pytest
from tests import create_rand


def test_simple():
    rnd = create_rand()
    assert rnd.gen("ro") == ["ro"]


def test_literal():
    rnd = create_rand()
    assert rnd.gen("") == [""]
    assert rnd.gen("koro") == ["koro"]
    assert rnd.gen("28") == ["28"]
    assert rnd.gen("a-z") == ["a-z"]
    assert rnd.gen("(a-z)") == ["a-z"]
    assert rnd.gen("\\141") == ["a"]
    assert rnd.gen("\0") == ["\x00"]


def test_any():
    rnd = create_rand()
    assert rnd.gen(".") == ["e"]


def test_branch():
    rnd = create_rand()
    assert rnd.gen("ko|ro") == ["ko"]
    assert rnd.gen("ko|ro|ro") == ["ro"]


def test_in():
    rnd = create_rand()
    assert rnd.gen("[kororo]") == ["k"]
    assert rnd.gen("k[o]r[o]r[o]") == ["kororo"]


def test_max_repeat():
    rnd = create_rand()
    assert rnd.gen("r{2,8}") == ["rr"]
    with pytest.raises(ValueError):
        assert rnd.gen("r{2,}") == ["rr"]
    assert rnd.gen("r{,8}") == ["rr"]
    assert rnd.gen("(roro){2,8}") == ["rorororororororororororo"]
    with pytest.raises(ValueError):
        assert rnd.gen("r+") == ["rr"]
    assert rnd.gen("r?") == [""]


def test_range():
    rnd = create_rand()
    assert rnd.gen("[a-z]") == ["d"]
    assert rnd.gen("[0-9]") == ["8"]
    assert rnd.gen("[a-z][0-9]") == ["h7"]
    # (IN, [(LITERAL, 97), (RANGE, (97, 122)), (LITERAL, 122)])
    # basically (a|a-z|z)
    assert rnd.gen("[aa-zz]") == ["a"]


def test_supattern():
    rnd = create_rand()
    assert rnd.gen("(ro)") == ["ro"]
    assert rnd.gen("(ko|ro|ro)") == ["ko"]
    assert rnd.gen("(?P<ro>ro)") == ["ro"]


def test_complex():
    rnd = create_rand()
    assert rnd.gen("(ko|ro|ro){2,8}") == ["roko"]


def test_ignored():
    rnd = create_rand()
    # (AT, AT_BEGINNING), (LITERAL, 114), (LITERAL, 111)
    assert rnd.gen("^ro") == ["ro"]
    # (LITERAL, 114), (LITERAL, 111), (AT, AT_END)
    assert rnd.gen("ro$") == ["ro"]


def test_exception():
    rnd = create_rand()
    with pytest.raises(Exception):
        assert rnd.gen("[[") == ["[["]


def test_register_parse():
    def test1(pattern, opts):
        return "test1"

    rnd = create_rand()
    # test not exist
    assert rnd.gen("(:test_not_exist:)") == [""]
    rnd.register_parse("test1", test1)
    # test registry
    assert rnd.parsers.get("_parse_test1", None) is not None
    # test execute parse
    assert rnd.gen("(:test1:)") == ["test1"]
    # test register with wrong name
    with pytest.raises(Exception):
        assert rnd.register_parse("test_with_wrong_name[]", test1)
