# Copyright (c) 2023 NEC Corporation. All Rights Reserved.

import argparse
from contextlib import contextmanager
import logging
import os
from typing import List

import pandas.errors

import firefw as fire
from firefw import tracing

from fireducks import fireducks_ext

logger = logging.getLogger(__name__)


class EvalOptions:
    """Evaluation options.

    Evaluation options can be changed upon each evaluation.
    """

    def __init__(self, inherit_default=True):
        # TODO: inherit _default_eval_options
        self.compile_options = fireducks_ext.FireDucksCompileOptions()
        self.prohibit_evaluation = False  # For test

        if inherit_default:
            src = get_fireducks_options()._default_eval_options.compile_options
            self.compile_options.target = src.target

    def set_pushdown_pass(self, flag: bool):
        # logger.debug("EvalOptions.set_pushdown_pass: %s", flag)
        self.compile_options.flag_pushdown_pass = flag
        return self


class _FireDucksIRProperty:
    """Global constant IR property.

    IR property is not changed during lifetime of process.

    has_series : bool
      True if IR supports pandas-like series.

    has_metadata: bool
      True if IR supports a metadata.

    NOTE: At the moment, we change IRProperty depending on a backend.
    """

    def __init__(self):
        logger.debug("_FireDucksIRProperty.__init__")
        self.has_metadata = False
        self.has_series = True


def parse_fireducks_flags(flags, namespace=None):
    parser = argparse.ArgumentParser(prog="FIREDUCKS_FLAGS")

    parser.add_argument(
        "--benchmark-mode",
        action="store_true",
        dest="_benchmark_mode",
        help="Enable benchmark mode",
    )

    # Log line number when fallback when True.
    # (efault is False because of non-negligible overhead
    parser.add_argument(
        "--fallback-lineno",
        action="store_true",
        help="Show line number on fallback log",
    )

    # Fast fallback is allowed when True.
    # When it is allowed and other conditions are met, fast fallback is
    # used to minimize fallback overhead by:
    #   - no check if fallback is prohibited
    #   - no logger
    #   - no trace
    #   - no unwrap and wrap
    # Note that other conditions depends on methods and should be checked
    # at fallback site.
    parser.add_argument(
        "--no-fast-fallback",
        action="store_false",
        dest="fast_fallback",
        help="Disable fast fallback",
    )

    parser.add_argument(
        "--trace",
        type=str,
        default=None,
        dest="trace_level",
        help="Enable tracing. 0-3",
    )

    parser.add_argument(
        "--trace-file",
        type=str,
        default="trace.json",
        help="filename to store trace",
    )

    parser.add_argument(
        "-Wfallback",
        action="store_true",
        dest="warn_fallback",
        help="Enable fallback warning and timing",
    )

    parser.add_argument(
        "-t", "--target", default="dfkl", help="Change backend (default: dfkl)"
    )

    parser.add_argument(
        "--pushdown",
        dest="_pushdown",
        choices=["on", "off"],
        help="Enable pushdown pass",
    )

    return parser.parse_known_args(flags.split(" "), namespace)


class _FireDucksOptions:
    """Global and singleton options. Not read-only."""

    def __init__(self):
        self._default_eval_options = EvalOptions(inherit_default=False)
        self.ir_prop = _FireDucksIRProperty()
        self._benchmark_mode = False
        self._configure()

    def _configure(self):
        flags = os.environ.get("FIREDUCKS_FLAGS", "")
        args, unknowns = parse_fireducks_flags(flags, self)

        self._transfer_fireducks_flags_to_compile_options(args, unknowns)

        # FIXME:
        if self._default_eval_options.compile_options.target == "dfkl":
            self.ir_prop.has_series = False
            self.ir_prop.has_metadata = True

        # FIXME: Depends on frovedis
        if self._default_eval_options.compile_options.target == "frovedis":
            import fireducks.frovedis_initialize  # noqa

    def _transfer_fireducks_flags_to_compile_options(self, args, unknowns):
        # parse unknown flags by extension
        options = self._default_eval_options.compile_options
        if fireducks_ext.ParseFireDucksFlags(" ".join(unknowns), options) != 0:
            raise RuntimeError("fireducks flags parse error")

        # transfer known flags
        options.target = self.target

        if args._pushdown is not None:
            self._default_eval_options.set_pushdown_pass(
                args._pushdown == "on"
            )

    @property
    def benchmark_mode(self):
        return self._benchmark_mode

    def set_benchmark_mode(self, flag: bool):
        self._benchmark_mode = flag


