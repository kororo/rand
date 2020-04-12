import pytest


def create_rand():
    from rand import Rand
    rand = Rand(seed=28)
    return rand


def test_simple():
    rand = create_rand()
    assert rand.gen('ro') == ['ro']


def test_literal():
    rand = create_rand()
    assert rand.gen('') == ['']
    assert rand.gen('koro') == ['koro']
    assert rand.gen('28') == ['28']
    assert rand.gen('a-z') == ['a-z']
    assert rand.gen('(a-z)') == ['a-z']
    assert rand.gen('\\141') == ['a']
    assert rand.gen('\0') == ['\x00']


def test_any():
    rand = create_rand()
    assert rand.gen('.') == ['e']


def test_branch():
    rand = create_rand()
    assert rand.gen('ko|ro') == ['ko']
    assert rand.gen('ko|ro|ro') == ['ro']


def test_in():
    rand = create_rand()
    assert rand.gen('[kororo]') == ['k']
    assert rand.gen('k[o]r[o]r[o]') == ['kororo']


def test_max_repeat():
    rand = create_rand()
    assert rand.gen('r{2,8}') == ['rr']
    with pytest.raises(ValueError):
        assert rand.gen('r{2,}') == ['rr']
    assert rand.gen('r{,8}') == ['rr']
    assert rand.gen('(roro){2,8}') == ['rorororororororororororo']
    with pytest.raises(ValueError):
        assert rand.gen('r+') == ['rr']
    assert rand.gen('r?') == ['']


def test_range():
    rand = create_rand()
    assert rand.gen('[a-z]') == ['d']
    assert rand.gen('[0-9]') == ['8']
    assert rand.gen('[a-z][0-9]') == ['h7']
    # (IN, [(LITERAL, 97), (RANGE, (97, 122)), (LITERAL, 122)])
    # basically (a|a-z|z)
    assert rand.gen('[aa-zz]') == ['a']


def test_supattern():
    rand = create_rand()
    assert rand.gen('(ro)') == ['ro']
    assert rand.gen('(ko|ro|ro)') == ['ko']
    assert rand.gen('(?P<ro>ro)') == ['ro']


def test_complex():
    rand = create_rand()
    assert rand.gen('(ko|ro|ro){2,8}') == ['roko']


def test_ignored():
    rand = create_rand()
    # (AT, AT_BEGINNING), (LITERAL, 114), (LITERAL, 111)
    assert rand.gen('^ro') == ['ro']
    # (LITERAL, 114), (LITERAL, 111), (AT, AT_END)
    assert rand.gen('ro$') == ['ro']


def test_exception():
    rand = create_rand()
    with pytest.raises(Exception):
        assert rand.gen('[[') == ['[[']


def test_register_parse():
    def test1(ri, pattern, opts):
        return 'test1'

    rand = create_rand()
    assert rand.gen('(:test_not_exist:)') == ['']
    rand.register_parse('test1', test1)
    assert rand.gen('(:test1:)') == ['test1']
    with pytest.raises(Exception):
        assert rand.register_parse('test_with_wrong_name[]', test1)


def test_proxy_provider():
    from rand.providers.base import RandProxyBaseProvider

    class TestProxy:
        def target(self, arg1='def1', arg2='def2'):
            return '%s-%s' % (arg1, arg2)

    rand = create_rand()
    test_proxy = RandProxyBaseProvider(prefix='test', target=TestProxy())
    rand.register_provider(test_proxy)
    rand.register_parse('test_target', test_proxy.proxy_parse())
    assert rand.gen('(:test_target:)') == ['def1-def2']
    assert rand.gen('(:test_target:)', ['ok1']) == ['ok1-def2']
    assert rand.gen('(:test_target:)', ['ok1', 'ok2']) == ['ok1-def2']
    assert rand.gen('(:test_target:)', [['ok1', 'ok2']]) == ['ok1-ok2']
    assert rand.gen('(:test_target:)', [['ok1', 'ok2'], 'ok3']) == ['ok1-ok2']
    assert rand.gen('(:test_target:)', [{'arg1': 'ok1'}]) == ['ok1-def2']
    assert rand.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2'}]) == ['ok1-ok2']
    assert rand.gen('(:test_target:arg_name:)', {'arg_name': {'arg1': 'ok1', 'arg2': 'ok2'}}) == ['ok1-ok2']
    with pytest.raises(Exception):
        assert rand.gen('(:test_target:)', [{'arg1': 'ok1', 'arg2': 'ok2', 'arg3': 'ok3'}]) == ['ok1-ok2']
