from ast import NodeVisitor, parse
from sys import exc_info


class SafeEval(NodeVisitor):
    def __init__(self, exp: str):
        self.__operations = ["FloorDiv", "UAdd", "USub", "Mult", "Div", "Expression", "BinOp", "Constant", "Add", "Sub", "UnaryOp"]
        self.__result = self.__calc(
            exp.replace("x", "*").replace(",", "").replace("%", "/100").replace("×", "*").replace(" ", "").replace("^", "**")
        )

    def __calc(self, exp):
        try:
            node = parse(exp, "<usercode>", "eval")
            self.visit(node)
        except Exception as ex:
            return False, str(ex)
        try:
            result = eval(compile(node, "<usercode>", "eval"), {})
        except Exception as ex:
            et, ev, erb = exc_info()
            return False, "{}: {}".format(type(ex).__name__, ev)
        return True, result

    def generic_visit(self, node):
        if type(node).__name__ in self.__operations:
            return NodeVisitor.generic_visit(self, node)
        raise ValueError("`{optype}` operation is forbidden!".format(optype=type(node).__name__))

    def result(self):
        return self.__result
