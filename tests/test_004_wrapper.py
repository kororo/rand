import pytest
from tests import create_rand


def test_register_parse_wrapper():
    rnd = create_rand()

    @rnd.register_parse_wrapper(name="test1")
    def parse_test1(pattern, opts=None):
        return "test1"

    # test parser
    print(rnd.gen("(:test1:)"))


def test_register_map_wrapper():
    rnd = create_rand()

    @rnd.register_parse_wrapper(name="test1")
    def parse_test1(pattern, opts=None):
        return "test1"

    @rnd.register_map_wrapper(name="test2")
    def parse_test2(pattern, opts=None):
        return "test2"

    # test parser
    print(rnd.gen("(:test1:)", args=[{"maps": [{"name": "test2"}]}]))
    print(rnd.gen("(:test1:)", maps=[{"name": "test2"}]))


def test_register_filter_wrapper():
    rnd = create_rand()

    @rnd.register_parse_wrapper(name="test1")
    def parse_test1(pattern, opts=None):
        return "test1"

    @rnd.register_filter_wrapper(name="test2")
    def parse_test2(pattern, opts=None):
        return "test2"

    # test parser
    print(rnd.gen("(:test1:)", args=[{"filters": [{"name": "test2"}]}]))
    print(rnd.gen("(:test1:)", filters=[{"name": "test2"}]))
