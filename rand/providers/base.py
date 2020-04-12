import typing

if typing.TYPE_CHECKING:  # pragma: no cover
    from rand import Rand


class BaseRandAdapter:
    _rand: typing.Optional['Rand']

    def __init__(self, rand: 'Rand' = None):
        self._rand = rand

    @property
    def rand(self):
        return self._rand

    @rand.setter
    def rand(self, rand):
        self._rand = rand


class RandBaseProvider(BaseRandAdapter):
    def __init__(self, prefix: str = ''):
        super(RandBaseProvider, self).__init__()
        self._prefix = prefix

    def register(self):  # pragma: no cover
        pass


class RandProxyBaseProvider(RandBaseProvider):
    def __init__(self, prefix: str = '', target=None):
        super(RandProxyBaseProvider, self).__init__(prefix=prefix)
        self._target = target

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    def proxy_parse(self):
        def parse(ri, pattern, opts):
            token, args = opts['token'], opts['args']
            name = token.replace('%s_' % self._prefix, '')
            fn = getattr(self._target, name)
            if fn:
                if isinstance(args, list):
                    return fn(*args)
                elif isinstance(args, dict):
                    return fn(**args)
                else:
                    return fn()
            return ''

        return parse

    def register(self):
        names = [name for name in dir(self._target)
                 if callable(getattr(self._target, name))
                 if not name.startswith('_')
                 ]
        for name in names:
            self.rand.register_parse('%s_%s' % (self._prefix, name), self.proxy_parse())
