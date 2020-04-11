from tests import create_rand


def test_faker():
    from rand.providers.contribs.faker import RandFakerProvider
    rand = create_rand()
    rand.register_provider(RandFakerProvider(rand=rand, prefix='faker'))
    print(rand.gen('(:faker_hexify:)'))
