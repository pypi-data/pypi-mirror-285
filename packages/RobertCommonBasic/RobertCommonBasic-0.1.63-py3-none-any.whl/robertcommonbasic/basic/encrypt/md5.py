import hashlib


def md5_encryption(content: str):
    """md5加密"""
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest()


def md5_verify(content: str, md5_content: str):
    """ md5校验"""
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest() == md5_content
