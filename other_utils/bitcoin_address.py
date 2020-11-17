from typing import Union
from random import randrange
from binascii import unhexlify
from hashlib import sha256, new

HEX_DIGITS = "0123456789abcdef"
ALPHABET = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
SHA = 2 ** 256
PRIME = SHA - 2 ** 32 - 977
GX = 55066263022277343669578718895168534326250603453777594175500187360389116729240
GY = 32670510020758816978083085130507043184471273380659243275938904335757337482424


class BitcoinAddress:
    def __init__(self, privHex=None):
        self.__privHex = privHex or self.__genPrivHex()
        self.__privWIF = self.__encodePriv()
        self.__addr = self.__privToAddr()

    @staticmethod
    def __genPrivHex():
        return "".join(
            "{:02x}".format(i) for i in sha256(
                bytes(str(randrange(SHA)), "utf-8")
            ).digest()
        )

    @staticmethod
    def __encode(val, base, minlen):
        base, minlen = int(base), int(minlen)
        codestr = HEX_DIGITS if base == 16 else ALPHABET.decode("utf-8")
        bytesres = bytes()
        while val > 0:
            curcode = codestr[val % base]
            bytesres = bytes([ord(curcode)]) + bytesres
            val //= base
        padsize = minlen - len(bytesres)
        padele = b"\x00" if base == 256 else b"1" if base == 58 else b"0"
        if padsize > 0:
            bytesres = padele * padsize + bytesres
        strres = "".join([chr(i) for i in bytesres])
        return bytesres if base == 256 else strres

    @staticmethod
    def __decode(string, base):
        if base == 256 and isinstance(string, str):
            string = bytes(bytearray.fromhex(string))
        base = int(base)
        result = 0
        if base == 16:
            string = string.casefold()
        while len(string) > 0:
            result = result * base + (
                string[0]
                if base == 256
                else HEX_DIGITS.find(
                    string[0] if isinstance(
                        string[0], str
                    ) else chr(string[0])
                )
            )
            string = string[1:]
        return result

    @staticmethod
    def __base58Encode(v: Union[str, bytes], alphabet: bytes=ALPHABET):
        if isinstance(v, str):
            v = v.encode("ascii")
        npad = len(v)
        v = v.lstrip(b"\0")
        npad -= len(v)
        p, acc = 1, 0
        for c in reversed(v):
            acc += p * c
            p <<= 8
        string = b""
        while acc:
            acc, idx = divmod(acc, 58)
            string = alphabet[idx:idx + 1] + string
        return alphabet[0:1] * npad + string

    def __encodePriv(self):
        ex = "80" + self.__privHex
        sha = sha256(
            unhexlify(sha256(unhexlify(ex)).hexdigest())
        ).hexdigest()
        return self.__base58Encode(unhexlify(ex + sha[:8])).decode("utf-8")

    def __jacoMultiply(self, gp, n):
        if n == 1:
            return gp
        p = self.__jacoMultiply(gp, n // 2)
        ysq = (p[1] ** 2) % PRIME
        s = (4 * p[0] * ysq) % PRIME
        m = (3 * p[0] ** 2 + 0 * p[2] ** 4) % PRIME
        nx = (m ** 2 - 2 * s) % PRIME
        ny = (m * (s - nx) - 8 * ysq ** 2) % PRIME
        nz = (2 * p[1] * p[2]) % PRIME
        p = nx, ny, nz
        if not n % 2:
            return p
        u1 = (p[0] * gp[2] ** 2) % PRIME
        u2 = (gp[0] * p[2] ** 2) % PRIME
        s1 = (p[1] * gp[2] ** 3) % PRIME
        s2 = (gp[1] * p[2] ** 3) % PRIME
        h, r = u2 - u1, s2 - s1
        h2 = (h ** 2) % PRIME
        h3 = (h * h2) % PRIME
        u1h2 = (u1 * h2) % PRIME
        nx = (r ** 2 - h3 - 2 * u1h2) % PRIME
        ny = (r * (u1h2 - nx) - s1 * h3) % PRIME
        nz = (h * p[2] * gp[2]) % PRIME
        return nx, ny, nz

    def __privToAddr(self):
        jm = self.__jacoMultiply(
            (GX, GY, 1),
            self.__decode(self.__privHex, 16)
        )
        lm, hm = 1, 0
        low, high = jm[2] % PRIME, PRIME
        while low > 1:
            r = high // low
            nm, newvar = hm - lm * r, high - low * r
            lm, low, hm, high = nm, newvar, lm, low
        toinv = lm % PRIME
        toencode = (jm[0] * toinv ** 2) % PRIME, (jm[1] * toinv ** 3) % PRIME
        inp = new(
            "ripemd160",
            sha256(
                unhexlify(
                    "04" + self.__encode(toencode[0], 16, 64) +
                    self.__encode(toencode[1], 16, 64)
                )
            ).digest(),
        ).digest()
        inpfmtd = bytes([0]) + inp
        lzbytes = 0
        for i in inpfmtd:
            if i != 0:
                break
            lzbytes += 1
        checksum = sha256(sha256(inpfmtd).digest()).digest()[:4]
        return "1" * lzbytes + self.__encode(
            self.__decode(inpfmtd + checksum, 256), 58, 0
        )

    def getAddr(self):
        return self.__addr, self.__privWIF, self.__privHex
