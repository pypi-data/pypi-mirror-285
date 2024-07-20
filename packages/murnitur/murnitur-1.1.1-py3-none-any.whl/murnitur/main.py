import os
import re
import json
import openlit as lit
from openlit.__helpers import handle_exception
from murnitur.instrumentation.astradb import AstraDBInstrumentor
from contextlib import contextmanager
from functools import wraps
from enum import Enum
from typing import List, Dict, Literal, Optional, TypedDict
from openlit.otel.tracing import trace as t
from openlit.otel.tracing import TracerProvider
from openlit.semcov import SemanticConvetion
from opentelemetry.trace import SpanKind, Status, StatusCode, Span
from .tracer import setup_tracing
from .util import Util


class GuardConfig(TypedDict):
    murnitur_key: str
    provider: Literal["openai", "groq", "anthropic", "custom"]
    model: str
    group: Optional[str]
    api_key: Optional[str]
    base_url: Optional[str]
    headers: Optional[dict]


class Config:
    environment: str
    app_name: str
    api_key: str = ""


_all_instruments = [
    "openai",
    "anthropic",
    "cohere",
    "mistral",
    "bedrock",
    "vertexai",
    "groq",
    "ollama",
    "gpt4all",
    "langchain",
    "llama_index",
    "haystack",
    "embedchain",
    "chroma",
    "pinecone",
    "astradb",
    "qdrant",
    "milvus",
    "transformers",
]

InstrumentLiteral = Literal[
    "openai",
    "anthropic",
    "cohere",
    "mistral",
    "bedrock",
    "vertexai",
    "groq",
    "ollama",
    "gpt4all",
    "langchain",
    "llama_index",
    "haystack",
    "embedchain",
    "chroma",
    "pinecone",
    "astradb",
    "qdrant",
    "milvus",
    "transformers",
]


class Prompt:
    messages = []
    id: str = ""
    name: str = ""
    version: str = ""

    def __init__(self, id: str, name: str, version: str, messages: List) -> None:
        self.id = id
        self.name = name
        self.messages = messages
        self.version = version


class Preset:
    active_version: Prompt = None
    versions: List[Prompt] = []

    def __init__(self, preset):
        active = preset["PresetPrompts"][0]
        self.active_version = Prompt(
            id=active["id"],
            name=active["name"],
            version=active["version"],
            messages=active["prompts"],
        )
        self.versions = [
            Prompt(
                id=curr["id"],
                name=curr["name"],
                version=curr["version"],
                messages=curr["prompts"],
            )
            for curr in preset["PresetPrompts"]
        ]

    def get_prompt_by_version(self, version: int):
        """Get prompt by it's version"""
        for p in self.versions:
            if int(p.version) == int(version):
                return p

    def get_prompt_by_name(self, name: str):
        """Get prompt by it's name"""
        for p in self.versions:
            if p.name == name:
                return p


