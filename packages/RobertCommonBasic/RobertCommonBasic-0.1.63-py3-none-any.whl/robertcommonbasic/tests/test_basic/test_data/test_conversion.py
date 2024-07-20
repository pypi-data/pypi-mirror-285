
from robertcommonbasic.basic.data.conversion import convert_value, convert_bytes_to_values, convert_values_to_bytes, TypeFormat, DataFormat, reverse_bytes, get_bool, set_bool


def format_bytes(data: bytes) -> str:
    return ''.join(["%02X" % x for x in data]).strip()


def test_long_ver():
    values = [52501, 1883]       # CDAB
    bytes = convert_values_to_bytes(values, TypeFormat.UINT16)
    print(format_bytes(bytes))
    #bytes = reverse_bytes(bytes, len(bytes), 0, DataFormat.ABCD)
    print(reverse_bytes(bytes, len(bytes), 0, DataFormat.BADC))
    bytes = reverse_bytes(bytes, len(bytes), 0, DataFormat.ABCD)
    print(format_bytes(bytes))
    v = convert_bytes_to_values(bytes, TypeFormat.INT32, 0)
    print(v)


def test_bool():
    value = 0
    print(get_bool(value, 0))
    value = set_bool(value, 1, 1)
    print(value)
    print(get_bool(value, 0))
    print(get_bool(value, 1))


def test_convert():
    print(convert_value(1067282596, TypeFormat.INT64, TypeFormat.FLOAT, DataFormat.ABCD))


test_convert()