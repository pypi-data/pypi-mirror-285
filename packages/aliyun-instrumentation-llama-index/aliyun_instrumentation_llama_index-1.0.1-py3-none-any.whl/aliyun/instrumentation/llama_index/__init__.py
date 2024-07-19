from typing import Any, Collection

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor  # type: ignore
from opentelemetry import trace as trace_api
import llama_index.core
from aliyun.instrumentation.llama_index.package import _instruments
from wrapt import wrap_function_wrapper
from aliyun.instrumentation.llama_index._wrapper import with_retriever_wrapper,with_call_end_wrapper


class AliyunLlamaIndexInstrumentor(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs: Any) -> None:
        if not (tracer_provider := kwargs.get("tracer_provider")):
            tracer_provider = trace_api.get_tracer_provider()
        tracer = trace_api.get_tracer(__name__, tracer_provider=tracer_provider)
        from aliyun.instrumentation.llama_index._callback import (
            AliyunCallbackHandler,
        )
        import llama_index.core
        wrap_function_wrapper(
            "llama_index.core.base.base_retriever",
            "BaseRetriever.aretrieve",
            wrapper=with_retriever_wrapper,
        )
        wrap_function_wrapper(
            "llama_index.core.base.base_retriever",
            "BaseRetriever.retrieve",
            wrapper=with_retriever_wrapper,
        )
        wrap_function_wrapper(
            "llama_index.core.callbacks.base",
            "EventContext.on_start",
            wrapper=with_call_end_wrapper
        )
        self._original_global_handler = llama_index.core.global_handler
        llama_index.core.global_handler = AliyunCallbackHandler(tracer=tracer)


    def _uninstrument(self, **kwargs: Any) -> None:
        import llama_index.core
        llama_index.core.global_handler = self._original_global_handler
        self._original_global_handler = None
