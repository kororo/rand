import pytest
from tests import create_rand


def test_register_map():
    def test1(pattern, opts):
        return "test1"

    def test_map(pattern: any, opts: dict):
        arg1 = opts["args"].get("arg1", "")
        return "map_%s%s" % (pattern, arg1,)

    rnd = create_rand()
    rnd.register_parse("test1", test1)
    # test register map
    rnd.register_map("test_map", test_map)
    # test get registry
    assert rnd.maps.get("_map_test_map", None) is not None
    # test map for subpattern
    assert rnd.gen("(:test1:)", args=[{"maps": [{"name": "test_map"}]}]) == [
        "map_test1"
    ]
    # test map for subpattern with args
    assert rnd.gen(
        "(:test1:)", args=[{"maps": [{"name": "test_map", "arg1": "_test"}]}]
    ) == ["map_test1_test"]
    # test map globally
    assert rnd.gen("(abc)", maps=[{"name": "test_map"}]) == ["map_abc"]
    # test map globally with args
    assert rnd.gen("(abc)", maps=[{"name": "test_map", "arg1": "_test"}]) == [
        "map_abc_test"
    ]
    # test register with wrong name
    with pytest.raises(Exception):
        assert rnd.register_map("test_with_wrong_name[]", test1)
