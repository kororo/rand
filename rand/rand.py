import re
import sre_parse
import string
import typing
from sre_parse import SubPattern
from sre_constants import LITERAL, MAXREPEAT
from random import Random

# support . notation
ANY_NONE = string.printable

# support MAX_REPEAT_MAXREPEAT
MAX_REPEAT_MAXREPEAT = None


class Rand:
    _random: Random
    _opts: dict
    _args: dict

    def __init__(self, seed=None, opts: dict = None):
        self._random = Random()
        self._opts = opts if opts else {}
        self._args = {}
        if seed:
            self.random_seed(seed)

    @property
    def random(self):
        return self._random

    def random_seed(self, seed=None):
        self._random.seed(seed)

    def register_provider(self, provider):
        provider.register()

    def register_parse(self, name: str, fn: typing.Callable[['Rand', typing.Any], typing.Any]):
        parse_name = '_parse_%s' % name.lower()
        invalid_chars = ''.join(list(set(list(parse_name)) - set(list(string.ascii_letters + '_'))))
        if len(invalid_chars) > 0:
            raise ValueError('E002 - Name "%s" contains invalid character "%s"' % (name, invalid_chars))
        setattr(self, parse_name, fn)

    def _parse_noop(self, pattern):
        return ''

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
        seq = [self._parse_list(value if isinstance(value, list) else [value]) for value in values]
        return self.random.choice(seq)

    def _parse_in(self, pattern):
        # input: r|o
        # pattern: [(IN, [(LITERAL, 114), (LITERAL, 111)])]
        _, values = pattern
        # get the list of sequence
        seq = [self._parse_list(value if isinstance(value, list) else [value]) for value in values]
        return self.random.choice(seq)

    def _parse_max_repeat(self, pattern):
        # input: r{2,8}
        # pattern: (MAX_REPEAT, (2, 8, [(LITERAL, 114)]))
        _, (start, end, patterns) = pattern
        if end == MAXREPEAT and MAX_REPEAT_MAXREPEAT is None:
            # input: r{2,}
            # pattern: (MAX_REPEAT, (2, MAXREPEAT, [(LITERAL, 114)]))
            raise ValueError('E001 - Notation {n,} or * or + is not supported, please specify the MAX_REPEAT_MAXREPEAT')
        total = self.random.randint(start, end)
        return ''.join([self._parse(patterns) for _ in range(total)])

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
                token = self._parse_list(patterns[1:-1])
                # get the args based on the token and input args
                args, arg_name = None, str(subpattern_index)
                # if named args specified like (:en_stringify:arg_name:)
                if ':' in token:
                    token, arg_name = token.split(':')
                args = self._args.get(arg_name, None)
                # get parser based on token with _parse_noop as default
                opts = {'token': token, 'args': args}
                name = '_parse_%s' % str(token).lower()
                return getattr(self, name, lambda ri, _, o: self._parse_noop(pattern))(self, pattern, opts)
        return self._parse(patterns)

    def _parse_list(self, pattern):
        # pattern: [(LITERAL, 114), (LITERAL, 111)]
        return ''.join(map(lambda x: str(x), filter(None, [self._parse(x) for x in pattern])))

    def _parse(self, pattern) -> typing.Any:
        if isinstance(pattern, SubPattern):
            # handle subpattern class specially
            return self._parse_list(pattern)
        elif isinstance(pattern, tuple):
            token = pattern[0]
            # get parser based on token with _parse_noop as default
            return getattr(self, '_parse_%s' % str(token).lower(), self._parse_noop)(pattern)
        return ''

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
                vals[str(i + 1)] = v if isinstance(v, list) or isinstance(v, dict) else [v]
        elif isinstance(args, dict):
            for i, v in args.items():
                vals[str(i)] = v if isinstance(v, list) or isinstance(v, dict) else [v]
        return vals

    def gen(self, pattern: str, args: typing.Union[list, dict] = None,
            maps=None, filters=None,
            n: int = 1) -> typing.List[str]:
        # get normalised regex pattern from regex compiler
        regex_pattern: str = re.compile(pattern=pattern).pattern
        # return parsed pattern from regex
        # input: abc
        # output: [(LITERAL, 97), (LITERAL, 98), (LITERAL, 99)]
        regex_parsed: SubPattern = sre_parse.parse(regex_pattern)
        # generate randomly X times
        self._args = self._prepare_args(args)
        print(pattern, self._args, regex_parsed)
        rs = [self._parse(regex_parsed) for _ in range(n)]
        self._args = {}
        return rs

    def map(self, x):
        pass

    def _map_lower(self, opt=None):
        def _map_lower():
            pass

        pass

    def filter(self, x):
        pass


# print(rand.many('a|b|c|d|r|o|a', maps=[
#     'lower',
#     ('lower', []),
#     ('replace', {'find': '', 'replace': ''})
# ], filters=[
#     ('regex', {'pattern': ''})
# ], n=1))
#
#
