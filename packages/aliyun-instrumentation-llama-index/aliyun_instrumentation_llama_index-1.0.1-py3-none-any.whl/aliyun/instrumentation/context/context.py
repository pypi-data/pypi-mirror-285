from typing import Dict
from opentelemetry import context as context_api
from aliyun.semconv.trace import SpanAttributes

CUSTOMER_ATTRIBUTES = "customer_attributes"


def set_custom_user_id(user_id: str):
    assert isinstance(user_id, str), f"user_id must be str, found {type(user_id)}"
    append_custom_attributes({SpanAttributes.SERVICE_USER_ID,user_id})

def set_custom_user_name(user_name: str):
    assert isinstance(user_name, str), f"user_name must be str, found {type(user_name)}"
    append_custom_attributes({SpanAttributes.SERVICE_USER_NAME,user_name})

def set_custom_attributes(attributes: Dict[str, object]):
    assert isinstance(attributes, Dict), f"attributes must be Dict[str,object], found {type(attributes)}"
    context_api.attach(context_api.set_value(CUSTOMER_ATTRIBUTES, attributes))


def append_custom_attributes(attributes: Dict[str, object]):
    assert isinstance(attributes, Dict), f"attributes must be Dict[str,object], found {type(attributes)}"
    attrs = get_custom_attributes()
    if attrs is None:
        attrs = {}
    attrs.update(attributes)
    context_api.attach(context_api.set_value(CUSTOMER_ATTRIBUTES, attrs))


def get_custom_attributes() -> Dict[str, object]:
    attr = context_api.get_value(CUSTOMER_ATTRIBUTES)
    if isinstance(attr, Dict):
        return attr
    return None


def remove_custom_attribute(key: str):
    attr = context_api.get_value(CUSTOMER_ATTRIBUTES)
    if attr is not None:
        if isinstance(attr, Dict):
            del attr[key]


def get_custom_attribute(key: str) -> str:
    attr = context_api.get_value(CUSTOMER_ATTRIBUTES)
    if attr is not None:
        if isinstance(attr, Dict) and (key in attr):
            return attr[key]
    return None
