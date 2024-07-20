import re
import sys
import time
from robertcommonbasic.basic.cls.utils import function_thread
from robertcommonbasic.basic.data.utils import format_value, revert_exp, chunk_list, SimpleEval, DEFAULT_FUNCTIONS, format_value, generate_object_id


def test_format_value():

    print(f"format_value('1.234', '1') = {format_value('1.234', '1')}")
    print(f"format_value('1.234', '-2.0') = {format_value('1.234', '-2.0')}")
    print(f"format_value('-1.234', '2.0') = {format_value('-1.234', '2.0')}")
    print(f"format_value('-1.234', 'v*3') = {format_value('-1.234', 'v*3')}")
    print(f"format_value('测试', '1') = {format_value('测试', '1')}")
    print(f"format_value('测试', '1.2') = {format_value('测试', '1.2')}")
    print(f"format_value('1.234', '') = {format_value('1.234', '')}")

    print(f"format_value('1.234', 'int(v)') = {format_value('1.234', 'int(v)')}")
    print(f"format_value('1.234', 'int(v)') = {format_value('1.234', 'int(v)')}")
    print(f"format_value('2, 'bit(v, 1)') = {format_value('2', 'bit(v, 1)')}")   #取位操作
    print(f"format_value('35535, 'signed(v)') = {format_value('35535', 'signed(v)')}")  # 取位操作
    print(f"format_value('1.234', '1 if v == 20.1234 else 0') = {format_value('1.234', '1 if v == 1.234 else 0')}")

    print()


def test_format_value11():
    print(format_value('nan', 3))
    print(format_value(7, 'divmod(v,2)'))
    print(format_value(7, 'pow(v,2)'))
    print(format_value('7.123456', 'round(v,2)'))
    print(format_value(2, 'bin(int(v))'))
    print(format_value(-16312, '-v if float(v) < 0 else v'))
    print(f"format_value('inf', '1') = {format_value('inf ', '1')}")
    print(format_value(-16312, 'bit(v,6)'))
    print(f"format_value('181', 'v*0.1') = {format_value([10.0, 10.0, 85.0, 85.0, 10.0, 10.0, -20.0, -20.0, -20.0, -20.0], '_in(v,1)')}")
    print(f"format_value('49159', 'bit(v,1)') = {format_value(49159, 'bit(v,1)')}")
    print(f"format_value([20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], '_in(v,2)') = {format_value([20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], '_in(v,2)')}")
    print(f"format_value('181', 'v*0.1') = {format_value('181', 'v*0.1')}")
    print(f"format_value('181', 'v*0.01') = {format_value('181', 'v*0.01')}")
    print(f"format_value('181', '1') = {format_value('181', '1')}")
    print(f"format_value('181', '测试') = {format_value('181', '测试')}")

    print(f"format_value('1.234', '1 if v == 20.1234 else 0') = {format_value('1.234', '1 if v == 20.1234 else 0')}")
    print(f"format_value('测试', '1 if True else 0') = {format_value('测试', '1 if True else 0')}")
    print(f"format_value('测试', '1.2') = {format_value('测试', '1.2')}")
    print(f"format_value('测试', 'v*0.1') = {format_value('测试', 'v*0.1')}")


def test_format_value_thread():

    while True:
        test_format_value()
        time.sleep(0.1)


def test_format_value_threads():
    function_thread(test_format_value_thread, True).start()

    while True:
        test_format_value()
        time.sleep(0.1)


def test_format_value1():

    #print(f"format_value('1.234', '1') = {format_value('1.234', '1')}")
    print(f"format_value('1.234', '1', revert=True) = {format_value('1.234', '1', revert=True)}")

    #print(f"format_value('4', 'v*3') = {format_value('4', 'v*3')}")
    print(f"format_value('12', 'v*3', revert=True) = {format_value('12', 'v*3', revert=True)}")

    #print(f"format_value('1.234', 'int(v)') = {format_value('1.234', 'int(v)')}")
    print(f"format_value('1.234', 'int(v)', revert=True) = {format_value('1.234', '-v', revert=True)}")

    #print(f"format_value('2, 'bit(v, 1)') = {format_value('2', 'bit(v, 1)')}")   #取位操作
    print(f"format_value('2, 'bit(v, 1)', revert=True) = {format_value('2', 'bit(v, 1)', revert=True)}")  # 取位操作

    #print(f"format_value('1.234', '1 if v == 20.1234 else 0') = {format_value('1.234', '1 if v == 1.234 else 0')}")
    print(f"format_value('1.234', '1 if v == 20.1234 else 0', revert=True) = {format_value('1.234', '1 if v == 1.234 else 0', revert=True)}")

    print()


