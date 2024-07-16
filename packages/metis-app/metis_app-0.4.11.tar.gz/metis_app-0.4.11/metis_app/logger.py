import json
from typing import Dict, Union, Any, Callable
from pino import pino
import time

from .tracer import Tracer
from . import json_util
from .observable import Observer


class PowerToolsLoggerWrapper:

    def __init__(self, lgr):
        self.logger = lgr

    def info(self, meta, msg):
        self.logger.info(msg, **meta.get('ctx', {}))


def info(msg: str,
         ctx: dict | None = None,
         tracer: Tracer | None = None,
         status: str = 'ok',
         **kwargs) -> None:
    _log('info',
         msg,
         tracer,
         status,
         ctx if ctx else {},
         **kwargs)


def _log(level: str,
         msg: str,
         tracer: Any,
         status: str,
         ctx: dict[str, str],
         **kwargs) -> None:
    if level not in level_functions.keys():
        return
    level_functions.get(level, info)(logger(), msg, meta(tracer, status, ctx, **kwargs))


def with_perf_log(perf_log_type: str = None, name: str = None):
    """
    Decorator which wraps the fn in a timer and writes a performance log
    """

    def inner(fn):
        def invoke(*args, **kwargs):
            t1 = time.time()
            result = fn(*args, **kwargs)
            t2 = time.time()
            if perf_log_type == 'http' and 'name' in kwargs:
                fn_name = kwargs['name']
            else:
                fn_name = name or fn.__name__
            perf_log(fn=fn_name, delta_t=(t2 - t1) * 1000.0)
            return result

        return invoke

    return inner


def log_decorator(fn):
    def log_writer(*args, **kwargs):
        _log(
            level='info',
            msg='Handling Command {fn}'.format(fn=fn.__name__),
            ctx=args[0].event,
            tracer=args[0].tracer
        )
        return fn(*args, **kwargs)

    return log_writer


def custom_pino_dump_fn(json_log):
    return json.dumps(json_log, cls=json_util.CustomLogEncoder)


def logger():
    if Observer().is_configured:
        return PowerToolsLoggerWrapper(lgr=Observer().logger)
    return pino(bindings={"apptype": "prototype", "context": "main"}, dump_function=custom_pino_dump_fn)


def _info(lgr, msg: str, meta: Dict) -> None:
    lgr.info(meta, msg)


def perf_log(fn: str, delta_t: float, callback: Callable = None):
    if callback:
        callback(fn, delta_t)
    info("PerfLog", ctx={'fn': fn, 'delta_t': delta_t})


def meta(tracer, status: str | int, ctx: dict, **kwargs):
    return {**trace_meta(tracer),
            **{'ctx': ctx},
            **{'status': status},
            **kwargs}


def trace_meta(tracer):
    return tracer.serialise() if tracer else {}


level_functions = {'info': _info}
