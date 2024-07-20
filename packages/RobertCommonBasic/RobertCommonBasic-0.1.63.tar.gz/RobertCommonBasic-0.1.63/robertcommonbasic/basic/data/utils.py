import logging
import math

import numpy as np
import json
from base64 import b64decode, b64encode
from bson import ObjectId
from struct import pack, unpack
from decimal import Decimal
from simpleeval import SimpleEval, DEFAULT_FUNCTIONS
from typing import Union, Any
from ..re.utils import contain_match
from .conversion import convert_value



def bracket(func, xa=0.0, xb=1.0, args=(), grow_limit=110.0, maxiter=1000):
    _gold = 1.618034  # golden ratio: (1.0+sqrt(5.0))/2.0
    _verysmall_num = 1e-21
    fa = func(*(xa,) + args)
    fb = func(*(xb,) + args)
    if fa < fb:                      # Switch so fa > fb
        xa, xb = xb, xa
        fa, fb = fb, fa
    xc = xb + _gold * (xb - xa)
    fc = func(*((xc,) + args))
    funcalls = 3
    iter = 0
    while fc < fb:
        tmp1 = (xb - xa) * (fb - fc)
        tmp2 = (xb - xc) * (fb - fa)
        val = tmp2 - tmp1
        if np.abs(val) < _verysmall_num:
            denom = 2.0 * _verysmall_num
        else:
            denom = 2.0 * val
        w = xb - ((xb - xc) * tmp2 - (xb - xa) * tmp1) / denom
        wlim = xb + grow_limit * (xc - xb)
        if iter > maxiter:
            raise RuntimeError("Too many iterations.")
        iter += 1
        if (w - xc) * (xb - w) > 0.0:
            fw = func(*((w,) + args))
            funcalls += 1
            if fw < fc:
                xa = xb
                xb = w
                fa = fb
                fb = fw
                return xa, xb, xc, fa, fb, fc, funcalls
            elif fw > fb:
                xc = w
                fc = fw
                return xa, xb, xc, fa, fb, fc, funcalls
            w = xc + _gold * (xc - xb)
            fw = func(*((w,) + args))
            funcalls += 1
        elif (w - wlim)*(wlim - xc) >= 0.0:
            w = wlim
            fw = func(*((w,) + args))
            funcalls += 1
        elif (w - wlim)*(xc - w) > 0.0:
            fw = func(*((w,) + args))
            funcalls += 1
            if fw < fc:
                xb = xc
                xc = w
                w = xc + _gold * (xc - xb)
                fb = fc
                fc = fw
                fw = func(*((w,) + args))
                funcalls += 1
        else:
            w = xc + _gold * (xc - xb)
            fw = func(*((w,) + args))
            funcalls += 1
        xa = xb
        xb = xc
        xc = w
        fa = fb
        fb = fc
        fc = fw
    return xa, xb, xc, fa, fb, fc, funcalls


