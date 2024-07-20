from typing import Collection
import importlib.metadata
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from wrapt import wrap_function_wrapper

from murnitur.instrumentation.astradb.astradb import general_wrap

_instruments = ("astrapy >= 1.3.1",)

WRAPPED_METHODS = [
    {
        "package": "astrapy.db",
        "object": "AstraDB.create_collection",
        "endpoint": "astradb.create_collection",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDB.delete_collection",
        "endpoint": "astradb.delete_collection",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.insert_one",
        "endpoint": "astradb.insert_one",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.insert_many",
        "endpoint": "astradb.insert_many",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.delete_one",
        "endpoint": "astradb.delete_one",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.delete_many",
        "endpoint": "astradb.delete_many",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.update_one",
        "endpoint": "astradb.update_one",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.update_many",
        "endpoint": "astradb.update_many",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.upsert_one",
        "endpoint": "astradb.upsert_one",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.upsert_many",
        "endpoint": "astradb.upsert_many",
        "wrapper": general_wrap,
    },
    {
        "package": "astrapy.db",
        "object": "AstraDBCollection.find",
        "endpoint": "astradb.find",
        "wrapper": general_wrap,
    },
]


class AstraDBInstrumentor(BaseInstrumentor):
    """An instrumentor for AstraDB's client library."""

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        application_name = kwargs.get("application_name")
        environment = kwargs.get("environment")
        tracer = kwargs.get("tracer")
        version = importlib.metadata.version("astrapy")

        for wrapped_method in WRAPPED_METHODS:
            wrap_package = wrapped_method.get("package")
            wrap_object = wrapped_method.get("object")
            gen_ai_endpoint = wrapped_method.get("endpoint")
            wrapper = wrapped_method.get("wrapper")
            wrap_function_wrapper(
                wrap_package,
                wrap_object,
                wrapper(
                    gen_ai_endpoint, version, environment, application_name, tracer
                ),
            )

    @staticmethod
    def _uninstrument(self, **kwargs):
        pass
