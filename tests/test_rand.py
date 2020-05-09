import pytest


def create_rand():
    from rand import Rand
    rnd = Rand(seed=28)
    return rnd


def test_simple():
    rnd = create_rand()
    assert rnd.gen('ro') == ['ro']


def test_literal():
    rnd = create_rand()
    assert rnd.gen('') == ['']
    assert rnd.gen('koro') == ['koro']
    assert rnd.gen('28') == ['28']
    assert rnd.gen('a-z') == ['a-z']
    assert rnd.gen('(a-z)') == ['a-z']
    assert rnd.gen('\\141') == ['a']
    assert rnd.gen('\0') == ['\x00']


def test_any():
    rnd = create_rand()
    assert rnd.gen('.') == ['e']


def test_branch():
    rnd = create_rand()
    assert rnd.gen('ko|ro') == ['ko']
    assert rnd.gen('ko|ro|ro') == ['ro']


def test_in():
    rnd = create_rand()
    assert rnd.gen('[kororo]') == ['k']
    assert rnd.gen('k[o]r[o]r[o]') == ['kororo']


def test_max_repeat():
    rnd = create_rand()
    assert rnd.gen('r{2,8}') == ['rr']
    with pytest.raises(ValueError):
        assert rnd.gen('r{2,}') == ['rr']
    assert rnd.gen('r{,8}') == ['rr']
    assert rnd.gen('(roro){2,8}') == ['rorororororororororororo']
    with pytest.raises(ValueError):
        assert rnd.gen('r+') == ['rr']
    assert rnd.gen('r?') == ['']


def test_range():
    rnd = create_rand()
    assert rnd.gen('[a-z]') == ['d']
    assert rnd.gen('[0-9]') == ['8']
    assert rnd.gen('[a-z][0-9]') == ['h7']
    # (IN, [(LITERAL, 97), (RANGE, (97, 122)), (LITERAL, 122)])
    # basically (a|a-z|z)
    assert rnd.gen('[aa-zz]') == ['a']


def test_supattern():
    rnd = create_rand()
    assert rnd.gen('(ro)') == ['ro']
    assert rnd.gen('(ko|ro|ro)') == ['ko']
    assert rnd.gen('(?P<ro>ro)') == ['ro']


def test_complex():
    rnd = create_rand()
    assert rnd.gen('(ko|ro|ro){2,8}') == ['roko']


def test_ignored():
    rnd = create_rand()
    # (AT, AT_BEGINNING), (LITERAL, 114), (LITERAL, 111)
    assert rnd.gen('^ro') == ['ro']
    # (LITERAL, 114), (LITERAL, 111), (AT, AT_END)
    assert rnd.gen('ro$') == ['ro']


def test_exception():
    rnd = create_rand()
    with pytest.raises(Exception):
        assert rnd.gen('[[') == ['[[']


def test_register_parse():
    def test1(pattern, opts):
        return 'test1'

    rnd = create_rand()
    assert rnd.gen('(:test_not_exist:)') == ['']
    rnd.register_parse('test1', test1)
    assert rnd.gen('(:test1:)') == ['test1']
    with pytest.raises(Exception):
        assert rnd.register_parse('test_with_wrong_name[]', test1)


def test_base_provider():
    from rand.providers.base import RandBaseProvider

    class TestProvider(RandBaseProvider):
        def _parse_fn(self, pattern, opts=None):
            return 'test'

        def parse(self, name: str, pattern: any, opts: dict):
            # name always start with _parse_[PREFIX], normalise first
            parsed_name = self.get_parse_name(name)
            if parsed_name:
                return self._parse_fn(pattern, opts)
            return None

    rnd = create_rand()
    rnd.register_provider(TestProvider(prefix='test_fn'))
    assert rnd.gen('(:test_fn:)') == ['test']


def test_proxy_provider():
    from rand.providers.base import RandProxyBaseProvider

    class TestProxy:
        def target(self, arg1='def1', arg2='def2'):
            return '%s-%s' % (arg1, arg2)

    rnd = create_rand()
    test_proxy = RandProxyBaseProvider(prefix='test', target=TestProxy())
    rnd.register_provider(test_proxy)
    assert rnd.gen('(:test_target:)') == ['def1-def2']
    assert rnd.gen('(:test_target:)', ['ok1']) == ['ok1-def2']
    assert rnd.gen('(:test_target:)', ['ok1', 'ok2']) == ['ok1-def2']
    assert rnd.gen('(:test_target:)', [['ok1', 'ok2']]) == ['ok1-ok2']
    assert rnd.gen('(:test_target:)', [['ok1', 'ok2'], 'ok3']) == ['ok1-ok2']
    assert rnd.gen('(:test_target:)', [{'arg1': 'ok1'}]) == ['ok1-def2']
    assert rnd.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2'}]) == ['ok1-ok2']
    assert rnd.gen('(:test_target:arg_name:)', {'arg_name': {'arg1': 'ok1', 'arg2': 'ok2'}}) == ['ok1-ok2']
    with pytest.raises(Exception):
        assert rnd.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2', 'arg3': 'ok3'}]) == ['ok1-ok2']

    with pytest.raises(Exception):
        class ErrorProxy:
            def __init__(self):
                raise Exception('Test error')
        test_proxy = RandProxyBaseProvider(prefix='test_error', target=ErrorProxy())
        rnd.register_provider(test_proxy)


def test_register_wrapper():
    rnd = create_rand()

    @rnd.register_parse_wrapper(name='test1')
    def parse_test1(pattern, opts=None):
        return 'test1'

    @rnd.register_provider_fn_wrapper(prefix='test2')
    def parse_test2(pattern, opts=None):
        return 'test2'

    print(rnd.gen('(:test1:)'))
    print(rnd.gen('(:test2:)'))
