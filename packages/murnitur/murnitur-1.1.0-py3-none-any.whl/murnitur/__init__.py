import os
from .main import (
    load_preset,
    format_prompt,
    init,
    set_api_key,
    get_api_key,
    tracer,
    trace,
    log,
    Environment,
)
from .guard.main import Guard


os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
