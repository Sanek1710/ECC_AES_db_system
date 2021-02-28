from Cryptodome.Math.Numbers import Integer
from Cryptodome.Hash.SHA256 import SHA256Hash
from random import randint

class BasePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toElPoint(self, ec):
        assert ec.check(self), 'ElPoint is not on ElCurve'
        return ElPoint(self.x % ec.p, self.y % ec.p, ec)

    def json(self):
        return {
            "x": self.x,
            "y": self.y
        }

class ElCurve():
    def __init__(self, A, B, p):
        if (A < 0): A %= p
        self.A = A
        if (B < 0): B %= p
        self.B = B
        self.p = p
        self._O = BasePoint(0, 0)
        pass

    def __get_O(self):
        return ElPoint(self._O.x, self._O.y, self)
    O = property(__get_O)

    def check(self, point):
        if (point.x == 0 and point.y == 0):
            return True
        return (point.y**2 - point.x**3 - self.A*point.x - self.B) %self.p == 0

    def checkAB(self):
        return (4*self.A**3 - 27*self.B**2) % self.p

    def __str__(self):
        return '\n'.join([
            'Elliptic Curve:',
            '  A = ' + str(self.A),
            '  B = ' + str(self.B)
        ])

    def json(self):
        return {
            "A": self.A,
            "B": self.B,
            "p": self.p
        }

class ElPoint(BasePoint):
    def __init__(self, x, y, curve):
        super().__init__(x, y)
        self.curve = curve
        pass

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __neg__(self):
        return ElPoint(self.x, -self.y, self.curve)

    def __add__(self, other):
        if (self == self.curve.O):
            return other
        if (other == self.curve.O):
            return self
        p = self.curve.p
        if (self.x == other.x):
            if ((self.y + other.y) % p == 0):
                return self.curve.O
            else:
                l = (((3*self.x**2 + self.curve.A) % p) * int(Integer(2*self.y).inverse(p))) % p
        else:
            l = ((other.y - self.y) * int(Integer(other.x - self.x).inverse(p))) % p
        x = (pow(l,2,p) - self.x - other.x) % p
        y = (l*(self.x - x) - self.y) % p
        return ElPoint(x, y, self.curve)
    
    def __rmul__(self, val : int):
        if (val == 0):
            return self.curve.O
        Q = self.curve.O
        for i in bin(val)[2:]:
            Q = Q + Q
            if (i == '1'):
                Q = Q + self
        return Q

    def __mul__(self, val : int):
        return self.__rmul__(val)

    def __str__(self):
        if self == self.curve.O:
            return '(+oo, +oo)'
        else:
            return str((self.x, self.y))

    def __repr__(self):
        if self == self.curve.O:
            return '(+oo, +oo)'
        else:
            return repr((self.x, self.y))

    def hash(self):
        sha = SHA256Hash(self.x.to_bytes((self.x.bit_length() + 7) // 8, byteorder="big"))
        sha.update(self.y.to_bytes((self.y.bit_length() + 7) // 8, byteorder="big"))
        return sha.digest()

    def project(self):
        if (self == self.curve.O):
            return ElPointProject(0, 0, 0, self.curve)
        return ElPointProject(self.x, self.y, 1, self.curve)
    pass

class ElPointProject():
    def __init__(self, x, y, z, curve):
        self.x = x
        self.y = y
        self.z = z
        self.curve = curve
        pass

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self.__eq__(other)

    def __neg__(self):
        return ElPointProject(self.x, -self.y, self.z, self.curve)

    def __add__(self, other):
        if (self.z == 0):
            return other
        if (other.z == 0):
            return self

        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = other.x, other.y, other.z
        A = self.curve.A
        B = self.curve.B
        p = self.curve.p
        if (self == other):
            x = (2*y1*z1*((3*x1**2 + A*z1**2)**2 - 8*x1*y1**2*z1)) % p
            y = (4*y1**2*z1*(3*x1*(3*x1**2 + A*z1**2) - 2*y1**2*z1)-(3*x1**2 + A*z1**2)**3) % p
            z = (8*y1**3*z1**3) % p
        else:
            x = ((x2*z1 - x1*z2)*(z1*z2*(y2*z1-y1*z2)**2 - (x2*z1+x1*z2)*(x2*z1-x1*z2)**2)) % p
            y = ((x2*z1 - x1*z2)**2*(y2*z1*(x2*z1 + 2*x1*z2)-y1*z2*(x1*z2+2*x2*z1)) - z1*z2*(y2*z1 - y1*z2)**3) % p
            z = (z1*z2*(x2*z1 - x1*z2)**3) % p
        return ElPointProject(x, y, z, self.curve)
    def __rmul__(self, val : int):
        if (val == 0):
            return self.curve.O
        Q = self.curve.O.project()
        for i in bin(val)[2:]:
            Q = Q + Q
            if (i == '1'):
                Q = Q + self
        return Q

    def check_mul(self, val : int, n : Integer):
        Q = self.curve.O.project()
        while val:
            if val & 1:
                Q = Q + self
                assert Q.z != 0 and n.gcd(Q.z)
            self = self + self
            val >>= 1
        return Q

    def __mul__(self, val : int):
        return self.__rmul__(val)

    def __str__(self):
        return str((self.x, self.y, self.z))

    def __repr__(self):
        return repr((self.x, self.y, self.z))

    def toElPoint(self):
        if (self.z == 0):
            return self.curve.O
        z_inv = int(Integer(self.z).inverse(self.curve.p))
        x = self.x * z_inv % self.curve.p
        y = self.y * z_inv % self.curve.p
        return ElPoint(x, y, self.curve)

def generate(Q, n):
    A = randint(1, n - 1)
    B = (Q.y**2 - Q.x**3 - A*Q.x) % n
    ec = ElCurve(A, B, n)
    if not ec.checkAB():
        return None
    return ec