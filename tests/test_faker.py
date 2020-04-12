from tests import create_rand


def test_faker():
    rand = create_rand()
    assert rand.gen('(:faker_hexify:)')