class Environment(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    STAGING = "staging"


class TracedSpan:
    def __init__(self, span):
        self._span: Span = span

    def log(self, name: str, payload: Dict):
        if self._span.is_recording():
            __trace = t.get_tracer_provider()
            with __trace.get_tracer(__name__).start_span(
                name=name,
                kind=SpanKind.CLIENT,
            ) as child:
                child.set_attribute("type", "log")
                child.set_attribute("log-data", json.dumps(payload, indent=4))

    def __shield__(self, rules: list, rule: any, triggered: bool, response: str):
        if self._span.is_recording():
            __trace = t.get_tracer_provider()
            with __trace.get_tracer(__name__).start_span(
                name="Murnitur Shield",
                kind=SpanKind.CLIENT,
            ) as child:
                child.set_attribute("type", "shield")
                child.set_attribute("rules", json.dumps(rules, indent=2))
                child.set_attribute("rule", json.dumps(rule, indent=2))
                child.set_attribute("triggered", triggered)
                child.set_attribute("response", str(response))

    def set_result(self, result):
        self._span.set_attribute(SemanticConvetion.GEN_AI_CONTENT_COMPLETION, result)

    def set_metadata(self, metadata: Dict):
        self._span.set_attributes(attributes=metadata)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._span.end()


@contextmanager
def tracer(name: str):
    __trace = t.get_tracer_provider()
    with __trace.get_tracer(__name__).start_as_current_span(
        name,
        kind=SpanKind.CLIENT,
    ) as span:
        yield TracedSpan(span)


def trace(wrapped):
    """
    Generates a telemetry wrapper for messages to collect metrics.
    """

    @wraps(wrapped)
    def wrapper(*args, **kwargs):
        __trace = t.get_tracer_provider()
        with __trace.get_tracer(__name__).start_as_current_span(
            name=wrapped.__name__,
            kind=SpanKind.CLIENT,
        ) as span:
            try:
                response = wrapped(*args, **kwargs)
                span.set_attribute(
                    SemanticConvetion.GEN_AI_CONTENT_COMPLETION, response or ""
                )
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                response = None
                handle_exception(span, e)
                lit.logging.error(f"Error in {wrapped.__name__}: {e}", exc_info=True)

            # Adding function arguments as metadata
            try:
                span.set_attribute("function.args", str(args))
                span.set_attribute("function.kwargs", str(kwargs))
                span.set_attribute(
                    SemanticConvetion.GEN_AI_APPLICATION_NAME, Config.app_name
                )
                span.set_attribute(
                    SemanticConvetion.GEN_AI_ENVIRONMENT, Config.environment
                )
            except Exception as meta_exception:
                lit.logging.error(
                    f"Failed to set metadata for {wrapped.__name__}: {meta_exception}",
                    exc_info=True,
                )
                handle_exception(span, e)

            return response

    return wrapper


def log(name: str, payload: Dict):
    __trace = t.get_tracer_provider()
    with __trace.get_tracer(__name__).start_span(
        name=name,
        kind=SpanKind.CLIENT,
    ) as child:
        child.set_attribute("type", "log")
        child.set_attribute("log-data", json.dumps(payload, indent=4))


def set_api_key(api_key: str):
    Config.api_key = api_key
    os.environ["MURNITUR_API_KEY"] = api_key


def get_api_key():
    return Config.api_key


def load_preset(name):
    _, content = Util().get_preset(
        name=name, api_key=os.getenv("MURNITUR_API_KEY", Config.api_key)
    )
    if content:
        return Preset(content)
    return None


def format_prompt(messages: List, params: Dict):
    def replace_match(match):
        variable_name = match.group(1)
        return str(params.get(variable_name, f"{{{{{variable_name}}}}}"))

    replaced_templates = []
    for template in messages:
        new_template = {}
        for key, value in template.items():
            if isinstance(value, str):
                new_value = re.sub(r"\{\{([\w-]+)\}\}", replace_match, value)
                new_template[key] = new_value
            else:
                new_template[key] = value
        replaced_templates.append(new_template)

    return replaced_templates


def init(
    project_name: str,
    environment: Environment = Environment.DEVELOPMENT,
    enabled_instruments: List[InstrumentLiteral] = [],
):
    tracer_provider = t.get_tracer_provider()
    if isinstance(tracer_provider, TracerProvider):
        return
    if os.getenv("MURNITUR_API_KEY"):
        set_api_key(os.getenv("MURNITUR_API_KEY"))

    if not Config.api_key:
        raise ValueError("Please provide a valid API key!")

    Config.app_name = project_name
    Config.environment = environment.value

    __init(
        project_name=project_name,
        environment=environment,
        enabled_instruments=enabled_instruments,
    )


def __init(
    project_name: str,
    environment: Environment,
    enabled_instruments: List[InstrumentLiteral],
):
    try:
        if enabled_instruments:
            disabled_instruments = [
                instr
                for instr in _all_instruments
                if instr not in enabled_instruments and instr != "astradb"
            ]
        else:
            disabled_instruments = []
        # Setup tracer
        tracer = setup_tracing(
            application_name=project_name,
            environment=environment.value,
            otlp_headers=f"x-murnix-trace-token={Config.api_key}",
            disable_batch=False,
            tracer=None,
        )

        lit.init(
            environment=environment.value,
            application_name=project_name,
            disable_metrics=True,
            tracer=tracer,
            disable_batch=False,
            disabled_instrumentors=disabled_instruments,
        )

        if "astradb" in enabled_instruments or not enabled_instruments:
            # instrument astraDB
            AstraDBInstrumentor().instrument(
                environment=environment.value,
                application_name=project_name,
                tracer=tracer,
                pricing_info=None,
                trace_content=True,
                metrics_dict=None,
                disable_metrics=True,
            )
    except Exception as e:
        lit.logging.error("Error during Murnitur initialization: %s", e)
