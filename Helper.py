from _sha1 import sha1
from collections import defaultdict
class Helper:
    def __init__(self):
        pass

    def init_routingtable(self, id: bytes):
        nodes = {"id": sha1("some_id1".encode("utf-8")).digest()[:2],
                 "ip": "some_ip1"},\
                {"id": sha1("some_id3".encode("utf-8")).digest()[:2],
                 "ip": "some_ip2"},\
                {"id": sha1("some_id2".encode("utf-8")).digest()[:2],
                 "ip": "some_ip3"}
        res = defaultdict(list)
        for item in nodes:
            res[self.xor(item["id"], id)].append(item)
        return res

    def xor(self, a: bytes, b: bytes):
        raw = bytes(x ^ y for x, y in zip(a, b))
        return int.from_bytes(raw, byteorder="big")