import ast


class SafeEval:
    def __init__(self, s: str):
        self.__s = s

    def __evaluate(self, astt: ast.AST):
        if not isinstance(astt, ast.AST):
            return astt
        func = Evaluable.NH.get(astt.__class__.__name__.casefold())
        if not func:
            raise ValueError
        gen = func(astt)
        n = next(gen)
        while True:
            if not isinstance(n, ast.AST):
                return n
            next(gen)
            res = self.__evaluate(n)
            n = gen.send(res)

    def __comp(self):
        return compile(source=self.__s, filename="<unknown>", mode="eval", flags=ast.PyCF_ONLY_AST)

    def safeEval(self):
        astt = self.__comp()
        assert isinstance(astt, ast.Expression)
        return self.__evaluate(astt.body)


class Evaluable(type):
    NH = {}

    def __new__(mcs, name, bases, classdict, *, en):
        nhl = []
        for node in en:
            if not issubclass(node, ast.AST):
                raise ValueError
            key = node.__name__.casefold()
            if key in Evaluable.NH:
                raise ValueError
            func = classdict.get(key)
            if not func or not isinstance(func, classmethod):
                raise ValueError
            nhl.append(key)
        sc = super().__new__(mcs, name, bases, classdict)
        for handler in nhl:
            Evaluable.NH[handler] = getattr(sc, handler)
        return sc


class Arithmetic(metaclass=Evaluable, en=(ast.Num, ast.UnaryOp, ast.BinOp)):
    @classmethod
    def num(cls, node: ast.Num):
        yield node.n

    @classmethod
    def unaryop(cls, node: ast.UnaryOp):
        yield node.operand
        operand = yield
        if not isinstance(operand, (int, float, complex)):
            raise ValueError
        if isinstance(node.op, ast.UAdd):
            yield + operand
        elif isinstance(node.op, ast.USub):
            yield - operand
        else:
            if isinstance(node.op, complex):
                raise ValueError
            yield ~ operand

    @classmethod
    def binop(cls, node: ast.BinOp):
        yield node.left
        left = yield
        yield node.right
        right = yield
        if not isinstance(left, (int, float, complex)) or not isinstance(right, (int, float, complex)):
            raise ValueError
        op = node.op
        if isinstance(op, ast.Add):
            yield left + right
        elif isinstance(op, ast.Sub):
            yield left - right
        elif isinstance(op, ast.Mult):
            yield left * right
        elif isinstance(op, ast.Div):
            yield left / right
        elif isinstance(op, ast.FloorDiv):
            yield left // right
        elif isinstance(op, ast.Mod):
            yield left % right
        elif isinstance(op, ast.Pow):
            yield left ** right
        elif isinstance(op, ast.LShift):
            yield left << right
        elif isinstance(op, ast.RShift):
            yield left >> right
        elif isinstance(op, ast.BitAnd):
            yield left & right
        elif isinstance(op, ast.BitOr):
            yield left | right
        else:
            yield left ^ right