_fireducks_options = _FireDucksOptions()


def get_fireducks_options():
    global _fireducks_options
    return _fireducks_options


# for tests.
def _get_default_backend():
    return get_fireducks_options()._default_eval_options.compile_options.target


def get_ir_prop():
    return get_fireducks_options().ir_prop


def set_fireducks_option(key, value):
    opts = get_fireducks_options()
    if key == "fallback-lineno":
        opts.fallback_lineno = value
    elif key == "fast-fallback":
        opts.fast_fallback = value
    elif key == "warn-fallback":
        opts.warn_fallback = value
    else:
        raise RuntimeError(f"unknown or read-only option: {key}")


_context = None


class Context:
    def __init__(self):
        self.ext_context = fireducks_ext.FireDucksContext()
        self.irbuilder = fire.IRBuilder()


def context():
    global _context
    if _context is None:
        _context = Context()
    return _context


def build_op(*args, **kwargs):
    return context().irbuilder.build_op(*args, **kwargs)


def make_available_value(x, ty):
    return context().irbuilder.make_available_value(x, ty)


def make_attr(typ, name, value):
    return context().irbuilder.new_attr(typ, name, value)


# Not well tested. Use only for testing.
@contextmanager
def prohibit_evaluation():
    options = get_fireducks_options()._default_eval_options
    options.prohibit_evaluation = True
    try:
        yield
    finally:
        options.prohibit_evaluation = False


class EvalLogger:
    """Evaluation logger to collect logs during evaluation."""

    def __init__(self):
        self._extLogger = fireducks_ext.ExecutionLogger()

    @property
    def optimized_ir(self):
        return self._extLogger.optimized_ir


def _evaluate(
    values: List[fire.Value], options: EvalOptions = None, evalLogger=None
):
    for value in values:
        logger.debug("evaluate: %s (defined by %s)", value, value.get_def())

    if options is None:
        options = get_fireducks_options()._default_eval_options

    import fireducks.pandas.utils as _utils

    options.compile_options._pd_version_under2 = _utils._pd_version_under2

    if options.prohibit_evaluation:
        raise RuntimeError("evaluation prohibited")

    def wrapper(ir, input_values, output_values):
        fi = fireducks_ext.FunctionInvocation()
        fi.ir = ir
        fi.input_types = [v.mlir_type for v in input_values]
        fi.input_values = [v.get_result() for v in input_values]
        fi.output_types = [v.mlir_type for v in output_values]

        return fireducks_ext.execute(
            context().ext_context,
            options.compile_options,
            fi,
            evalLogger._extLogger if evalLogger is not None else None,
        )

    try:
        return fire.evaluate(values, wrapper, package="fireducks")
    except fireducks_ext.InvalidIndexError as e:
        raise pandas.errors.InvalidIndexError(e)
    except fireducks_ext.MergeError as e:
        raise pandas.errors.MergeError(e)
    except fireducks_ext.NotImplementedError as e:
        raise NotImplementedError(e)
    except fireducks_ext.SpecificationError as e:
        raise pandas.errors.SpecificationError(e)
    except fireducks_ext.OSError as e:
        raise OSError(e)


def evaluate(
    values: List[fire.Value],
    options: EvalOptions = None,
    evalLogger: EvalLogger = None,
):
    with tracing.scope(tracing.Level.DEFAULT, "fireducks.core.evaluate"):
        ret = _evaluate(values, options, evalLogger)
    return ret


def evaluate_ops_depending_on_defs_of(values: List[fire.Value]):
    ops = context().irbuilder.get_ops_with_any_inputs_in(values)
    values = []
    for op in ops:
        values += op.outs
    evaluate(list(set(values)))
