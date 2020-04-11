import typing
from faker import Faker
from rand.providers.base import RandProxyBaseProvider

if typing.TYPE_CHECKING:
    from rand import Rand


class RandFakerProvider(RandProxyBaseProvider):
    def __init__(self, rand: 'Rand', prefix: str, target=None):
        target = target if target else Faker()
        super(RandFakerProvider, self).__init__(rand=rand, prefix=prefix, target=target)

    def register(self):
        for name in ['hexify', 'numerify']:
            self.rand.register_parse('%s_%s' % (self._prefix, name), self.proxy_parse())