class Brent:

    def __init__(self, func, args=(), tol=1.48e-8, maxiter=500):
        self.func = func
        self.args = args
        self.tol = tol
        self.maxiter = maxiter
        self._mintol = 1.0e-11
        self._cg = 0.3819660
        self.xmin = None
        self.fval = None
        self.iter = 0
        self.funcalls = 0

    def set_bracket(self, brack=None):
        self.brack = brack

    def get_bracket_info(self):
        func = self.func
        args = self.args
        brack = self.brack
        if brack is None:
            xa, xb, xc, fa, fb, fc, funcalls = bracket(func, args=args)
        elif len(brack) == 2:
            xa, xb, xc, fa, fb, fc, funcalls = bracket(func, xa=brack[0], xb=brack[1], args=args)
        elif len(brack) == 3:
            xa, xb, xc = brack
            if xa > xc:
                xc, xa = xa, xc
            if not ((xa < xb) and (xb < xc)):
                raise ValueError("Bracketing values (xa, xb, xc) do not fulfill this requirement: (xa < xb) and (xb < xc)")
            fa = func(*((xa,) + args))
            fb = func(*((xb,) + args))
            fc = func(*((xc,) + args))
            if not ((fb < fa) and (fb < fc)):
                raise ValueError("Bracketing values (xa, xb, xc) do not fulfill this requirement: (f(xb) < f(xa)) and (f(xb) < f(xc))")
            funcalls = 3
        else:
            raise ValueError("Bracketing interval must be length 2 or 3 sequence.")
        return xa, xb, xc, fa, fb, fc, funcalls

    def optimize(self):
        func = self.func
        xa, xb, xc, fa, fb, fc, funcalls = self.get_bracket_info()
        _mintol = self._mintol
        _cg = self._cg
        x = w = v = xb
        fw = fv = fx = fb
        if (xa < xc):
            a = xa
            b = xc
        else:
            a = xc
            b = xa
        deltax = 0.0
        iter = 0
        rat = 0
        while iter < self.maxiter:
            tol1 = self.tol * np.abs(x) + _mintol
            tol2 = 2.0 * tol1
            xmid = 0.5 * (a + b)
            if np.abs(x - xmid) < (tol2 - 0.5 * (b - a)):
                break
            if np.abs(deltax) <= tol1:
                if x >= xmid:
                    deltax = a - x
                else:
                    deltax = b - x
                rat = _cg * deltax
            else:
                tmp1 = (x - w) * (fx - fv)
                tmp2 = (x - v) * (fx - fw)
                p = (x - v) * tmp2 - (x - w) * tmp1
                tmp2 = 2.0 * (tmp2 - tmp1)
                if tmp2 > 0.0:
                    p = -p
                tmp2 = np.abs(tmp2)
                dx_temp = deltax
                deltax = rat
                if (p > tmp2 * (a - x)) and (p < tmp2 * (b - x)) and (np.abs(p) < np.abs(0.5 * tmp2 * dx_temp)):
                    rat = p * 1.0 / tmp2
                    u = x + rat
                    if (u - a) < tol2 or (b - u) < tol2:
                        if xmid - x >= 0:
                            rat = tol1
                        else:
                            rat = -tol1
                else:
                    if x >= xmid:
                        deltax = a - x
                    else:
                        deltax = b - x
                    rat = _cg * deltax

            if np.abs(rat) < tol1:
                if rat >= 0:
                    u = x + tol1
                else:
                    u = x - tol1
            else:
                u = x + rat
            fu = func(*((u,) + self.args))
            funcalls += 1

            if fu > fx:
                if u < x:
                    a = u
                else:
                    b = u
                if (fu <= fw) or (w == x):
                    v = w
                    w = u
                    fv = fw
                    fw = fu
                elif (fu <= fv) or (v == x) or (v == w):
                    v = u
                    fv = fu
            else:
                if u >= x:
                    a = x
                else:
                    b = x
                v = w
                w = x
                x = u
                fv = fw
                fw = fx
                fx = fu

            iter += 1

        self.xmin = x
        self.fval = fx
        self.iter = iter
        self.funcalls = funcalls

    def get_result(self, full_output=False):
        if full_output:
            return self.xmin, self.fval, self.iter, self.funcalls
        else:
            return self.xmin


def minimize_scalar_brent(func, brack=None, maxiter=500):
    brent = Brent(func=func)
    brent.set_bracket(brack)
    brent.optimize()
    x, fval, nit, nfev = brent.get_result(full_output=True)
    success = nit < maxiter and not (np.isnan(x) or np.isnan(fval))
    if success:
        return x
    else:
        if nit >= maxiter:
            raise Exception(f"Maximum number of iterations exceeded")
        if np.isnan(x) or np.isnan(fval):
            raise Exception(f"NaN result encountered.")
    return x


def base64_encode(datas: bytes) -> str:
    return b64encode(datas).decode()


def base64_decode(datas: str) -> bytes:
    return b64decode(datas)


def chunk_list(values: list, num: int):
    for i in range(0, len(values), num):
        yield values[i: i+num]


# 转换类为字典
def convert_class_to_dict(obeject_class):
    object_value = {}
    for key in dir(obeject_class):
        value = getattr(obeject_class, key)
        if not key.startswith('__') and not key.startswith('_') and not callable(value):
            object_value[key] = value
    return object_value


def generate_object_id():
    return ObjectId().__str__()


def remove_exponent(value: Decimal):
    return value.to_integral() if value == value.to_integral() else value.normalize()


def remove_exponent_str(value: str) -> str:
    dec_value = Decimal(value)
    if dec_value == dec_value.to_integral():    # int
        return str(int(float(value)))
    else:
        return value.rstrip('0')


def is_number(value: str):
    try:
        return True, float(value)
    except ValueError:
        pass
    return False, value


def find_all_pos(scale: str, exp: str):
    return [i for i, c in enumerate(scale) if c == exp]


def revert_exp(scale: str) -> str:
    exps = {'+': ['-', []], '-': ['+', []], '*': ['/', []], '/': ['*', []]}
    for exp in exps.keys():
        exps[exp][1] = find_all_pos(scale, exp)

    _scale = list(scale)
    for exp, [_exp, pos] in exps.items():
        for _pos in pos:
            _scale[_pos:_pos+1] = _exp
    return ''.join(_scale)


def inverse_exp(scale: str, value: str):
    try:
        if not contain_match(scale, r'[^0-9\-+*./%()v ]+'):
            func = lambda v: eval(scale)
            def _inverse(v):
                optimizer = (lambda x, bounded_f=func: (((func(x) - v)) ** 2))
                return minimize_scalar_brent(optimizer, (0, 1))
            return _inverse(float(str(value)))
    except:
        pass
    return value