def test_format_value2():
    print(format_value('5.0', '1 if v == 5 else 0'))
    print(format_value('2', '_or(bit(v, 1), bit(v, 0), _and(bit(v, 0),bit(v, 1)))'))


def test_float_value():
    values = ['123456789.0', '-123456789.0', '9.0', '9.1', '9.12334567', '-9.0', '-9.12300000', '-0.00000567', '-0.000005670001000']
    for value in values:
        print(f"{value} {format_value(value, '1', 7)}")
    print()


def test_format_value3():
    a = format_value('255', 'bit(v, 0)*2+bit(v, 1)')
    print(format_value('255', 'bit(v, 0)'))
    print(format_value('255', 'bit(v, 1)'))
    print(format_value('255', 'bit(v, 2)'))
    print(format_value('2', '_or(bit(v, 1), bit(v, 0), _and(bit(v, 0),bit(v, 1)))'))


def test_format_value31():
    a = format_value(str(int(8)), 'bit(v, 0)*2**0+bit(v, 1)*2**1+bit(v, 3)*2**3')
    print(format_value('255', 'bit(v, 0)'))
    print(format_value('255', 'bit(v, 1)'))
    print(format_value('255', 'bit(v, 2)'))
    print(format_value(str(int(0x7B)), '_or(bit(v, 1), bit(v, 0), _and(bit(v, 0),bit(v, 1)))'))

    datas = bytes([0x7B])
    freq_ant = int(format_value(str(int(datas[0])), 'bit(v, 0)') + format_value(str(int(datas[0])), 'bit(v, 1)'))
    print(freq_ant)


def test_nvn_value():
    result = format_value('952', '(max(4, v*3.3*1000/(4095*150))-4)/16*100', 2)
    print('{:g}'.format(6.96))
    print(format_value('2', '(max(4, v*3.3*1000/(4095*150))-4)/16*100', 3))


def test_conver():
    result = format_value('-1.234', 'v*10/10-1')
    result1 = format_value(str(result), 'v*10/10-1', revert=True)

    result = format_value('952', '(max(4, v*3.3*1000/(4095*150))-4)/16*100', 3)
    print(format_value(str(result), '(max(4, v*3.3*1000/(4095*150))-4)/16*100', 3))
    print()


def test_chunk_list():
    datas = ['1', '2', '3', '4', '5', '6', '7']
    aa = chunk_list(datas, 3)
    ab = list(aa)
    print(len(ab))


def test_large():
    result = format_value('0.1', '0.15 if v>5 else v', 2)
    print(result)
    print(format_value('2', '(max(4, v*3.3*1000/(4095*150))-4)/16*100', 3))


def test_express():
    try:
        expression = 'Bucket Brigade Real4 > 0'
        vs = {'Bucket Brigade Real4': 2}
        return SimpleEval(None, DEFAULT_FUNCTIONS.copy(), vs).eval(expression)
    except Exception as e:
        return None


def test_format_value21():
    #print(format_value('-32768', '"GW_NONE" if v < 0 else 1 if 0 <= v < 2000 else 1'))
    #print(format_value('-1', 'None if v < 0 else 1 if 0 <= v < 2000 else 0'))
    #print(format_value('2500', 'None if v < 0 else 1 if 0 <= v < 2000 else 0'))
    #print(format_value('Open', "1 if v=='Open' else 0"))
    #print(format_value('', "1 if len(v)==0 else 0"))
    #print(format_value('1067282596', 'convert(int(v), 14, 18, 0)[0]'))
    #print(format_value('1067282596', "convert(int(v), 14, 18, 0)[0]"))
    #print(format_value('-32762', 'bit(v,3)'))
    #print(format_value('[0.0, 0.30000001192092896, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]', '_in(v,1)'))
    #format_value('123')
    #format_value('acb')
    #format_value('1.23')
    #format_value(str([False, True, 0.31, 1, 'active']))
    #format_value(str({'abc': '123', 'abc2': False, 'abc1': 'active'}))
    # print(format_value('1+2'))
    #print(format_value(str([False, True, 0.31, 1, 'inactive']), '_in(v,-1)'))
    #print(format_value(str([False, True, 0.31, 1, 'inactive']), '_zero(v,"false|inactive","true|active")'))
    # print(format_value(str([False, True, 0.31, 1, 'inactive']), '_zero(v,1,2)'))
    print(generate_object_id())
    print(format_value('123456781.123', "'GW_NONE' if int(float(str(v))) >= 99999999 else v"))


def test_round():
    print(format_value('1.2345', '_round(v, 2)', 3))
    print(format_value('1.2345', '_round(v, 3)', 3))
    print(format_value('1.2', '_round(v, 2)', 3))
    print(format_value('1.2', '_round(max(v+1,2), 2)', 3))


test_format_value11()