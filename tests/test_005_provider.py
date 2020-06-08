import pytest
from tests import create_rand


def test_register_provider():
    from rand.providers.base import RandBaseProvider

    class TestProvider(RandBaseProvider):
        pass

    rnd = create_rand()
    provider = TestProvider(prefix="test_fn")
    # test register provider
    rnd.register_provider(provider)
    # test getting provider registry
    assert rnd.providers.get("test_fn") == provider

    with pytest.raises(Exception):

        class ErrorProvider(RandBaseProvider):
            def register(self):
                raise Exception("Test error")

        test_error = ErrorProvider(prefix="test_error")
        rnd.register_provider(test_error)


def test_base_provider():
    from rand.providers.base import RandBaseProvider

    class TestProvider(RandBaseProvider):
        def _parse_fn(self, pattern, opts=None):
            return "test"

        def parse(self, name: str, pattern: any, opts: dict):
            parsed_name = self.get_parse_name(name)
            print("parsed", parsed_name)
            if parsed_name:
                return self._parse_fn(pattern, opts)
            return None

        def _map_fn(self, pattern, opts=None):
            return "test2"

        def map(self, name: str, pattern: any, opts: dict):
            mapped_name = self.get_map_name(name)
            print("mapped", mapped_name)
            if mapped_name:
                return self._map_fn(pattern, opts)
            return None

        def _filter_fn(self, pattern, opts=None):
            return True

        def filter(self, name: str, pattern: any, opts: dict):
            filtered_name = self.get_filter_name(name)
            print("filterped", filtered_name)
            if filtered_name:
                return self._filter_fn(pattern, opts)
            return None

    rnd = create_rand()
    rnd.register_provider(TestProvider(prefix="test_fn"))
    # test parse
    assert rnd.gen("(:test_fn:)") == ["test"]
    # test map
    assert rnd.gen("(:test_fn:)", args=[{"maps": [{"name": "test_fn"}]}]) == ["test2"]
    assert rnd.gen("(:test_fn:)", maps=[{"name": "test_fn"}]) == ["test2"]
    assert rnd.gen(
        "(:test_fn:)",
        args=[{"maps": [{"name": "test_fn"}]}],
        maps=[{"name": "test_fn"}],
    ) == ["test2"]
    # test filter
    assert rnd.gen("(:test_fn:)", args=[{"filters": [{"name": "test_fn"}]}]) == ["test"]
    assert rnd.gen("(:test_fn:)", filters=[{"name": "test_fn"}]) == ["test"]
    assert rnd.gen(
        "(:test_fn:)",
        args=[{"filters": [{"name": "test_fn"}]}],
        filters=[{"name": "test_fn"}],
    ) == ["test"]


def test_proxy_provider():
    from rand.providers.base import RandProxyBaseProvider

    class TestProxy:
        def target(self, arg1="def1", arg2="def2", *args, **kwargs):
            return "%s-%s" % (arg1, arg2)

        def test2_map(self):
            return "test2"

        def test2_map2(self):
            return "test22"

        def test3_filter(self):
            return True

        def test3_filter2(self):
            return False

    rnd = create_rand()
    test_proxy = RandProxyBaseProvider(prefix="test", target=TestProxy())
    rnd.register_provider(test_proxy)
    assert rnd.gen("(:test_target:)") == ["def1-def2"]
    assert rnd.gen("(:test_target:)", ["ok1"]) == ["ok1-def2"]
    assert rnd.gen("(:test_target:)", ["ok1", "ok2"]) == ["ok1-def2"]
    assert rnd.gen("(:test_target:)", [["ok1", "ok2"]]) == ["ok1-ok2"]
    assert rnd.gen("(:test_target:)", [["ok1", "ok2"], "ok3"]) == ["ok1-ok2"]
    assert rnd.gen("(:test_target:)", [{"arg1": "ok1"}]) == ["ok1-def2"]
    assert rnd.gen("(:test_target:)", [{"arg1": "ok1", "arg2": "ok2"}]) == ["ok1-ok2"]
    assert rnd.gen(
        "(:test_target:arg_name:)", {"arg_name": {"arg1": "ok1", "arg2": "ok2"}}
    ) == ["ok1-ok2"]
    assert rnd.gen(
        "(:test_target:)", [{"arg1": "ok1", "arg2": "ok2", "arg3": "ok3"}]
    ) == ["ok1-ok2"]

    with pytest.raises(Exception):

        class ErrorProxy:
            def __init__(self):
                raise Exception("Test error")

        test_proxy = RandProxyBaseProvider(prefix="test_error", target=ErrorProxy())
        rnd.register_provider(test_proxy)

    # test proxy map
    assert rnd.gen("(:test_target:)", maps=[{"name": "test_test2_map"}]) == ["test2"]
    assert rnd.gen(
        "(:test_target:)",
        args=[{"maps": [{"name": "test_test2_map"}]}],
        maps=[{"name": "test_test2_map2"}],
    ) == ["test22"]
    # test proxy filter
    assert rnd.gen("(:test_target:)", filters=[{"name": "test_test3_filter"}]) == [
        "def1-def2"
    ]
    assert rnd.gen(
        "(:test_target:)",
        args=[{"filters": [{"name": "test_test3_filter"}]}],
        filters=[{"name": "test_test3_filter2"}],
    ) == ["def1-def2"]
