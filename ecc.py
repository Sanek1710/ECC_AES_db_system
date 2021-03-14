from el_curve import ElCurve, ElPoint
from random import randint
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad 

def generate():
    A = -1
    B = 43710617685176640081115791799072828565464240578102647674571004997445073590733
    p = 57896044623304043104299010705220227593411047292536827792690781397890347747339
    EC = ElCurve(A, B, p)

    PX = 2375898023066818922259876468809957958853252818454947955735283254927910319797
    PY = 41494802599112005706154126874294477637447794334726831230592311725680992538390
    q = 28948022311652021552149505352610113796704505182029833954354922263763927570003
    P = ElPoint(PX, PY, EC)

    d = 94861536845132794615
    Q = d*P

    return ECC(EC, P, Q, q, d)

def construct(A, B, p, PX, PY, QX, QY):
    EC = ElCurve(A, B, p)
    P = ElPoint(PX, PY, EC)
    Q = ElPoint(QX, QY, EC)

    return ECC(EC, P, Q)



class EccPublicKey:
    def __init__(self, EC, P, Q):
        self.EC = EC
        self.P = P
        self.Q = Q

    def json(self):
        return {
            "EC" : self.EC.json(),
            "P"  : self.P.json(),
            "Q"  : self.Q.json()
        }



class ECC:
    def __init__(self, EC : ElCurve, P : ElPoint, Q : ElPoint, q=None, d=None):
        self.EC = EC
        self.P = P
        self.Q = Q
        if q: self.q = q
        if d: self.d = d
    
    def encrypt(self, data):
        r = randint(2, self.q)
        k = r*self.Q
        ks = k.hash()
        aes = AES.new(ks, AES.MODE_ECB)
        c = aes.encrypt(pad(data, 32))
        kc = r*self.P
        return (c, (kc.x, kc.y))

    def decrypt(self, cdata):
        c, kc = cdata
        kc = ElPoint(kc[0], kc[1], self.EC)
        k = self.d * kc
        ks = k.hash()
        aes = AES.new(ks, AES.MODE_ECB)
        data = unpad(aes.decrypt(c), 32)
        return data
        
    def publicKey(self):
        return EccPublicKey(self.EC, self.P, self.Q)

    def json(self):
        return {
                "EC" : self.EC.json(),
                "P"  : self.P.json(),
                "Q"  : self.Q.json(),
                "q"  : self.q,
                "d"  : self.d
            }
        