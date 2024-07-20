import warnings
import re

# Optionally add telemtry
from ._version import __version__

from murnitur.annotation.evaluation.evaluate import evaluate, assert_test
from murnitur.annotation.evaluation.test_run import on_test_run_end, log_hyperparameters

__all__ = [
    "log_hyperparameters",
    "evaluate",
    "assert_test",
    "on_test_run_end",
]


def compare_versions(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r"(\.0+)*$", "", v).split(".")]

    return normalize(version1) > normalize(version2)
