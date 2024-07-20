from openlit import logging
from openlit.__helpers import handle_exception
from openlit.semcov import SemanticConvetion
from opentelemetry.sdk.resources import TELEMETRY_SDK_NAME
from opentelemetry.trace import SpanKind, Status, StatusCode

# Initialize logger for logging potential issues and operations
logger = logging.getLogger(__name__)


def object_count(obj):
    """
    Counts Length of object if it exists, Else returns None
    """

    if obj:
        return len(obj)

    return None


def general_wrap(gen_ai_endpoint, version, environment, application_name, tracer):
    """
    Wraps a AstraDB operation to trace and log its execution metrics.

    This function is intended to wrap around AstraDB operations in order to
    measure their execution time, log relevant information, and trace the execution
    using OpenTelemetry. This helps in monitoring and debugging operations within
    the AstraDB space.

    Returns:
    - function: A decorator function that, when applied, wraps the target function with
                additional functionality for tracing and logging AstraDB operations.
    """

    def wrapper(wrapped, instance, args, kwargs):
        """
        Executes the wrapped AstraDB operation, adding tracing and logging.

        This inner wrapper function captures the execution of AstraDB operations,
        annotating the operation with relevant metrics and tracing information, and
        ensuring any exceptions are caught and logged appropriately.

        Parameters:
        - wrapped (Callable): The AstraDB operation to be wrapped and executed.
        - instance (object): The instance on which the operation is called (for class methods).
        - args (tuple): Positional arguments for the AstraDB operation.
        - kwargs (dict): Keyword arguments for the AstraDB operation.

        Returns:
        - Any: The result of executing the wrapped AstraDB operation.
        """

        with tracer.start_as_current_span(
            gen_ai_endpoint, kind=SpanKind.CLIENT
        ) as span:
            response = wrapped(*args, **kwargs)
            try:
                span.set_attribute(TELEMETRY_SDK_NAME, "murnitur")
                span.set_attribute(SemanticConvetion.GEN_AI_ENDPOINT, gen_ai_endpoint)
                span.set_attribute(SemanticConvetion.GEN_AI_ENVIRONMENT, environment)
                span.set_attribute(
                    SemanticConvetion.GEN_AI_APPLICATION_NAME, application_name
                )
                span.set_attribute(
                    SemanticConvetion.GEN_AI_TYPE,
                    SemanticConvetion.GEN_AI_TYPE_VECTORDB,
                )
                span.set_attribute(SemanticConvetion.DB_SYSTEM, "astradb")

                if gen_ai_endpoint == "astradb.create_collection":
                    # db_operation = SemanticConvetion.DB_OPERATION_CREATE_INDEX
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        "create_collection",
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_INDEX_NAME,
                        kwargs.get("collection_name", ""),
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_INDEX_DIMENSION,
                        kwargs.get("dimension", ""),
                    )
                elif gen_ai_endpoint == "astradb.delete_collection":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_DELETE_COLLECTION,
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_INDEX_NAME,
                        kwargs.get("collection_name", ""),
                    )

                elif gen_ai_endpoint == "astradb.insert_one":
                    span.set_attribute(SemanticConvetion.DB_OPERATION, "insert_one")

                elif gen_ai_endpoint == "astradb.insert_many":
                    span.set_attribute(SemanticConvetion.DB_OPERATION, "insert_many")

                elif gen_ai_endpoint == "astradb.delete_one":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_DELETE,
                    )
                    span.set_attribute("id", kwargs.get("id", ""))
                    span.set_attribute(
                        SemanticConvetion.DB_FILTER, str(kwargs.get("sort", ""))
                    )

                elif gen_ai_endpoint == "astradb.delete_many":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_DELETE_ALL,
                    )

                elif gen_ai_endpoint == "astradb.find":
                    span.set_attribute(SemanticConvetion.DB_OPERATION, "find")
                    span.set_attribute(
                        SemanticConvetion.DB_FILTER, str(kwargs.get("projection", ""))
                    )
                    if "limit" in kwargs.get("options", ""):
                        span.set_attribute(
                            SemanticConvetion.DB_N_RESULTS,
                            kwargs.get("options")["limit"],
                        )
                    if "$vector" in kwargs.get("sort", ""):
                        vector = kwargs.get("sort")["$vector"] or []
                        span.set_attribute(
                            SemanticConvetion.DB_VECTOR_COUNT,
                            object_count(vector),
                        )
                        span.set_attribute(SemanticConvetion.DB_STATEMENT, str(vector))

                elif gen_ai_endpoint == "astradb.update_one":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_UPDATE,
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_UPDATE_ID, str(kwargs.get("filter", ""))
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_UPDATE_VALUES,
                        str(kwargs.get("update", {})),
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_FILTER, str(kwargs.get("sort", ""))
                    )
                elif gen_ai_endpoint == "astradb.update_many":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_UPDATE,
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_UPDATE_ID, str(kwargs.get("filter", ""))
                    )
                    span.set_attribute(
                        SemanticConvetion.DB_UPDATE_VALUES,
                        str(kwargs.get("update", {})),
                    )
                    span.set_attribute("options", str(kwargs.get("options", "")))

                elif gen_ai_endpoint == "astradb.upsert_one":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_UPSERT,
                    )
                    span.set_attribute("document", str(kwargs.get("document", "")))

                elif gen_ai_endpoint == "astradb.upsert_many":
                    span.set_attribute(
                        SemanticConvetion.DB_OPERATION,
                        SemanticConvetion.DB_OPERATION_UPSERT,
                    )
                    span.set_attribute("documents", str(kwargs.get("documents", "")))
                    span.set_attribute("concurrency", kwargs.get("concurrency", 1))

                span.set_status(Status(StatusCode.OK))

                # Return original response
                return response

            except Exception as e:
                span.set_attribute(SemanticConvetion.DB_SYSTEM, "astradb")
                handle_exception(span, e)
                logger.error("Error in trace creation: %s", e)
                # Return original response
                return response

    return wrapper
