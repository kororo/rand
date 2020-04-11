from rand.providers.en import ENProvider
from tests import create_rand


def test_en():
    rand = create_rand()
    rand.register_provider(ENProvider(rand=rand, prefix='en'))
    print(rand.gen('(:en_vocal:)'))
