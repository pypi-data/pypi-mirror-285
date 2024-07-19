from aliyun.instrumentation.context.context import append_custom_attributes, get_custom_attributes, \
    get_custom_attribute, remove_custom_attribute
from aliyun.instrumentation.context import RETRIEVER_CLASS_NAME


def with_retriever_wrapper(wrapped, instance, args, kwargs):
    if instance is not None:
        append_custom_attributes({RETRIEVER_CLASS_NAME: instance.__class__.__name__})

    def wrapper(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    return wrapper(wrapped, instance, args, kwargs)


def with_call_end_wrapper(wrapped, instance, args, kwargs):
    if instance is not None:
        newkwargs = kwargs.copy()
        attr = get_custom_attribute(RETRIEVER_CLASS_NAME)
        if attr is not None:
            newkwargs.update({RETRIEVER_CLASS_NAME: attr})
            remove_custom_attribute(RETRIEVER_CLASS_NAME)

    def wrapper(wrapped, instance, args, kwargs):
        return wrapped(*args, **kwargs)

    return wrapper(wrapped, instance, args, newkwargs)