def replace_value(value: str, replaces: dict = {'on': 1, 'true': 1, 'active': 1, 'off': 0, 'false': 0, 'inactive': 0}):
    """将相应值转换为0,1"""
    try:
        _value = json.loads(value)
        if isinstance(_value, list):
            return str([replaces.get(str(v).lower(), v) for v in _value])
        elif isinstance(_value, dict):
            return str({k: replaces.get(str(v).lower(), v) for k, v in _value.items()})
        return replaces.get(str(_value).lower(), value)
    except Exception as e:
        try:
            _value = eval(value)
            if isinstance(_value, list):
                return str([replaces.get(str(v).lower(), v) for v in _value])
            elif isinstance(_value, dict):
                return str({k: replaces.get(str(v).lower(), v) for k, v in _value.items()})
        except Exception as e:
            return replaces.get(str(value).lower(), value)
    return replaces.get(str(value).lower(), value)


# 自定义
# 取位函数
def bit(value, index: int):
    try:
        value = int(value)
        return value & (1 << index) and 1 or 0
    except Exception:
        pass
    return value


def signed(value):
    try:
        value = int(value)
        return unpack('h', pack('H', value))[0]
    except Exception:
        pass
    return value


def inverse_long(value):
    try:
        value = int(float(value))
        vev_value = unpack('HH', pack('I', value))
        return unpack('I', pack('HH', vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def inverse_float(value):
    try:
        value = float(value)
        vev_value = unpack('HH', pack('f', value))
        return unpack('f', pack('HH', vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def inverse_double(value):
    try:
        value = float(value)
        vev_value = unpack('HHHH', pack('d', value))
        return unpack('d', pack('HHHH', vev_value[3], vev_value[2], vev_value[1], vev_value[0]))[0]
    except Exception:
        pass
    return value


def _and(*args):
    start = 1
    for a in args:
        start = start & a
    return start


def _or(*args):
    start = 0
    for a in args:
        start = start | a
    return start


def _in(value, index: Union[int, str]):
    try:
        if isinstance(index, int):
            return eval(value)[index]
        elif isinstance(index, str):
            return eval(index).get(index, value)
    except Exception:
        pass
    return value


def _zero(value, falses: str, trues: str):
    replaces = {k: 0 for k in falses.lower().split('|')}
    replaces.update({k: 1 for k in trues.lower().split('|')})
    return replace_value(value, replaces)


def _round(value, decimal: int = 2):
    try:
        return round(float(str(value)), decimal)
    except:
        return value


'''
"v+20"  #基础方法 + - * / %  == < > <= >= >> <<
"int(v)" #基础函数 randint rand int float str
"com(v)"   #自定义函数 bit signed inverse_long inverse_float inverse_double
"1 if v == 20.1234 else 0" #表达式
'''

functions = DEFAULT_FUNCTIONS.copy()
functions.update(convert=convert_value, abs=abs, divmod=divmod, pow=pow, round=round, max=max, min=min, sum=sum, _round=_round, _zero=_zero, bit=bit, _in=_in, signed=signed, inverse_long=inverse_long, inverse_float=inverse_float, inverse_double=inverse_double, _and=_and, _or=_or)


def eval_express(value: Any, scale: Any, revert: bool = False, fail_retry: bool = False):
    """计算表达式"""
    value_old = value
    scale_old = scale
    try:
        # 判断值是文本还是数字
        is_value_num, value = is_number(str(value))

        is_scale_num, scale = is_number(str(scale))

        if is_scale_num is True:
            if is_value_num is True:
                value = value * scale
        else:
            if revert is True:
                value = inverse_exp(scale, str(value))
            else:
                value = SimpleEval(names={'v': value}, functions=functions).eval(scale)
    except Exception as e:
        if fail_retry is True:
            return eval_express(value_old, scale_old, revert, False)
        raise Exception(f"invalid scale({e.__str__()})")
    return value


def reset_decimal(value: Any, decimal: int = 2):
    """保留小数点"""
    try:
        is_value_num, value = is_number(str(value))
        if is_value_num is True and math.isnan(value) is False:
            if -Decimal(str(value)).as_tuple().exponent > decimal:
                _format = f"%.{decimal}f"
                value = _format % value
            return remove_exponent_str(str(value))    # 格式化小数点
    except Exception as e:
        logging.error(f"invalid decimal ({value}/{decimal})({e.__str__()})")
    return value


def format_value(value: str, scale: str = '1', decimal: int = 2, revert: bool = False, replaces: dict = {'on': 1, 'true': 1, 'active': 1, 'off': 0, 'false': 0, 'inactive': 0}) -> str:
    value_old = value
    scale_old = scale
    value = str(value_old).strip()
    scale = str(scale_old).strip()
    try:
        if isinstance(value, str) and len(value) > 0:
            # 替换非标字符
            value = replace_value(value, replaces)

            if scale not in ['', '1']:  # 倍率不为空或者1
                value = eval_express(value, scale, revert, True)
    except Exception as e:
        logging.error(f"format_value({value_old} - {scale_old})-({e.__str__()})")
    finally:
        value = reset_decimal(value, decimal)
    return str(value)
