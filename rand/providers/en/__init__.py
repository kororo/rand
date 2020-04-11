import typing
from rand.providers.base import RandProxyBaseProvider

if typing.TYPE_CHECKING:
    from rand import Rand


class ENTarget:
    def __init__(self, rand: 'Rand'):
        self._rand = rand

    def vocal(self):
        vocals = 'aiueo'
        return self._rand.random.choice(list(vocals) + list(vocals.upper()))

    def consonant(self):
        consonants = 'bcdfghjklmnpqrstvwxyz'
        return self._rand.random.choice(list(consonants) + list(consonants.upper()))


class ENProvider(RandProxyBaseProvider):
    def __init__(self, rand: 'Rand', prefix: str, target=None):
        target = target if target else ENTarget(rand=rand)
        super(ENProvider, self).__init__(rand=rand, prefix=prefix, target=target)
