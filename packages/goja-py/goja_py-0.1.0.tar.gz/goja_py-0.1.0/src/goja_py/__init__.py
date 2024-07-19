import json

import goja_py_runtime as runtime


class GojaRuntimeError(RuntimeError):
    pass


def execute(code: str) -> dict:
    result = runtime.execute(code)
    try:
        result = json.loads(result)
        if isinstance(result, dict) and '___error___' in result:
            raise GojaRuntimeError(result['___error___'])

    except json.JSONDecodeError:
        raise GojaRuntimeError(f'Unable to decode runtime response {result}')

    return result


__all__ = ['execute']
