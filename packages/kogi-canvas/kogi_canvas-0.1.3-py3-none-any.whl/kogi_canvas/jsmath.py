import math

class JSCompatibleMath:
    E = math.e
    LN10 = math.log(10)
    LN2 = math.log(2)
    LOG2E = 1 / math.log(2)
    LOG10E = 1 / math.log(10)
    PI = math.pi
    SQRT1_2 = math.sqrt(0.5)
    SQRT2 = math.sqrt(2)

    @staticmethod
    def abs(x):
        return abs(x)

    @staticmethod
    def acos(x):
        return math.acos(x)

    @staticmethod
    def acosh(x):
        return math.acosh(x)

    @staticmethod
    def asin(x):
        return math.asin(x)

    @staticmethod
    def asinh(x):
        return math.asinh(x)

    @staticmethod
    def atan(x):
        return math.atan(x)

    @staticmethod
    def atan2(y, x):
        return math.atan2(y, x)

    @staticmethod
    def atanh(x):
        return math.atanh(x)

    @staticmethod
    def cbrt(x):
        return x ** (1 / 3)

    @staticmethod
    def ceil(x):
        return math.ceil(x)

    @staticmethod
    def clz32(x):
        # Emulates JavaScript's Math.clz32 function
        return len(bin(x)) - len(bin(x).lstrip('-0b'))

    @staticmethod
    def cos(x):
        return math.cos(x)

    @staticmethod
    def cosh(x):
        return math.cosh(x)

    @staticmethod
    def exp(x):
        return math.exp(x)

    @staticmethod
    def expm1(x):
        return math.expm1(x)

    @staticmethod
    def floor(x):
        return math.floor(x)

    @staticmethod
    def fround(x):
        # Emulates JavaScript's Math.fround function (single precision)
        return float(math.fsum([x]))

    @staticmethod
    def hypot(*args):
        return math.hypot(*args)

    @staticmethod
    def imul(a, b):
        # Emulates JavaScript's Math.imul function (32-bit integer multiplication)
        return (a * b) & 0xFFFFFFFF

    @staticmethod
    def log(x):
        return math.log(x)

    @staticmethod
    def log10(x):
        return math.log10(x)

    @staticmethod
    def log1p(x):
        return math.log1p(x)

    @staticmethod
    def log2(x):
        return math.log2(x)

    @staticmethod
    def max(*args):
        return max(*args)

    @staticmethod
    def min(*args):
        return min(*args)

    @staticmethod
    def pow(x, y):
        return math.pow(x, y)

    @staticmethod
    def random():
        return math.random()

    @staticmethod
    def round(x):
        return round(x)

    @staticmethod
    def sign(x):
        return (x > 0) - (x < 0)

    @staticmethod
    def sin(x):
        return math.sin(x)

    @staticmethod
    def sinh(x):
        return math.sinh(x)

    @staticmethod
    def sqrt(x):
        return math.sqrt(x)

    @staticmethod
    def tan(x):
        return math.tan(x)

    @staticmethod
    def tanh(x):
        return math.tanh(x)

    @staticmethod
    def trunc(x):
        return math.trunc(x)

