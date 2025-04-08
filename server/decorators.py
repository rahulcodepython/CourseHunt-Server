from typing import Callable, Any  # Importing necessary types for type hinting
from django.conf import settings
from .message import Message  # Importing Message for error handling


def catch_exception(func: Callable) -> Callable:
    """
    Decorator to catch exceptions in a function and handle them gracefully.
    If DEBUG is enabled in Django settings, the exception is printed to the console.
    Otherwise, an error message is returned using the Message class.

    Args:
        func (Callable): The function to be wrapped by the decorator.

    Returns:
        Callable: The wrapped function with exception handling.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function to execute the decorated function with exception handling.

        Args:
            *args (Any): Positional arguments for the decorated function.
            **kwargs (Any): Keyword arguments for the decorated function.

        Returns:
            Any: The result of the decorated function or an error message.
        """
        try:
            # Attempt to execute the decorated function
            return func(*args, **kwargs)
        except Exception as e:
            # Handle exceptions gracefully
            # Convert exception to string for readability
            error_message: str = str(e)
            if settings.DEBUG:
                # Print the error message to the console in DEBUG mode
                print(error_message)
            # Return an error message using the Message class
            return Message.error(error_message)

    return wrapper
