from aliyun.instrumentation.llama_index.internal._callback import \
    AliyunTraceCallbackHandler as _AliyunTraceCallbackHandler
from opentelemetry import trace


class AliyunCallbackHandler(_AliyunTraceCallbackHandler):

    def __init__(self, tracer: trace.Tracer) -> None:
        super().__init__(tracer=tracer)
