import logging.config
import numbers
from functools import wraps


class LogIndetation:
    """Indent logs when we enter a new function"""

    current_indentation = 0

    @classmethod
    def increase_indentation(cls):
        cls.current_indentation += 1

    @classmethod
    def decrease_indentation(cls):
        cls.current_indentation -= 1

    @classmethod
    def get_indentation(cls):
        return "    " * cls.current_indentation


def log(func):
    """Create a log decorator
    When this decorator is applied to a method, it will display in the logs :
    - the input
    - the output
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)

        LogIndetation.increase_indentation()
        indentation = LogIndetation.get_indentation()

        class_name = args[0].__class__.__name__ if args else ""
        method_name = func.__name__
        args_list = list(
            [str(arg) if not isinstance(arg, numbers.Number) else arg for arg in args[1:]]
            + list(kwargs.values())
        )

        param_names = func.__code__.co_varnames[1 : func.__code__.co_argcount]  # noqa
        for i, v in enumerate(param_names):
            if v in ["password", "passwd", "pwd", "pass", "mot_de_passe", "mdp"]:
                args_list[i] = "*****"

        args_list = tuple(args_list)

        logger.info(f"{indentation}{class_name}.{method_name}{args_list} - DEBUT")
        result = func(*args, **kwargs)
        logger.info(f"{indentation}{class_name}.{method_name}{args_list} - FIN")

        if isinstance(result, list):
            result_str = str([str(item) for item in result[:3]])
            result_str += " ... (" + str(len(result)) + " elements)"
        elif isinstance(result, dict):
            result_str = [(str(k), str(v)) for k, v in result.items()][:3]
            result_str += " ... (" + str(len(result)) + " elements)"
        elif isinstance(result, str) and len(result) > 50:
            result_str = result[:50]
            result_str += " ... (" + str(len(result)) + " caracteres)"
        else:
            result_str = str(result)

        logger.info(f"{indentation}   └─> Sortie : {result_str}")

        LogIndetation.decrease_indentation()

        return result

    return wrapper
