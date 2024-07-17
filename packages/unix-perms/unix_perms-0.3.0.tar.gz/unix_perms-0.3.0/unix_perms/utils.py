import inspect
from typing import Any, List, Type


def get_all_class_parameters(class_object: Type[Any]) -> List[str]:
    """
    Retrieves all parameters for a class object.

    Args:
        class_object (Type[Any]): Any class object.

    Returns:
        List[str]: A list of string class parameter names.
    """
    return [
        param for param in inspect.signature(class_object).parameters if param != 'self'
    ]
