import asyncio
from functools import partial

class MicroSignal:
    """
    Class for handling custom signals with synchronous
    and asynchronous callbacks.
    """

    def __init__(self):
        """Initialize the MicroSignal instance."""
        self._listeners = {}

    def send(self, signal_number, data=None):
        """
        Send a signal to all registered listeners.

        Args:
            signal_number (int): The signal number to send.
            data (optional): The data to send with the signal.
        """
        if signal_number in self._listeners:
            for callback in self._listeners[signal_number]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(data))
                else:
                    callback(data)

    def subscribe(self, signal_number, callback=None):
        """
        Subscribe a callback to a signal.

        This can be used both as a decorator and a method.

        Args:
            signal_number (int): The signal number to subscribe to.
            callback (optional): The callback function to register.

        Returns:
            function: The decorator function if used as a decorator.
        """
        if callback is None:
            # Used as a decorator
            def decorator(func):
                def wrapper(instance, *args, **kwargs):
                    bound_func = partial(func, instance)
                    self._register_callback(signal_number, bound_func)
                    return func
                return wrapper
            return decorator
        else:
            # Used as a method
            self._register_callback(signal_number, callback)

    def _register_callback(self, signal_number, callback):
        """
        Register a callback to a signal.

        Args:
            signal_number (int): The signal number to register the callback to.
            callback (function): The callback function to register.
        """
        if signal_number not in self._listeners:
            self._listeners[signal_number] = []
        self._listeners[signal_number].append(callback)


# Create a global instance of MicroSignal
microsignal = MicroSignal()

def subscribe(signal_number):
    """
    Decorator to subscribe a function to a signal.

    Args:
        signal_number (int): The signal number to subscribe to.

    Returns:
        function: The decorator function.
    """
    return microsignal.subscribe(signal_number)
