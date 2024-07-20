
from typing import Optional, Any
from ..data.utils import SimpleEval, DEFAULT_FUNCTIONS, is_number, remove_exponent_str, Decimal
from ..re.utils import find_match


class SystemAPIFunc:
    """系统API"""

    def __init__(self, value_decimal: Optional[int] = 2, **kwargs):
        self.kwargs = kwargs
        self.value_decimal = value_decimal
        self.s_e = SimpleEval()
        self.s_e.functions = DEFAULT_FUNCTIONS.copy()

    @staticmethod
    def get_points(expression: str, pattern: str = r'<%(.*?)%>') -> list:
        return find_match(expression, pattern)

    def is_expression(self, content: str):
        try:
            self.s_e.eval(content)
            return True
        except Exception as e:
            return False

    def calculate_excel_expression(self, expression: str):
        """处理当报表单元格中含有#时，eval函数返回结果只留数字的情况"""
        if expression.find('#') >= 0:
            return True, expression, ''

        try:
            return True, float(self.s_e.eval(expression)), ''
        except Exception as e:
            return False, expression, e.__str__()

    def convert_value(self, value: Any):
        is_value_num, value = is_number(str(value))
        if is_value_num is True:
            if -Decimal(str(value)).as_tuple().exponent > self.value_decimal:
                _format = f"%.{self.value_decimal}f"
                value = _format % value  # 格式化小数点
            return remove_exponent_str(str(value))
        return value

    def execute_expression(self, expression: str, values: dict):
        """执行表达式"""

        # 获取点名
        names = self.get_points(expression)
        expression_new = expression.strip().replace('<%', '').replace('%>', '')

        vs = {}
        for name in names:
            vs[name] = values.get(name)

        # 替换表达式
        for k, v in vs.items():
            expression_new = expression_new.replace(k, str(self.convert_value(v)))

        result = None
        try:
            if vs is None or (isinstance(vs, dict) and len(vs) > 0):
                result = self.s_e.eval(expression_new)
            else:
                return result
        except Exception as e:
            return result

        if isinstance(result, bool):
            result = int(result)
        elif isinstance(result, float):
            result = round(result, self.value_decimal)
        return result
