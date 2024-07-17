import hashlib


def get_hash_key(s: str) -> str:
    """
    建字符串转成 md5 hash
    :param s:
    :return:
    """
    return get_md5_str(s)


def get_md5_str(s: str) -> str:
    """
    将字符串编码并进行 MD5 加密
    :param s:
    :return:
    """
    hash_object = hashlib.md5(s.encode())
    return hash_object.hexdigest()
