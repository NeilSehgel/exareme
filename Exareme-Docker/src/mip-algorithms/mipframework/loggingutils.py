import logging
import logging.handlers
import os

from .constants import LOGGING_LEVEL_ALG

LOG_FILENAME = os.path.join(os.path.dirname(__file__), "logs/mip.log")

miplogger = logging.getLogger("miplogger")
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=int(1e7), backupCount=10
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
handler.setFormatter(formatter)
miplogger.setLevel(LOGGING_LEVEL_ALG)
miplogger.addHandler(handler)


def log_this(method, **kwargs):
    if LOGGING_LEVEL_ALG == logging.INFO:
        miplogger.info("Starting: {method}".format(method=method))
    elif LOGGING_LEVEL_ALG == logging.DEBUG:
        arguments = ",".join(["\n{k}={v}".format(k=k, v=v) for k, v in kwargs.items()])
        miplogger.debug(
            "Starting: {method}, "
            "{arguments}".format(method=method, arguments=arguments)
        )


def repr_with_logging(self, **kwargs):
    cls = type(self).__name__
    if LOGGING_LEVEL_ALG == logging.INFO:
        return "{cls}()".format(cls=cls)
    elif LOGGING_LEVEL_ALG == logging.DEBUG:
        arguments = ",".join(["\n{k}={v}".format(k=k, v=v) for k, v in kwargs.items()])
        return "{cls}({arguments})".format(cls=cls, arguments=arguments)


def logged(func):
    def logging_wrapper(*args, **kwargs):
        cls = get_class_name(args)
        if LOGGING_LEVEL_ALG == logging.INFO:
            miplogger.info("Starting: {0}{1}".format(cls, func.__name__))
        elif LOGGING_LEVEL_ALG == logging.DEBUG:
            miplogger.debug(
                "Starting: {0}{1},\nargs: \n{2},\nkwargs: \n{3}".format(
                    cls, func.__name__, args, kwargs
                )
            )
        return func(*args, **kwargs)

    def get_class_name(args):
        if is_classmethod(args[0]):
            cls = args[0].__name__ + "."
        elif is_mipframework_method(args[0]):
            cls = type(args[0]).__name__ + "."
        else:
            cls = ""
        return cls

    logging_wrapper._original = func
    return logging_wrapper


def is_classmethod(arg):
    return type(arg) == type


def is_mipframework_method(arg):
    return (hasattr(arg, "__module__") and "mipframework" in arg.__module__) or (
        hasattr(type(arg), "__base__")
        and "mipframework" in type(arg).__base__.__module__
    )
