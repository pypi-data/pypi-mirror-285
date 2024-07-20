from robertcommonbasic.basic.re.utils import format_name, find_match, contain_match, search_match
from robertcommonbasic.basic.dt.utils import parse_time


def test():
    name = 'Bldg3_Area1_hourly_SiteId_08-14-2021-23_00_00_PM_EDT.zip'
    time = format_name(name, r'[^0-9]+', '')
    tm = parse_time(time)
    print(tm)


def get_expression_points(expression: str, pattern: str = r'<%(.*?)%>') -> list:
    return find_match(expression, pattern)


#points = get_expression_points('if <%Bucket Brigade.Real4%> and <%Bucket@Brigade_Real5%>')
#points = get_expression_points('<%Bucket Brigade.Real4%>')
import re


print(re.search('(?P<asctime>.*?)\((?P<lineno>.*?)\)', 'iot_base.py(101)').groupdict())
print(find_match(' power(W)', r'.*?\(.*?\)'))
print(re.sub(r'\(.*?[^)]\)', '', ' power(Wh)'))

print(re.sub(r'\([^)]\)', '', ' power'))
print(find_match(' power(W)', r'.*?\(.*?\)'))
print(find_match(' power', r'.*?\(.*?\)'))

#print(re.search(r'[(?P<asctime>.*?)] level: [(?P<level>.*?)] module: [(?P<module>.*?)] func: [(?P<func>.*?)] lineno: [(?P<lineno>.*?)] msg: [(?P<msg>.*)]', '[2023-11-02 14:33:16] level: [INFO ] module: [run.py] func: [init_license] lineno: [91] msg: [========== GateWayCore V1.0.31 20231030 ==========]'))
print(re.search(r'\[(?P<asctime>.*?)] level: \[(?P<level>.*?)] module: \[(?P<module>.*?)] func: \[(?P<func>.*?)] lineno: \[(?P<lineno>.*?)] msg: \[(?P<msg>.*)]', r'[2023-11-02 14:33:16] level: [INFO ] module: [run.py] func: [init_license] lineno: [91] msg: [========== GateWayCore V1.0.31 20231030 ==========]').groupdict())



print(contain_match('Keypad Medical Alarm Closing1, Area: {area}, Point: {param1}', r'Closing|Restor|Cancel'))
print(contain_match('Alarm, Area: {area}, Point: {param1}', r'.*?Alarm.*?Area.*?Point.*?'))
print(contain_match('    日期\t名称', r'[\u4e00-\u9fa5]'))
print(re.compile(r'[\u4e00-\u9fa5]').search('    日期\t名称'))
print(find_match('bit(v,1)', r'bit\(v,(.*?)\)'))

