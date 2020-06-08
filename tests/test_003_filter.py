import pytest
from tests import create_rand


def test_register_filter():
    def test1(pattern, opts):
        return "test1"

    def test_filter(pattern: any, opts: dict):
        arg1 = opts["args"].get("arg1", "")
        return True if arg1 != "_test" else False

    rnd = create_rand()
    rnd.register_parse("test1", test1)
    # test register filter
    rnd.register_filter("test_filter", test_filter)
    # test get registry
    assert rnd.filters.get("_filter_test_filter", None) is not None
    # test filter for subpattern
    assert rnd.gen("(:test1:)", args=[{"filters": [{"name": "test_filter"}]}]) == [
        "test1"
    ]
    # test filter for subpattern with args
    assert rnd.gen(
        "(:test1:)", args=[{"filters": [{"name": "test_filter", "arg1": "_test"}]}]
    ) == [""]
    # test filter globally
    assert rnd.gen("(abc)", filters=[{"name": "test_filter"}]) == ["abc"]
    # test filter globally with args
    assert rnd.gen("(abc)", filters=[{"name": "test_filter", "arg1": "_test"}]) == []
    # test register with wrong name
    with pytest.raises(Exception):
        assert rnd.register_filter("test_with_wrong_name[]", test1)
