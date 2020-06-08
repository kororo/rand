import inspect
import re
import sre_parse
import string
import typing
import importlib
import pkgutil
import logging
import warnings
from sre_parse import SubPattern
from sre_constants import LITERAL, MAXREPEAT
from random import Random

warnings.simplefilter(action="ignore", category=FutureWarning)
logger = logging.getLogger("rand")

# support . notation
ANY_NONE = string.printable

# support MAX_REPEAT_MAXREPEAT
MAX_REPEAT_MAXREPEAT = None

# type alias for parser fn definition
# def _parse_noop(self, pattern, opts=None):
#     return ''
ParseFnType = typing.Callable[[typing.Any, typing.Optional[typing.Any]], typing.Any]
MapFnType = typing.Callable[[typing.Any, typing.Optional[typing.Any]], typing.Any]
FilterFnType = typing.Callable[[typing.Any, typing.Optional[typing.Any]], typing.Any]


class Rand:
    _random: Random
    _providers: dict
    _parsers: dict
    _maps: dict
    _filters: dict
    _opts: dict
    _args: dict

    def __init__(self, seed=None, opts: dict = None):
        self._random = Random()
        self._providers = {}
        self._parsers = {}
        self._maps = {}
        self._filters = {}
        self._opts = opts if opts else {}
        self._args = {}
        if seed:
            self.random_seed(seed)
        # import built-in providers
        import rand.providers

        self.discover_providers(rand.providers)

    @property
    def random(self):
        return self._random

    def random_seed(self, seed=None):
        self._random.seed(seed)

    @property
    def providers(self):
        return self._providers

    def register_provider(self, provider):
        from rand.providers.base import RandProxyBaseProvider

        provider.rand = self
        if isinstance(provider, RandProxyBaseProvider):
            if provider.target:
                provider.target.rand = self
        # allowing to override providers
        self._providers[provider.prefix] = provider
        provider.register()

    def discover_providers(self, ns):
        from rand.providers.base import RandBaseProvider, RandProxyBaseProvider
        from rand.providers.ds.ds import RandDatasetBaseProvider

        def iter_namespace(ns_pkg: typing.Any):
            return pkgutil.walk_packages(ns_pkg.__path__, "%s." % ns_pkg.__name__)

        providers = {
            name: importlib.import_module(name)
            for finder, name, ispkg in iter_namespace(ns)
        }
        for module_name, module in providers.items():
            for obj_name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    exclude_classes = [
                        RandBaseProvider,
                        RandProxyBaseProvider,
                        RandDatasetBaseProvider,
                    ]
                    if issubclass(obj, RandBaseProvider) and obj not in exclude_classes:
                        try:
                            # TODO: perhaps adding new class function to check whether allowed to load?
                            self.register_provider(provider=obj())
                        except Exception as ex:  # pragma: no cover
                            logger.warning(
                                msg='E003 - Unable to auto-load provider "%s", Reason: %s'
                                % (obj_name, str(ex))
                            )

    @property
    def parsers(self):
        return self._parsers

    def register_parse(self, name: str, fn: ParseFnType):
        parse_name = "_parse_%s" % name.lower()
        invalid_chars = "".join(
            list(
                set(list(parse_name))
                - set(list(string.ascii_letters + string.digits + "_"))
            )
        )
        if len(invalid_chars) > 0:
            raise ValueError(
                'E002 - Name "%s" contains invalid character "%s"'
                % (name, invalid_chars)
            )
        self._parsers[parse_name] = fn

    def register_parse_wrapper(self, name: str):
        def decorator_fn(fn):
            self.register_parse(name=name, fn=fn)
            # this is ignored basically, there is no need to handle, when function is called
            # import functools
            # @functools.wraps(fn)
            # def wrapper_fn(*args, **kwargs):
            #     value = fn(*args, **kwargs)
            #     return value
            # return wrapper_fn

        return decorator_fn

    def do_parse(self, name: str, pattern: any, opts: dict):
        # the steps to executing fn of specified name:
        # 1. checking all the parser from custom providers in register_provider
        # 2. checking all the parser from self._parsers in register_parser
        # 3. finally, checking all the privitive parser from all _parse_xyz in self
        # 4. otherwise, return self._parse_noop
        from rand.providers.base import RandBaseProvider

        provider: RandBaseProvider
        # this is important to remember, it seems noop operation that removing _parse_ and adding back _parse_
        # this op important when a parser, return back as token with ('WORDS', ['test123'])
        # when 'WORDS' as name, it will be non callable because it expect as _parse_words
        # in order to support this, it is required to normalise all the _parse_ first and re-added it back
        name = re.sub("^_parse_", "", str(name))
        name = ("_parse_%s" % name).lower()
        for _, provider in self._providers.items():
            # remember, name here is always prefixed with _parse_[PREFIX] to avoid conflict
            result = provider.parse(name, pattern, opts)
            if result:
                return result
        fn = self._parsers.get(name)
        if fn:
            return fn(pattern, opts)
        fn = getattr(self, name, self._parse_noop)
        if fn:
            return fn(pattern)
        return self._parse_noop(pattern)

    @property
    def maps(self):
        return self._maps

    def register_map(self, name: str, fn: MapFnType):
        map_name = "_map_%s" % name.lower()
        invalid_chars = "".join(
            list(
                set(list(map_name))
                - set(list(string.ascii_letters + string.digits + "_"))
            )
        )
        if len(invalid_chars) > 0:
            raise ValueError(
                'E002 - Name "%s" contains invalid character "%s"'
                % (name, invalid_chars)
            )
        print("register", map_name)
        self._maps[map_name] = fn

    def register_map_wrapper(self, name: str):
        def decorator_fn(fn):
            self.register_map(name=name, fn=fn)
            # this is ignored basically, there is no need to handle, when function is called
            # import functools
            # @functools.wraps(fn)
            # def wrapper_fn(*args, **kwargs):
            #     value = fn(*args, **kwargs)
            #     return value
            # return wrapper_fn

        return decorator_fn

    def do_map(self, name: str, pattern: any, opts: dict):
        # the steps to executing fn of specified id and name:
        # 1. checking all the map from custom providers in register_provider
        # 2. checking all the map from self._maps in register_map
        # 3. finally, checking all the privitive map from all _map_xyz in self
        # 4. otherwise, return self._parse_noop
        from rand.providers.base import RandBaseProvider

        provider: RandBaseProvider
        name = re.sub("^_map_", "", str(name))
        name = ("_map_%s" % name).lower()
        for _, provider in self._providers.items():
            result = provider.map(name, pattern, opts)
            if result:
                return result
        fn = self._maps.get(name)
        if fn:
            return fn(pattern, opts)
        fn = getattr(self, name, None)
        if fn:
            return fn(pattern, opts)

    @property
    def filters(self):
        return self._filters

    def register_filter(self, name: str, fn: FilterFnType):
        filter_name = "_filter_%s" % name.lower()
        invalid_chars = "".join(
            list(
                set(list(filter_name))
                - set(list(string.ascii_letters + string.digits + "_"))
            )
        )
        if len(invalid_chars) > 0:
            raise ValueError(
                'E002 - Name "%s" contains invalid character "%s"'
                % (name, invalid_chars)
            )
        self._filters[filter_name] = fn

    def register_filter_wrapper(self, name: str):
        def decorator_fn(fn):
            self.register_filter(name=name, fn=fn)
            # this is ignored basically, there is no need to handle, when function is called
            # import functools
            # @functools.wraps(fn)
            # def wrapper_fn(*args, **kwargs):
            #     value = fn(*args, **kwargs)
            #     return value
            # return wrapper_fn

        return decorator_fn

    def do_filter(self, name: str, pattern: any, opts: dict):
        # the steps to executing fn of specified id and name:
        # 1. checking all the filter from custom providers in register_provider
        # 2. checking all the filter from self._filters in register_map
        # 3. finally, checking all the privitive filter from all _filter_xyz in self
        # 4. otherwise, return self._filter_noop
        from rand.providers.base import RandBaseProvider

        provider: RandBaseProvider
        name = re.sub("^_filter_", "", str(name))
        name = ("_filter_%s" % name).lower()
        for _, provider in self._providers.items():
            result = provider.filter(name, pattern, opts)
            if result is False:
                return None
            if result:
                return result
        fn = self._filters.get(name)
        if fn:
            return fn(pattern, opts)
        fn = getattr(self, name, None)
        if fn:
            return fn(pattern, opts)

    def _parse_noop(self, pattern):
        return ""

    def _parse_literal(self, pattern):
        return chr(pattern[1])

    def _parse_any(self, pattern):
        # input: .
        # pattern: (ANY, None)
        _, val = pattern
        val = val if val is not None else ANY_NONE
        return self.random.choice(list(val))

    def _parse_branch(self, pattern):
        # input: ro|ko
        # pattern: (BRANCH, (None, [[(LITERAL, 114), (LITERAL, 111)], [(LITERAL, 107), (LITERAL, 111)]]))
        _, (_, values) = pattern
        # get the list of sequence
        seq = [
            self._parse_list(value if isinstance(value, list) else [value])
            for value in values
        ]
        return self.random.choice(seq)

    def _parse_in(self, pattern):
        # input: r|o
        # pattern: [(IN, [(LITERAL, 114), (LITERAL, 111)])]
        _, values = pattern
        # get the list of sequence
        seq = [
            self._parse_list(value if isinstance(value, list) else [value])
            for value in values
        ]
        return self.random.choice(seq)

    def _parse_max_repeat(self, pattern):
        # input: r{2,8}
        # pattern: (MAX_REPEAT, (2, 8, [(LITERAL, 114)]))
        _, (start, end, patterns) = pattern
        if end == MAXREPEAT and MAX_REPEAT_MAXREPEAT is None:
            # input: r{2,}
            # pattern: (MAX_REPEAT, (2, MAXREPEAT, [(LITERAL, 114)]))
            raise ValueError(
                "E001 - Notation {n,} or * or + is not supported, please specify the MAX_REPEAT_MAXREPEAT"
            )
        total = self.random.randint(start, end)
        return "".join([self._parse(patterns) for _ in range(total)])

    def _parse_range(self, pattern):
        # input: [a-z]
        # pattern: (RANGE, (97, 122))
        _, (start, end) = pattern
        return chr(self.random.randint(start, end))

    def _parse_subpattern(self, pattern):
        # input: (ro)
        # pattern: (SUBPATTERN, (1, 0, 0, [(LITERAL, 114), (LITERAL, 111)]))
        _, (subpattern_index, _, _, patterns) = pattern
        if len(patterns) >= 2:
            if patterns[0] == (LITERAL, 58) and patterns[-1] == (LITERAL, 58):
                # input: (::)
                # pattern: (SUBPATTERN, (1, 0, 0, [(LITERAL, 58), (LITERAL, 58)]))
                # get the custom name
                token = "".join(map(lambda x: str(x), self._parse_list(patterns[1:-1])))
                # get the args based on the token and input args
                args, arg_name = None, str(subpattern_index)
                # if named args specified like (:en_stringify:arg_name:)
                if ":" in token:
                    token, arg_name = token.split(":")
                args = self._args.get(arg_name, None)
                # get parser based on token with _parse_noop as default
                opts = {"token": token, "args": args}
                name = "_parse_%s" % str(token).lower()
                result = self.do_parse(name, pattern, opts)
                if isinstance(args, dict):
                    # the reason why maps and filter are executed in this section of subpattern ()
                    # because if we put inside do_parse, every single thing will be executed in there which is bad
                    # for example (abc) will be execute maps and filters for a, b, c, and abc
                    maps, filters = args.get("maps", []), args.get("filters", [])
                    result = self._map(pattern=result, maps=maps)
                    result = self._filter(pattern=result, filters=filters)
                return result
        return self._parse(patterns)

    def _parse_list(self, pattern):
        # pattern: [(LITERAL, 114), (LITERAL, 111)]
        # return ''.join(map(lambda x: str(x), filter(None, [self._parse(x) for x in pattern])))
        return list(filter(None, [self._parse(x) for x in pattern]))

    def _parse(self, pattern) -> typing.Any:
        if isinstance(pattern, SubPattern) or isinstance(pattern, list):
            # for subpattern, check what is the type, if non list, force it to be list
            pattern = pattern if type(pattern) == "list" else list(pattern)
            # handle when result return list after the parse result
            # [(LITERAL, 114), (LITERAL, 111)]
            return "".join(map(lambda x: str(x), self._parse_list(pattern)))
        elif isinstance(pattern, tuple):
            token = pattern[0]
            # get parser based on token with _parse_noop as default
            result = self.do_parse(token, pattern=pattern, opts={})
            # the reason to throw again back to _parse because it may contain token
            return self._parse(result)
        return pattern

    def _map(self, pattern: any, maps: typing.List[dict]):
        # pattern is the result from _parse
        for map_ in maps:
            name, opts = map_.get("name", None), {"token": pattern, "args": map_}
            if pattern and name:
                # ensure remove name from the map_
                opts["args"].pop("name")
                pattern = self.do_map(name=name, pattern=pattern, opts=opts)
        return pattern

    def _filter(self, pattern: any, filters: list):
        # pattern is the result from _parse and _map
        for filter_ in filters:
            name, opts = filter_.get("name", None), {"token": pattern, "args": filter_}
            if pattern and name:
                # ensure remove name from the map_
                opts["args"].pop("name")
                if self.do_filter(name=name, pattern=pattern, opts=opts) is False:
                    return None
        return pattern

    def _prepare_args(self, args):
        # args input will be always be either list or dict
        # each item needs to be also either list or dict, either of those, will be assumed as list with single arg

        # for example
        # rand.gen('(:faker_numerify:)', ['#####'])
        # faker_numerify signature: fake.numerify('###') or fake.numerify(text='###')
        # arg_name format:
        # - (:faker_numerify:) = implicit arg_name by the subpattern_index
        # - (:faker_numerify:xyz:) = explicit arg_name
        # args format:
        # - ['#####'] = auto converted to [['#####']]
        # - [['#####']] = no changes
        # - {'xyz': '#####'} = auto converted to {'xyz': ['#####']}
        # - {'xyz': ['#####']} = no changes
        # - {'xyz': {'text': '#####'} = no changes
        vals = {}
        if isinstance(args, list):
            for i, v in enumerate(args):
                vals[str(i + 1)] = (
                    v if isinstance(v, list) or isinstance(v, dict) else [v]
                )
        elif isinstance(args, dict):
            for i, v in args.items():
                vals[str(i)] = v if isinstance(v, list) or isinstance(v, dict) else [v]
        return vals

    def sre_parse_compile_parse(self, pattern) -> SubPattern:
        # get normalised regex pattern from regex compiler
        regex_pattern: str = re.compile(pattern=pattern).pattern
        # return parsed pattern from regex
        # input: abc
        # output: [(LITERAL, 97), (LITERAL, 98), (LITERAL, 99)]
        regex_parsed: SubPattern = sre_parse.parse(regex_pattern)
        return regex_parsed

    def gen(
        self,
        pattern: str,
        args: typing.Union[list, dict] = None,
        maps: list = None,
        filters: list = None,
        n: int = 1,
    ) -> typing.List[str]:
        # get normalised regex pattern from regex compiler and get parsed pattern
        regex_parsed: SubPattern = self.sre_parse_compile_parse(pattern)
        # generate randomly X times
        self._args = self._prepare_args(args)
        rs = []
        for _ in range(n):
            r = self._parse(regex_parsed)
            r = self._map(r, maps if maps else [])
            r = self._filter(r, filters if filters else [])
            if r is not None:
                rs.append(r)
        self._args = {}
        return rs
