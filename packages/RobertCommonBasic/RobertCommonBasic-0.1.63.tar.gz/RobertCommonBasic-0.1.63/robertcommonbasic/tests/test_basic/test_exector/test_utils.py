import random

from robertcommonbasic.basic.exector.utils import Code


def run():
    src = """
    def fib(n):
        print(f"fib({n})")
        if n == 1 or n == 2:
            return 1
        print(f"fib1({n})")
        return fib(n-1) + fib(n-2)
    return fib(3)
    """
    module = Code(src)
    print(module.run_code())


def run2():
    src = """
    import time
    def fib(n):
        print(f"fib({n})")
        time.sleep(1)
        if n == 1 or n == 2:
            return 1
        print(f"fib1({n})")
        return fib(n-1) + fib(n-2)
    return fib(3)
    """
    module = Code(src, True)
    print(module.run_code())


def run21():
    src = """
    import time
    def fib(n):
        print(f"fib({n})")
        time.sleep(1)
        if n == 1 or n == 2:
            return 1
        print(f"fib1({n})")
        return fib(n-1) + fib(n-2)
    return fib(3)
    """
    module = Code(src, True)
    print(module.run_code())


def run1():
    src = """
def fib(n):
    print(f"fib({n})")
    if n == 1 or n == 2:
        return 1
    print(f"fib1({n})")
    return fib(n-1) + fib(n-2)
    """
    module = Code(src, False)
    print(module.run_code('fib', 2))


def run21():
    src = """
    def get_seniverse(core):
        print(core)
        core.set_debug_log(f"aa")
        return {}
    return get_seniverse(core)
    """
    module = Code(src, True)
    print(module.run_code())


def run_task(task, tools, **kwargs):
    import random
    task.logging(content=f"run task")
    values = tools.get_values('1', ['Bucket Brigade.Int2', 'Bucket Brigade.Real4'])
    task.logging(content=f"get value({values})")
    vs = tools.set_values({'Bucket Brigade.Real4': random.randint(1, 20)})
    task.logging(content=f"set value({vs})")


class ExeTools:

    def __init__(self):
        pass

    def __str__(self):
        return 'abc'

    def set_debug_log(self, content: str):
        print(content)
        return {}

    def run(self):
        code = """
    def get_seniverse(core):
        print(core)
        core.set_debug_log(f"aa")
        return {}
    """
        values = Code(code, False).run_code('get_seniverse', self)
        print(values)

    def run1(self):
        code = """
def fib(n):
    print(f"fib({n})")
    if n == 1 or n == 2:
        return 1
    print(f"fib1({n})")
    return fib(n-1) + fib(n-2)
        """
        values = Code(code, False).run_code('fib', 3)
        print(values)

    def run2(self):
        code = """
def get_seniverse(core):
	values = {}
	try:
		name = weather
		response = HttpTool().send_request(url=f"https://api.seniverse.com/v3/air/now.json?location=beijing&key=SowLtcHC8AvFEO6md&language=zh-Hans&scope=city", method='GET, timeout=30, headers={'content-type': 'application/json'})
		if response.success is True:
			datas = json.loads(response.data)
			if isinstance(datas, dict) and len(datas) > 0:
				results = datas.get('results', [])
				if isinstance(results, list) and len(results) > 0:
					for result in results:
						if isinstance(result, dict):
							now_value = result.get('now', {}) if name == 'weather' else result.get('air', {}).get('city', {})
							values[f"{name}_last_update"] = result.get('last_update', '')
							if isinstance(now_value, dict):
								for k, v in now_value.items():
									values[f"{name}_{k}"] = v
		else:
			raise Exception(f"{response.msg[:200]}")
	except Exception as e:
		print(MyLogRecord(f"{core.name} get {name} fail ({e.__str__()})", MyLogLevel.ERROR).format_msg())
	return values
return get_seniverse(core)
        """
        values = Code(code, False).run_code('get_seniverse', task_func=self, data_func=DataFunc)
        print(values)


content = """
def run_task(task, tools, **kwargs):
    import random
    task.logging(content=f"run task")
    values = tools.get_values('1', ['Bucket Brigade.Int2', 'Bucket Brigade.Real4'])
    task.logging(content=f"get value({values})")
    vs = tools.set_values({'Bucket Brigade.Real4': random.randint(1, 20)})
    task.logging(content=f"set value({vs})")
"""

print(content)

ExeTools().run2()
