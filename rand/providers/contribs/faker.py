from rand.providers.base import RandProxyBaseProvider


class RandFakerProvider(RandProxyBaseProvider):
    def __init__(self, prefix: str = 'faker', target=None):
        from faker import Faker
        target = target if target else Faker()
        super(RandFakerProvider, self).__init__(prefix=prefix, target=target)

    def register(self):
        for name in ['hexify', 'numerify']:
            self.rand.register_parse('%s_%s' % (self._prefix, name), self.proxy_parse())
