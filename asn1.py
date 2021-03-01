TAG_INTEGER = bytes([0x02])
TAG_UTF_STRING = bytes([0x0C])
TAG_BYTE_STRING = bytes([0x04])
TAG_SEQUENCE = bytes([0x30])
TAG_SET = bytes([0x31])

def encode_len(value : int) -> bytes:
    if (value < 128):
        return bytes([value])
    else:
        len_len = (value.bit_length() + 7) // 8
        asn_len = bytes([0x80 | len_len])
        asn_len += value.to_bytes(len_len, "big")
        return asn_len

def decode_len(data: bytes):
    if ((data[0] & 0x80) == 0):
        return data[0], data[1:]
    else:
        len_len = data[0] & 0x7f
        return int.from_bytes(data[1:len_len + 1], 'big'), data[len_len + 1:]

def load(object):
    if isinstance(object, (SEQUENCE, SET, INTEGER, UTF_STRING, BYTE_STRING)):
        return object
    elif isinstance(object, list) or isinstance(object, tuple):
        return SEQUENCE(object)
    elif isinstance(object, set):
        return SET(object)
    elif isinstance(object, int):
        return INTEGER(object)
    elif isinstance(object, str):
        return UTF_STRING(object)
    elif isinstance(object, bytes):
        return BYTE_STRING(object)
    else:
        raise TypeError("Unsupported object type")

class SEQUENCE(list):
    def __new__(cls, *args, **kw):
        return list.__new__(cls, *args, **kw)

    def encode(self):
        data = b''.join(load(obj).encode() for obj in self)
        return b''.join([
            TAG_SEQUENCE, 
            encode_len(len(data)),
            data
        ])

    @staticmethod
    def decode(data : bytes):
        dlen, data = decode_len(data)
        seqdata, taildata = data[:dlen], data[dlen:]
        seq = []
        while seqdata:
            obj, seqdata = decode(seqdata)
            seq.append(obj)

        return seq, taildata

class SET(set):
    def __new__(cls, *args, **kw):
        return set.__new__(cls, *args, **kw)

    def encode(self):
        data = b''.join(load(obj).encode() for obj in self)
        return b''.join([
            TAG_SET, 
            encode_len(len(data)),
            data
        ])
    
    @staticmethod
    def decode(data : bytes):
        dlen, data = decode_len(data)
        seqdata, taildata = data[:dlen], data[dlen:]
        seqset = set()
        while seqdata:
            obj, seqdata = decode(seqdata)
            seqset.add(obj)
        return seqset, taildata

class INTEGER(int):
    def __new__(cls, *args, **kw):
        return int.__new__(cls, *args, **kw)

    def encode(self):
        numlen = (self.bit_length() + 7) // 8
        return b''.join([
            TAG_INTEGER, 
            encode_len(numlen),
            self.to_bytes(numlen, 'big')
        ])

    @staticmethod
    def decode(data : bytes):
        dlen, data = decode_len(data)
        return int.from_bytes(data[:dlen], 'big'), data[dlen:]

class UTF_STRING(str):
    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def encode(self):
        return b''.join([
            TAG_UTF_STRING, 
            encode_len(len(self)),
            bytes(self, 'utf-8')
        ])

    @staticmethod
    def decode(data : bytes):
        dlen, data = decode_len(data)
        return str(data[:dlen], encoding='utf-8'), data[dlen:]

class BYTE_STRING(bytes):
    def __new__(cls, *args, **kw):
        return bytes.__new__(cls, *args, **kw)

    def encode(self):
        return b''.join([
            TAG_BYTE_STRING, 
            encode_len(len(self)),
            self
        ])

    @staticmethod
    def decode(data : bytes):
        dlen, data = decode_len(data)
        return data[:dlen], data[dlen:]

def encode(value):
    value = load(value)
    return value.encode()

def decode(data : bytes):

    if data[0:1] == TAG_INTEGER:
        return INTEGER.decode(data[1:])

    elif data[0:1] == TAG_UTF_STRING:
        return UTF_STRING.decode(data[1:])

    elif data[0:1] == TAG_BYTE_STRING:
        return BYTE_STRING.decode(data[1:])

    elif data[0:1] == TAG_SEQUENCE:
        return SEQUENCE.decode(data[1:])

    elif data[0:1] == TAG_SET:
        return SET.decode(data[1:])
    else:
        raise ValueError('Invalid tag')