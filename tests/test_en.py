from tests import create_rand


def test_en():
    rand = create_rand()
    assert rand.gen('(:en_vocal:)') == ['i']
    assert rand.gen('(:en_consonant:)') == ['l']
