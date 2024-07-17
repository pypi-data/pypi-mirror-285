import hashlib


class WUtil(object):

    def __init__(self, times=1):
        self.__times = times

    def do_encrypt(self, param):
        result = None
        try:
            for _ in range(self.__times):
                param = hashlib.md5(param.encode()).hexdigest()
                result = param
        except:
            pass
        finally:
            return result

    def do_encrypt_nt(self, param):
        result = None
        try:
            hash_object = hashlib.md5(param.encode())
            for _ in range(self.__times):
                hash_object = hashlib.md5(hash_object.digest())
            result = hash_object.hexdigest()
        except:
            pass
        finally:
            return result


if __name__ == "__main__":
    wutil = WUtil(8)
    print(wutil.do_encrypt(""))